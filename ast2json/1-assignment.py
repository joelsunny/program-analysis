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

def get_stmt(line, end_line, col, end_col):
    p = program.split("\n")

    if line == end_line:
        return p[line-1][col:end_col]
    else:
        return p[line-1] + "\n" + get_stmt(line+1, end_line, 0, end_col)

def print_stmt(line, end_line, col, end_col):
    stmt = get_stmt(line, end_line, col, end_col)
    print(f"assignent: \n{stmt}")


def find_assignment_stmts(ast):
    """
    function to find assignment stmts

    assignment stmts:
        Assign(expr* targets, expr value, string? type_comment)
        AugAssign(expr target, operator op, expr value)
            -- 'simple' indicates that we annotate simple name without parens
        AnnAssign(expr target, expr annotation, expr? value, int simple)
    """
    for key in ast:
        if key == "_type":
            if ast["_type"] == "Assign":
                print_stmt(ast["lineno"], ast["end_lineno"], ast["col_offset"], ast["end_col_offset"])
        elif key == "body":
            for d in ast["body"]:
                find_assignment_stmts(d)

def usage():
    help = f"""
    Usage:

    python 1-assignment.py <pyhton source file> <option>
    options:
        assign - print assignment stmts
        branch - print branch conditions"""
    print(help)
    exit()

def find_branch_conditions(ast):
    """
    function to find branch conditions in the source ast

    branch stmts:
        For(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
        AsyncFor(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
        While(expr test, stmt* body, stmt* orelse)
        If(expr test, stmt* body, stmt* orelse)
    """
    pass

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