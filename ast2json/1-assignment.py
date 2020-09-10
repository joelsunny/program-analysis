"""
Usage: python 1-assignment.py <pyhton source file> <option>
    options:
        assign - print assignment stmts
        branch - print branch conditions

Assignment objectives
1. print all assignment statements
2. branch and loop conditions
"""

import sys
import json
import astgen
from pprint import pprint

def ast_to_str(ast):
    def get_stmt(line, end_line, col, end_col):
        if line == end_line:
            return p[line-1][col:end_col]
        else:
            return p[line-1] + "\n" + get_stmt(line+1, end_line, 0, end_col)

    p = program.split("\n")
    return get_stmt(ast["lineno"], ast["end_lineno"], ast["col_offset"], ast["end_col_offset"])

# def print_stmt(line, end_line, col, end_col):
#     stmt = get_stmt(line, end_line, col, end_col)
#     print(f"assignent: \n{stmt}")




def usage():
    help = f"""
    Usage:

    python 1-assignment.py <pyhton source file> <option>
    options:
        assign - print assignment stmts
        branch - print branch conditions"""
    print(help)
    exit()

def get_test(test):
    print("test")
    print(ast_to_str(test))

# def parse_expr(ast):
#     if ast["_type"] == "Name":
#         pass
#     elif ast["_type"] == "Tuple":
#         pass
#     elif ast["_type"] == "BinOp"

def get_for_condition(ast):
    stmt = ast_to_str(ast["target"]) + " in " + ast_to_str(ast["iter"])
    return stmt

def find_branch_conditions(ast):
    """
    function to find branch conditions in the source ast

    branch stmts:
        For(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
        AsyncFor(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
        While(expr test, stmt* body, stmt* orelse)
        If(expr test, stmt* body, stmt* orelse)
    """
    for key in ast:
        if key == "_type":
            if ast["_type"] == "If" or ast["_type"] == "While":
                get_test(ast["test"]) # "test" field of if
                # parse if body
                for d in ast["body"]:
                    find_branch_conditions(d)

                # parse orselse subtree
                for d in ast["orelse"]:
                    find_branch_conditions(d)

            elif ast["_type"] == "For":
                print("parsing for")
                print(get_for_condition(ast)) # combine target and iter of for expression
                
                # parse orselse subtree
                for d in ast["orelse"]:
                    find_branch_conditions(d)

        elif key == "body":
            for d in ast["body"]:
                find_branch_conditions(d)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()

    file_in = sys.argv[1]
    opt = sys.argv[2]

    program = open(file_in).read()
    ast = astgen.generate_ast(file_in)
    
    if opt == "assign":
        find_assignment_stmts(ast)
    elif opt == "branch":
        find_branch_conditions(ast)
    else:
        print(f"unknown option {opt}")
        usage()