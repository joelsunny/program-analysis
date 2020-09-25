import os
import sys
import json
import asttostr
from collections import deque
from graphviz import Digraph

"""
The script will contain only assignment statements, if-then, if-then-else, while loops and function calls. 
The nodes of the CFG will be basic blocks containing a sequence of assignment statements, branch statements and function calls. 
The conditions for if-then, if-then-else and while statements will be a single variable.
"""
def usage():
    help = f"""
    Usage:

    python 1-assignment.py <pyhton source file> <option>
    options:
        assign - print assignment stmts
        branch - print branch conditions"""
    print(help)
    exit()

BLOCK_COUNT = 0
class BasicBlock:
    def __init__(self):
        global BLOCK_COUNT
        self.id = BLOCK_COUNT
        BLOCK_COUNT += 1
        self.source = []
        self.neighbours = []

    def add_instruction(self, instr):
        self.source.append(instr)

    def add_successor(self, block):
        self.neighbours.append(block)

    def __repr__(self):
        block_contents = "\n".join(self.source)
        block_contents = f"""b{self.id}:
{block_contents}\n"""
        return block_contents

class CFG:
    def __init__(self):
        self.root = BasicBlock()
        self.adjacency_list = {self.root.id:[]}
        self.blocks = {self.root.id: self.root}

    def add_node(self, block):
        if block.id in self.blocks:
            return
        self.blocks[block.id] = block
        self.adjacency_list[block.id] = []

    def add_edge(self, b1, b2):
        self.add_node(b2)
        self.adjacency_list[b1.id].append(b2.id)
        b1.add_successor(b2)

    def generate_dot(self):
        # render to dot file format
        dot = Digraph(comment='CFG', format='svg')

        for block in self.blocks:
            dot.node(str(block), str(self.blocks[block]) )
        
        for block in self.adjacency_list:
            for neighbour in self.adjacency_list[block]:
                dot.edge(str(block), str(neighbour))
    
        return dot
    
    def construct_from_ast(self, ast, entry=None):
        if entry == None:
            curr_block = self.root
        else:
            curr_block = entry

        for stmt in ast:
            stmt_type = stmt["_type"]

            print(f"stmt type : {stmt_type}")
            if stmt_type not in BRANCH:
                curr_block.add_instruction(asttostr.ast_to_str(stmt))
            else:
                if len(curr_block.source) != 0:
                    t_block = BasicBlock()
                    self.add_edge(curr_block, t_block)
                    curr_block = t_block
                if stmt_type == "If":
                    # If(expr test, stmt* body, stmt* orelse)
                    t = asttostr.ast_to_str(stmt["test"])
                    instr = f"branch[{t}]"
                    curr_block.add_instruction(instr)
                    if_block = curr_block

                    body = BasicBlock()
                    self.add_edge(curr_block, body)
                    body = self.construct_from_ast(stmt["body"], body)
                    
                    if len(stmt["orelse"]) != 0:
                        orelse = BasicBlock()
                        self.add_edge(curr_block, orelse)
                        orelse = self.construct_from_ast(stmt["orelse"], orelse)

                    # create a new block and set it to current
                    t_block = BasicBlock()
                    self.add_edge(body, t_block)
                    if len(stmt["orelse"]) != 0:
                        self.add_edge(orelse, t_block)
                    else:
                        self.add_edge(if_block, t_block)
                    curr_block = t_block

                elif stmt_type == "While":
                    while_block = curr_block
                    # While(expr test, stmt* body, stmt* orelse)
                    t = asttostr.ast_to_str(stmt["test"])
                    instr = f"while[{t}]"
                    curr_block.add_instruction(instr)
                    body = BasicBlock()
                    self.add_edge(curr_block, body)
                    body = self.construct_from_ast(stmt["body"], body)
                    self.add_edge(body, curr_block)
                    if len(stmt["orelse"]) != 0:
                        orelse = BasicBlock()
                        self.add_edge(curr_block, orelse)
                        self.construct_from_ast(stmt["orelse"], orelse)
                        curr_block = orelse
                    
                    # create a new basic block and set it to current
                    t_block = BasicBlock()
                    self.add_edge(while_block, t_block)
                    curr_block = t_block
                else:
                    print(f"Unimplemented: {stmt_type}")
        
        return curr_block

    def __repr__(self):
        graph = ""
        visited = set()
        q = deque([self.root])
        while len(q) != 0:
            node = q.popleft()
            graph += f"{node}"
            for succ in node.neighbours:
                if succ.id not in visited:
                    q.append(succ)
                    visited.add(succ.id)
        return graph

BLOCK_LEADERS = {"If", "While"}
BRANCH = {"If", "While"}
               
def render_graph(cfg, outfile):
    """
    function to render the control flow graph in graphviz.
    """
    dot = cfg.generate_dot()
    dot.render(f'temp/{outfile}.gv', view=True)

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
    cfg.construct_from_ast(ast["body"])
    print(cfg)
    # render cfg as image
    outfile = os.path.basename(ast_file)
    outfile = outfile.split(".")[:-1]
    outfile = "".join(outfile)
    render_graph(cfg, outfile=outfile)