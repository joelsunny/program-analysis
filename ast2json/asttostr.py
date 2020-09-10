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

def usage():
    help = f"""
    Usage:

    python 1-assignment.py <pyhton source file> <option>
    options:
        assign - print assignment stmts
        branch - print branch conditions"""
    print(help)
    exit()

op_dict = {
    "Add": "+",
    "Sub": "-",
    "Mult": "*",
    "MatMult": "u",
    "Div": "/",
    "Mod": "%",
    "Pow": "**",
    "LShift": ">>",
    "RShift": "<<",
    "BitOr": "u",
    "BitXor": "u",
    "BitAnd": "u",
    "FloorDiv": "u",
    "And": "and",
    "Or": "or"
}

TERMINALS = {"Constant", "Name"}

def ast_to_str(ast, op = False, sub=False):
    """
    two types of nodes:
        1. terminal - Constant, Name
        2. non-terminal
    """
    expr_type = ast["_type"]
    stmt = ""
    if op:
        stmt = op_dict[expr_type]
    elif expr_type == "Constant":
        stmt = str(ast["value"])
    elif expr_type == "Name":
        stmt = ast["id"]
    elif expr_type == "Assign":
        # Assign(expr* targets, expr value, string? type_comment)
        # TODO: why targets?
        stmt = ast_to_str(ast["targets"][0]) + " = " + ast_to_str(ast["value"])
    elif expr_type == "BinOp":
        # BinOp(expr left, operator op, expr right)
        stmt = ast_to_str(ast["left"], sub=True) + ast_to_str(ast["op"], op=True) + ast_to_str(ast["right"], sub=True)
    elif expr_type == "BoolOp":
        # BoolOp(boolop op, expr* values)
        sub_stmts = [ast_to_str(val, sub=True) for val in ast["values"]]
        op = ast_to_str(ast["op"], op=True)
        stmt = f" {op} ".join(sub_stmts)
    elif expr_type == "Tuple":
        # Tuple(expr* elts, expr_context ctx)
        sub_stmts = [ast_to_str(val) for val in ast["elts"]]
        stmt = ", ".join(sub_stmts)
        if ast["ctx"]["_type"] != "Store":
            stmt = f"({stmt})"
    elif expr_type == "List":
        # List(expr* elts, expr_context ctx)
        sub_stmts = [ast_to_str(val) for val in ast["elts"]]
        stmt = ", ".join(sub_stmts)
        stmt = f"[{stmt}]"
    elif expr_type == "Call":
        # Call(expr func, expr* args, keyword* keywords)
        # TODO: keywords?
        args = [ast_to_str(val) for val in ast["args"]]
        #args = f", ".join(args)
        keywords = [ast_to_str(val) for val in ast["keywords"]]
        #keywords = f", ".join(keywords)
        args = args + keywords
        args = f", ".join(args)
        args = f"({args})"
        stmt = ast_to_str(ast["func"]) + args
    elif expr_type == "keyword":
        # keyword = (identifier? arg, expr value)
        stmt = ast["arg"] + "=" + ast_to_str(ast["value"])
    elif expr_type == "ListComp":
        # ListComp(expr elt, comprehension* generators)
        # related: comprehension, IfExp, Compare
        # TODO: why generator list?
        elt = ast_to_str(ast["elt"])
        comprehension = ast_to_str(ast["generators"][0])
        stmt = f"[{elt} for {comprehension}]"
    elif expr_type == "comprehension":
        # comprehension = (expr target, expr iter, expr* ifs, int is_async)
        stmt = ast_to_str(ast["target"]) + " in " + ast_to_str(ast["iter"])
        ifs = [" if " + ast_to_str(val) for val in ast["ifs"]]
        ifs = " ".join(ifs)
        stmt += ifs
    elif expr_type == "Compare":
        # Compare(expr left, cmpop* ops, expr* comparators)
        # cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
        stmt = ast_to_str(ast["left"], sub=True)

    else:
        return f"unimplemented: {expr_type}"
    
    if sub and expr_type not in TERMINALS:
        return "("+stmt+")"
    else:
        return stmt


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
                print(ast_to_str(ast))
        elif key == "body":
            for d in ast["body"]:
                find_assignment_stmts(d)

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