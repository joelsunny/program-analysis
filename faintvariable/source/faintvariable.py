import os
import sys
import json
import asttostr
from pprint import pprint
from asttocfg import CFG
import graphviz
from graphviz import Digraph
     
def get_block_ordering(cfg):
    post_order = []
    visited = set()

    def dfs_order(node):
        visited.add(node.id)
        # print(node.id)
        for pred in node.neighbours:
            if pred.id not in visited:
                dfs_order(pred)
        if not node.is_special and not node.is_dummy:
            post_order.append(node.id)

    dfs_order(cfg.root)
    # print("\n".join([str(i) for i in post_order]))
    return post_order

def get_successor_info(cfg):
    succ_map = {}
    def succ(block):
        res = set()
        
        for n in block.neighbours:
            if n.is_dummy:
                # print(f"dummy block: {n.id}")
                res = res.union(succ(n))
            elif not n.is_special:
                res.add(n.id)
        return res
    
    for b in cfg.blocks:
        block = cfg.blocks[b]
        if not block.is_dummy and not block.is_special:
            # print(f"processing block : {block.id}")
            succ_map[block.id] = succ(block)
    
    # pprint(succ_map, indent=4)
    return succ_map

def get_targets(targets):
    t = set()
    for node in targets:
        t.add(node["id"])
    return t

def get_uses(node, key=None):
    uses = set()
    if key == "func":
        return uses
    if node["_type"] == "Name":
        if node["ctx"]["_type"] == "Load":
            uses.add(node["id"])
            return uses
            
    for key in node:
        if isinstance(node[key], dict):
            uses = uses.union(get_uses(node[key], key=key))
        elif isinstance(node[key], list):
            for n in node[key]:
                uses = uses.union(get_uses(n))
    return uses

def init_block(block, U):
    block.faintgen = [set()]*len(block.ast_nodes)
    block.faintkill = [set()]*len(block.ast_nodes)
    block.faintout = [U]*len(block.ast_nodes)
    block.faintin = [set()]*len(block.ast_nodes)

def get_call_arguments(node, key=None): 
    uses = set()
    if key == "func":
        return uses
    if node["_type"] == "Call":
        for arg in node["args"]:
            uses = uses.union(get_uses(arg))
        return uses
            
    for key in node:
        if isinstance(node[key], dict):
            uses = uses.union(get_call_arguments(node[key], key=key))
        elif isinstance(node[key], list):
            for n in node[key]:
                uses = uses.union(get_call_arguments(n))
    return uses

def intrablock_fv2(block, block_out, block_in):
    for i in range(len(block.ast_nodes)):
        idx = len(block.ast_nodes)-1 -i
        stmt = block.ast_nodes[idx]
        stmt_type = stmt["_type"]
        block.faintout[idx] = block_out if idx == len(block.ast_nodes)-1 else block.faintin[idx+1]
        
        if stmt_type == "Assign":
            ts = get_targets(stmt["targets"])
            block.faintgen[idx] = get_targets(stmt["targets"])
            # block.faintgen[idx] = get_targets(stmt["targets"]).difference(get_uses(stmt))
            
            block.faintkill[idx] = get_uses(stmt) if list(get_targets(stmt["targets"]))[0] not in block.faintout[idx] else set()
            args = get_call_arguments(stmt)
            if len(args) > 0:
                block.faintkill[idx] = block.faintkill[idx].union(args)
                block.faintout[idx] = block.faintout[idx].difference(ts)
            if 'x' in ts:
                print(f"source = {block.source[idx]}, out = {block.faintout[idx]}, kill = {block.faintkill[idx]}, uses = {get_uses(stmt)}")
                print(f"args = {args}")
        elif stmt_type == "AugAssign":
            pass
        else:
            block.faintgen[idx] = set()
            block.faintkill[idx] = get_uses(stmt)
        
        
        # print(f"block {block.id}: {block.source[idx]} : in = ({block.faintgen[idx]} - {block.faintkill[idx]}) U ({block.faintout[idx]} - {block.faintkill[idx]})")
        block.faintin[idx] = (block.faintgen[idx].difference(block.faintkill[idx])).union(block.faintout[idx].difference(block.faintkill[idx]))
        # print(f"block {block.id}: {block.source[idx]} : in = ({block.faintgen[idx]} - {block.faintkill[idx]}) U ({block.faintout[idx]} - {block.faintkill[idx]}) = { block.faintin[idx]}")

def get_all_targets(cfg):
    res = set()
    for b in cfg.blocks:
        block = cfg.blocks[b]
        for stmt in block.ast_nodes:
            if stmt["_type"] == "Assign":
                res = res.union(get_targets(stmt["targets"]))
    return res

def faintvariable(cfg):
    blocks = get_block_ordering(cfg)
    # print(blocks)
    successors = get_successor_info(cfg)
    U = get_all_targets(cfg)
    # pprint(U)
    IN = [U]*len(blocks)
    OUT = [U]*len(blocks)
    OUT[0] = U
    block_order = {}
    for i, block in enumerate(blocks):
        block_order[block] = i

    # initialise blocks for fv
    for block in blocks:
        init_block(cfg.blocks[block], U)

    flag = False 
    prev_in = [i for i in IN]
    # k = 0
    while not flag:
        for i, block in enumerate(blocks):
            # intra block calculation
            # if block == 2:
            #     print(f"calling intrablock({block}, {OUT[i]}, {1})")
            # intrablock_fv(cfg.blocks[block], OUT[i], IN[i]) # TODO
            # IN[i] = cfg.blocks[block].faintin[0]

            OUT[i] = U
            for s in successors[block]:
                # calculate OUT of block
                OUT[i] = OUT[i].intersection(IN[block_order[s]])
            # print(f"out[{block}] = { ' int '.join([ str(IN[block_order[s]]) for s in successors[block] ]) } = {OUT[i]}")
            # print(f"in{[block]} = {IN[i]}")
            intrablock_fv2(cfg.blocks[block], OUT[i], IN[i])
            IN[i] = cfg.blocks[block].faintin[0]
        if prev_in == IN:
            flag = True
            # print("amzing")
            # exit(0)
        # print(f"flag = {flag}")
        prev_in = [i for i in IN]
        # k+=1

    return IN, OUT, blocks

def render_graph(cfg, outfile):
    """
    function to render the control flow graph in graphviz.
    """
    dot = cfg.generate_dot()
    try:
        dot.render(f'temp/{outfile}.gv', view=True)
    except graphviz.ExecutableNotFound:
        print("ERROR: graphviz.ExecutableNotFound. Install graphviz tool.")
        exit(1)
    except RuntimeError:
        print("WARN: image viewer opening is requested but not supported. Output image file is placed under temp folder")

def augment_blocks(cfg):
    IN, OUT, blocks = faintvariable(cfg)
    for i,block in enumerate(blocks):
        cfg.blocks[block].IN = IN[i]
        cfg.blocks[block].OUT = OUT[i]

def get_faintvariables(cfg):
    faint = set()
    faint_source = []
    for b in cfg.blocks:
        block = cfg.blocks[b]
        if block.is_dummy or block.is_special:
            continue
        for i, stmt in enumerate(block.source):
            stmt_type = block.ast_nodes[i]["_type"]
            if stmt_type == "Assign":
                if list(get_targets(block.ast_nodes[i]["targets"]))[0] in block.faintout[i]:
                    faint.add(block.ast_nodes[i]["instr_id"])
                    faint_source.append(stmt)
            elif stmt_type == "AugAssign":
                if block.ast_nodes[i]["target"]["id"] in block.faintout[i]:
                    faint.add(block.ast_nodes[i]["instr_id"])
                    faint_source.append(stmt)
    return faint, faint_source

def remove_faint(cfg, faint, outfile):
    """
    preoreder traversal, delete fain Assign/AugAssign nodes
    """
    def mark_node(node, faint):
        if not isinstance(node, dict):
            return idx
        if node["_type"] == "Assign" or node["_type"] == "AugAssign":
            idx = node["instr_id"]
            if idx in faint:
                node["is_faint"] = True
        else: 
            node["is_faint"] = False
            
        for key in node:
            if isinstance(node[key], dict):
                idx = mark_node(node[key], faint)
            elif isinstance(node[key], list):
                for n in node[key]:
                    idx = mark_node(n, faint)

    for stmt in cfg.augmented_ast["body"]:
        mark_node(stmt, faint)
    
    source = ""
    for node in cfg.augmented_ast["body"]:
        t = asttostr.ast_to_str(node)
        if t != "":
            source += "\n" + asttostr.ast_to_str(node)
    print(source)
    with open(f'temp/{outfile}_optimized.py', 'w') as f: 
        f.write(source)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    # read inputs to the script
    ast_file = sys.argv[1]
    # load AST json
    ast = json.loads(open(ast_file).read())
    # initialise CFG object
    cfg = CFG()
    # # construct control flow graph from ast
    cfg.from_ast(ast)
    augment_blocks(cfg)
    # # render cfg as image
    outfile = os.path.basename(ast_file)
    outfile = outfile.split(".")[:-1]
    outfile = "".join(outfile)
    # render_graph(cfg, outfile=outfile)
    faintvariable(cfg)
    faint, faint_source = get_faintvariables(cfg)
    print(faint_source)
    remove_faint(cfg, faint, outfile)