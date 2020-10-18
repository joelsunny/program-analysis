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

def instruction_gen_kill(instr):
    """
    generate the GEN, KILL sets of a single instruction
    """
    KILL = set()
    GEN = set()

    stmt_type = instr["_type"]
    if stmt_type == "Assign":
        # Assign(expr* targets, expr value, string? type_comment)
        lhs = get_targets(instr["targets"])
        rhs = get_uses(instr["value"])
        for v in lhs:
            if v not in rhs:
                GEN.add(v)
    elif stmt_type == "AugAssign":
        # AugAssign(expr target, operator op, expr value)
        # GEN = {instr["target"]["id"]}.union(get_uses(instr["value"]))
        pass
    else:
        KILL = get_uses(instr)
    
    return GEN, KILL

def basic_block_gen_kill(block):
    """
    generate the GEN, KILL sets of a single basic block
    """
    GEN = set()
    KILL = set()

    for node in block.ast_nodes:
        gen, kill = instruction_gen_kill(node)
        GEN = GEN.union(gen.difference(KILL)) # a = b + a, is a use for a. so gen first, then kill
        KILL = KILL.union(kill)

    return GEN, KILL

def get_gen_kill_sets(blocks, cfg):
    """
    generate the GEN, KILL sets of all basic blocks in the control flow graph
    """
    GEN = []
    KILL = []

    for b in blocks:
       block = cfg.blocks[b]
       gen, kill = basic_block_gen_kill(block)
       GEN.append(gen)
       KILL.append(kill) 
    return GEN, KILL

def init_block(block, U):
    block.faintgen = [set()]*len(block.ast_nodes)
    block.faintkill = [set()]*len(block.ast_nodes)
    block.faintout = [U]*len(block.ast_nodes)
    block.faintin = [set()]*len(block.ast_nodes)

def get_block_gen_kill(block):
    KILL = set()
    GEN = set()

    for gen in block.faintgen:
        GEN = GEN.union(gen)
    
    for kill in block.faintkill:
        KILL = KILL.union(kill)
    
    return GEN.difference(KILL), KILL

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
            if 'x' in ts:
                print(f"source = {block.source[idx]}, out = {block.faintout[idx]}, kill = {block.faintkill[idx] }")
        elif stmt_type == "AugAssign":
            pass
        else:
            block.faintgen[idx] = set()
            block.faintkill[idx] = get_uses(stmt)
        
        
        # print(f"block {block.id}: {block.source[idx]} : in = ({block.faintgen[idx]} - {block.faintkill[idx]}) U ({block.faintout[idx]} - {block.faintkill[idx]})")
        block.faintin[idx] = (block.faintgen[idx].difference(block.faintkill[idx])).union(block.faintout[idx].difference(block.faintkill[idx]))
        # print(f"block {block.id}: {block.source[idx]} : in = ({block.faintgen[idx]} - {block.faintkill[idx]}) U ({block.faintout[idx]} - {block.faintkill[idx]}) = { block.faintin[idx]}")

def intrablock_fv(block, block_out, block_in):
    for i, stmt in enumerate(block.ast_nodes):
        stmt_type = stmt["_type"]
        if stmt_type == "Assign":
            ts = get_targets(stmt["targets"])
            block.faintgen[i] = get_targets(stmt["targets"])
            # block.faintgen[i] = get_targets(stmt["targets"]).difference(get_uses(stmt))
            if list(ts)[0] == "x" and block.id == 3:
                # print("uses")
                # print(get_uses(stmt))
                # print(block.faintout[i])
                pass
            block.faintkill[i] = get_uses(stmt) if list(get_targets(stmt["targets"]))[0] not in block.faintout[i] else set()
            # print(block.faintkill[i])
        elif stmt_type == "AugAssign":
            pass
        else:
            block.faintkill[i] = get_uses(stmt)
        
        # note: kill and gen are interchanged for fv analysis
        # in = out - gen - kill
        # block.faintin[i] = block.faintout[i].difference(block.faintgen[i]).difference(block.faintkill[i])
        # block.faintin[i] = block.faintout[i].union(block.faintgen[i]).difference(block.faintkill[i])

        block.faintout[i] = block_out if i == len(block.ast_nodes)-1 else block.faintin[i+1]
        block.faintin[i] = (block.faintgen[i].difference(block.faintkill[i])).union(block.faintout[i].difference(block.faintkill[i]))
        # block.faintin[i] = block.faintout[i-1] if i != 0 else block_in 
        # block.faintin[i] = block.faintgen[i].union(block.faintout[i].difference(block.faintkill[i]))
        # block.faintout[i] = block_out if i == len(block.ast_nodes)-1 else block.faintin[i+1]

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
    print(blocks)
    successors = get_successor_info(cfg)
    U = get_all_targets(cfg)
    pprint(U)
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
    k = 0
    while k < 10:
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
            print("amzing")
            # exit(0)
        # print(f"flag = {flag}")
        prev_in = [i for i in IN]
        k+=1

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
            if stmt_type == "Assign" or stmt_type == "AugAssign":
                if list(get_targets(block.ast_nodes[i]["targets"]))[0] in block.faintout[i]:
                    faint.add((block.id, i))
                    faint_source.append(stmt)
    return faint, faint_source

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    # read inputs to the script
    ast_file = sys.argv[1]
    # load AST json
    ast = json.loads(open(ast_file).read())
    for node in ast["body"]:
        print(asttostr.ast_to_str(node))

    exit(2)
    # initialise CFG object
    # cfg = CFG()
    # # construct control flow graph from ast
    # cfg.from_ast(ast)
    # s = cfg.cfg_to_code()
    # print(s)
    # liveness analysis
    # augment_blocks(cfg)
    # # render cfg as image
    # outfile = os.path.basename(ast_file)
    # outfile = outfile.split(".")[:-1]
    # outfile = "".join(outfile)
    # render_graph(cfg, outfile=outfile)
    # faintvariable(cfg)
    # faint, faint_source = get_faintvariables(cfg)
    # print(faint, faint_source)
    # for node in ast["body"]:
    #     print(asttostr.ast_to_str2(node, block=1, idx=0 faint=faint))