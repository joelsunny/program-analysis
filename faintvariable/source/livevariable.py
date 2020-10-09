import os
import sys
import json
import asttostr
from pprint import pprint
from asttocfg import CFG
import graphviz
from graphviz import Digraph
     
def faintvariable_analysis(cfg):
    pass 

def remove_faint_variables(cfg, faint_variables):
    pass

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
        KILL = get_targets(instr["targets"])
        GEN = get_uses(instr["value"])
    elif stmt_type == "AugAssign":
        # AugAssign(expr target, operator op, expr value)
        GEN = {instr["target"]["id"]}.union(get_uses(instr["value"]))
    # elif stmt_type == "If":
    #     # If(expr test, stmt* body, stmt* orelse)
    #     pass
    # elif stmt_type == "While":
    #     # While(expr test, stmt* body, stmt* orelse)
    #     pass
    else:
        GEN = get_uses(instr)
    
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

def liveness_analysis(cfg):
    blocks = get_block_ordering(cfg)
    successors = get_successor_info(cfg)
    pprint(successors, indent=4)
    IN = [set()]*len(blocks)
    OUT = [set()]*len(blocks)
    GEN, KILL = get_gen_kill_sets(blocks, cfg)

    block_order = {}
    for i, block in enumerate(blocks):
        block_order[block] = i

    flag = False 
    prev_in = [i for i in IN]
    # prev_out = OUT
    while not flag:
        for i,block in enumerate(blocks):
            # OUT[i] = pass 
            for s in successors[block]:
                if block == 3:
                    print(f"{s}: {IN[block_order[s]] }")
                    print(block_order)
                    print(IN)
                OUT[i] = OUT[i].union(IN[block_order[s]])

            IN[i] = GEN[i].union(OUT[i].difference(KILL[i]))
        if prev_in == IN:
            flag = True
        prev_in = [i for i in IN]
        # prev_out = OUT
    
    return IN, OUT, blocks

def augment_blocks(cfg):
    IN, OUT, blocks = liveness_analysis(cfg)
    for i,block in enumerate(blocks):
        cfg.blocks[block].IN = IN[i]
        cfg.blocks[block].OUT = OUT[i]

    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    # read inputs to the script
    ast_file = sys.argv[1]
    # load AST json
    ast = json.loads(open(ast_file).read())

    # initialise CFG object
    cfg = CFG()
    # construct control flow graph from ast
    cfg.from_ast(ast)
    # liveness analysis
    augment_blocks(cfg)
    # render cfg as image
    outfile = os.path.basename(ast_file)
    outfile = outfile.split(".")[:-1]
    outfile = "".join(outfile)
    render_graph(cfg, outfile=outfile)