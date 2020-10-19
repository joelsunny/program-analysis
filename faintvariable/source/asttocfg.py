import os
import sys
import json
import asttostr
from pprint import pprint 
from collections import deque
import graphviz
from graphviz import Digraph

def usage():
    help = f"""
    Usage:

    python 1-assignment.py <pyhton source file> <option>
    options:
        assign - print assignment stmts
        branch - print branch conditions"""
    print(help)
    exit()

BLOCK_LEADERS = {"If", "While"}
BLOCK_COUNT = 0
INSTR_COUNT = 0

class BasicBlock:
    """
    data structure for representing a basic block
    """
    def __init__(self, is_special=False):
        """
        constructor.
        @param is_special: True for special blocks - ENTRY, EXIT
        """
        global BLOCK_COUNT
        self.id = BLOCK_COUNT
        BLOCK_COUNT += 1
        self.source = []
        self.valuenumbers = []
        self.ast_nodes = []
        self.predecessors = []
        self.neighbours = []
        self.is_special = is_special
        self.is_dummy = False
        self.has_branched = False
        self.IN = None 
        self.OUT = None
        self.faintgen = []
        self.faintkill = []
        self.faintout = []
        self.faintin = []

    def add_instruction(self, instr):
        """
        add a new instruction to the basic block
        """
        self.source.append(instr)
        # if instr["_type"] == "Assign" or instr["_type"] == "AugAssign":
        #     INSTR_COUNT += 1
        #     self.valuenumbers.append[INSTR_COUNT]
        # else: 
        #     self.valuenumbers.append(-1)
    def add_neighbour(self, block):
        """
        add a neighbour to the block
        """
        self.neighbours.append(block)
        block.predecessors.append(self)

    def remove_neighbour(self, block):
        """
        delete a neighbour
        """
        def _find_index(neighbours):
            for i, node in enumerate(neighbours):
                if node.id == block:
                    return i
        idx = _find_index(self.neighbours)
        if idx == 0:
            self.neighbours = self.neighbours[1:]
        else:
            self.neighbours = self.neighbours[0:idx] + self.neighbours[idx+1:]

    def to_code(self, indentation=0):
        prefix = "\t"*indentation
        source = ""
        last = None
        next_indent = 0
        for i,node in enumerate(self.ast_nodes):
            source += prefix + asttostr.ast_to_str(node) + "\n"
            last = node
        if last != None:
            print(f"last = {last['_type']}")
        if last == None:
            next_indent = 0
        elif last["_type"] == "Compare":
            next_indent = 1
        else: 
            next_indent = -1
        return source, next_indent

    def __repr__(self):
        # TODO: remove this
        # return json.dumps(self.ast_nodes, indent=4)
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

        block_contents = ""
        if not self.is_special:
            block_contents=f"block {self.id}:\n"
        # block_source = "\n".join(self.source)
        block_contents += f"\nIN = {self.IN}\n"
        block_source = "\n".join([f"{self.ast_nodes[i]['instr_id']}: " + self.source[i] + ": " + f"gen = {self.faintgen[i]}, kill = {self.faintkill[i]}, out = {self.faintout[i]}, in = {self.faintin[i]} " for i in range(len(self.ast_nodes))]) 
        block_contents += f"{block_source}"
        GEN, KILL = basic_block_gen_kill(self)

        block_contents += f"\nGEN: {GEN},  KILL: {KILL} \nOUT = {self.OUT}"
        return block_contents

class CFG:
    def __init__(self):
        self.root = BasicBlock(is_special=True)
        self.adjacency_list = {self.root.id:[]}
        self.blocks = {self.root.id: self.root}
        self.root.add_instruction("ENTRY")
        t_block = BasicBlock()
        self.add_edge(self.root, t_block)
        self.root = t_block
        self.exit_block = None
        self.augmented_ast = None

    def add_node(self, block):
        """
        add a node to the graph
        """
        if block.id in self.blocks:
            return
        self.blocks[block.id] = block
        self.adjacency_list[block.id] = []

    def remove_node(self, block):
        """
        remove node from graph
        """
        self.blocks.pop(block.id)
        self.adjacency_list.pop(block.id)
        for p in block.predecessors:
            self.remove_edge(p, block)
            p.remove_neighbour(block.id)
        global BLOCK_COUNT
        BLOCK_COUNT -= 1

    def add_edge(self, b1, b2):
        """
        add an edge between two blocks
        """
        self.add_node(b2)
        self.adjacency_list[b1.id].append(b2.id)
        b1.add_neighbour(b2)

    def remove_edge(self, b1, b2):
        """
        remove the edge between two blocks
        """
        def _find_index(neighbours):
            for i, node in enumerate(neighbours):
                if node == b2.id:
                    return i
        idx = _find_index(self.adjacency_list[b1.id])
        if idx == 0:
            self.adjacency_list[b1.id] = self.adjacency_list[b1.id][1:]
        else:
            self.adjacency_list[b1.id] = self.adjacency_list[b1.id][0:idx] + self.adjacency_list[b1.id][idx+1:]

    def generate_dot(self):
        """
        function to generate the dotfile for rendering
        """
        dot = Digraph(comment='CFG', format='svg')

        for block in self.blocks:
            if self.blocks[block].is_special:
                # check to see if the nodes are ENTRY or EXIT blocks
                dot.attr('node', shape='diamond', style='filled', color='#97fcb2')
            elif self.blocks[block].is_dummy:
                # mark dummy nodes
                dot.attr('node', shape='ellipse', style='filled', color='#ffb1a3')
            dot.node(str(block), str(self.blocks[block]) )
            dot.attr('node', shape='ellipse', style='filled', color='#f2e996')
        
        for block in self.adjacency_list:
            visited_neighbours = set()
            for neighbour in self.adjacency_list[block]:
                if neighbour not in visited_neighbours:
                    dot.edge(str(block), str(neighbour))
                visited_neighbours.add(neighbour)
    
        return dot

    def augment_ast(self, ast):
        idx = 0
        def augment_node(node, idx):
            if not isinstance(node, dict):
                return idx
            if node["_type"] == "Assign" or node["_type"] == "AugAssign":
                node["instr_id"] = idx
                idx+=1
                return idx
            else: 
                node["instr_id"] = -1

            for key in node:
                if isinstance(node[key], dict):
                    idx = augment_node(node[key], idx)
                elif isinstance(node[key], list):
                    for n in node[key]:
                        idx = augment_node(n, idx)
            return idx

        for stmt in ast["body"]:
            idx = augment_node(stmt, idx)
        return ast

    def from_ast(self, ast):
        """
        function to generate CFG from the AST
        """
        ast = self.augment_ast(ast)
        self.augmented_ast = ast 
        # pprint(ast)
        exit_block = self.construct_from_ast(ast["body"])
        if len(exit_block.source) == 0:
            exit_block.add_instruction("EXIT")
            exit_block.is_special = True
            self.exit_block = exit_block
        else: 
            t_block = BasicBlock(is_special=True)
            t_block.add_instruction("EXIT")
            self.exit_block = t_block
            self.add_edge(exit_block, t_block)
        
        # do a second pass to mark the blocks
        for block in self.blocks:
            block = self.blocks[block]
            if len(block.source) == 0:
                block.is_dummy = True

    def faintvariable_opt(self, ast, entry=None):
        """
        Do a pre-order traversal of the AST to generate the control flow graph.
        The algorithm adds the source instructions to the current basic block
        until a branch leader is encountered.
        """
        if entry == None:
            curr_block = self.root
        else:
            curr_block = entry

        for stmt in ast:
            stmt_type = stmt["_type"]

            # if stmt is not a block leader, add it to the current block
            if stmt_type not in BLOCK_LEADERS:
                curr_block.add_instruction(asttostr.ast_to_str(stmt))
                curr_block.ast_nodes.append(stmt)
            else:
                if curr_block.has_branched:
                    t_block = BasicBlock()
                    self.add_edge(curr_block, t_block)
                    curr_block = t_block
                if stmt_type == "If":
                    # If(expr test, stmt* body, stmt* orelse)
                    t = asttostr.ast_to_str(stmt["test"])
                    instr = f"branch[{t}]"
                    curr_block.add_instruction(instr)
                    curr_block.ast_nodes.append(stmt["test"])
                    curr_block.has_branched = True
                    if_block = curr_block

                    # if body processing
                    body = BasicBlock()
                    self.add_edge(curr_block, body)
                    body = self.construct_from_ast(stmt["body"], body)
                    
                    # orelse node processing
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
                    # While(expr test, stmt* body, stmt* orelse)
                    if len(curr_block.source) != 0:
                        t_block = BasicBlock()
                        self.add_edge(curr_block, t_block)
                        curr_block = t_block
                    while_block = curr_block
                    t = asttostr.ast_to_str(stmt["test"])
                    curr_block.ast_nodes.append(stmt["test"])
                    instr = f"while[{t}]"
                    curr_block.add_instruction(instr)
                    curr_block.has_branched = True

                    # while body processing
                    body = BasicBlock()
                    self.add_edge(curr_block, body)
                    body = self.construct_from_ast(stmt["body"], body)
                    # add back edge from body of while to the branch condition
                    self.add_edge(body, while_block)
                    # check if the returned block is a dummy node
                    # self.add_edge(body, curr_block)
                    if len(body.source) == 0:
                        if len(body.predecessors) > 1:
                            self.add_edge(body, curr_block)
                        elif len(body.predecessors) == 1:
                            self.add_edge(body.predecessors[0], curr_block)
                            self.remove_node(body)
                        else: 
                            self.add_edge(body, curr_block)
                    
                    # orelse node processing
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


    def construct_from_ast(self, ast, entry=None):
        """
        Do a pre-order traversal of the AST to generate the control flow graph.
        The algorithm adds the source instructions to the current basic block
        until a branch leader is encountered.
        """
        if entry == None:
            curr_block = self.root
        else:
            curr_block = entry

        for stmt in ast:
            stmt_type = stmt["_type"]

            # if stmt is not a block leader, add it to the current block
            if stmt_type not in BLOCK_LEADERS:
                curr_block.add_instruction(asttostr.ast_to_str(stmt))
                curr_block.ast_nodes.append(stmt)
            else:
                if curr_block.has_branched:
                    t_block = BasicBlock()
                    self.add_edge(curr_block, t_block)
                    curr_block = t_block
                if stmt_type == "If":
                    # If(expr test, stmt* body, stmt* orelse)
                    t = asttostr.ast_to_str(stmt["test"])
                    instr = f"branch[{t}]"
                    curr_block.add_instruction(instr)
                    curr_block.ast_nodes.append(stmt["test"])
                    curr_block.has_branched = True
                    if_block = curr_block

                    # if body processing
                    body = BasicBlock()
                    self.add_edge(curr_block, body)
                    body = self.construct_from_ast(stmt["body"], body)
                    
                    # orelse node processing
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
                    # While(expr test, stmt* body, stmt* orelse)
                    if len(curr_block.source) != 0:
                        t_block = BasicBlock()
                        self.add_edge(curr_block, t_block)
                        curr_block = t_block
                    while_block = curr_block
                    t = asttostr.ast_to_str(stmt["test"])
                    curr_block.ast_nodes.append(stmt["test"])
                    instr = f"while[{t}]"
                    curr_block.add_instruction(instr)
                    curr_block.has_branched = True

                    # while body processing
                    body = BasicBlock()
                    self.add_edge(curr_block, body)
                    body = self.construct_from_ast(stmt["body"], body)
                    # add back edge from body of while to the branch condition
                    self.add_edge(body, while_block)
                    # check if the returned block is a dummy node
                    # self.add_edge(body, curr_block)
                    if len(body.source) == 0:
                        if len(body.predecessors) > 1:
                            self.add_edge(body, curr_block)
                        elif len(body.predecessors) == 1:
                            self.add_edge(body.predecessors[0], curr_block)
                            self.remove_node(body)
                        else: 
                            self.add_edge(body, curr_block)
                    
                    # orelse node processing
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

    def cfg_to_code(self):
        prefix = 0
        source = ""
        for b in self.blocks:
            block = self.blocks[b]
            s, n = block.to_code(prefix)
            source += s
            prefix += n
            print(f"n = {n}, prefix = {prefix}")
        return source

    def __repr__(self):
        graph = ""
        visited = set()
        q = deque([self.root])
        while len(q) != 0:
            node = q.popleft()
            graph += f"{node}\n"
            for succ in node.neighbours:
                if succ.id not in visited:
                    q.append(succ)
                    visited.add(succ.id)
        return graph
               
def render_graph(cfg, outfile):
    """
    function to render the control flow graph in graphviz.
    """
    dot = cfg.generate_dot()
    try:
        dot.render(f'temp/{outfile}.gv', view=False, quiet=True, quiet_view=True)
    except graphviz.ExecutableNotFound:
        print("ERROR: graphviz.ExecutableNotFound. Install graphviz tool.")
        exit(1)
    except RuntimeError:
        print("WARN: image viewer opening is requested but not supported. Output image file is placed under temp folder")

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
    # render cfg as image
    outfile = os.path.basename(ast_file)
    outfile = outfile.split(".")[:-1]
    outfile = "".join(outfile)
    render_graph(cfg, outfile=outfile)
