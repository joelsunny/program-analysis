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

# operator = Add | Sub | Mult | MatMult | Div | Mod | Pow | LShift | RShift | BitOr | BitXor | BitAnd | FloorDiv
# unaryop = Invert | Not | UAdd | USub
# cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
op_dict = {
    "Add": "+",
    "Sub": "-",
    "Mult": "*",
    "MatMult": "@",
    "Div": "/",
    "Mod": "%",
    "Pow": "**",
    "LShift": ">>",
    "RShift": "<<",
    "BitOr": "|",
    "BitXor": "^",
    "BitAnd": "&",
    "FloorDiv": "//",
    "Invert": "~",
    "Not": "not",
    "UAdd": "+",
    "Usub": "-",
    "And": "and",
    "Or": "or",
    "Eq": "==",
    "Lt": "<",
    "Gt": ">",
    "NotEq": "!=",
    "LtE": "<=",
    "GtE": ">=",
    "Is": "is",
    "IsNot": "is not",
    "In": "in",
    "NotIn": "not in"
}

TERMINALS = {"Constant", "Name", "arg"}

def ast_to_str(ast, op = False, sub=False):
    """
    two types of nodes:
        1. terminal - Constant, Name, arg
        2. non-terminal
    """
    if ast == None:
        return None
    expr_type = ast["_type"]
    stmt = ""
    
    if op:
        stmt = op_dict[expr_type]
    elif expr_type == "Constant":
        # Constant(constant value, string? kind)
        stmt = str(ast["value"]) if not isinstance(ast["value"], str) else f'"{ast["value"]}"'
    elif expr_type == "Name":
        # Name(identifier id, expr_context ctx)
        stmt = ast["id"]
    elif expr_type == "Assign":
        # Assign(expr* targets, expr value, string? type_comment)
        # TODO: why targets?
        stmt = ast_to_str(ast["targets"][0]) + " = " + ast_to_str(ast["value"])
    elif expr_type == "AugAssign":
        # AugAssign(expr target, operator op, expr value)
        stmt = ast_to_str(ast["target"]) + " " + ast_to_str(ast["op"], op=True) + "= " + ast_to_str(ast["value"])
    elif expr_type == "AnnAssign":
        # AnnAssign(expr target, expr annotation, expr? value, int simple)
        target = ast_to_str(ast["target"])
        annotation = ast_to_str(ast["annotation"])
        value = ast_to_str(ast["value"])
        stmt = f"{target}: {annotation}"
        if value != None:
            stmt += f" = {value}"
    elif expr_type == "BinOp":
        # BinOp(expr left, operator op, expr right)
        stmt = ast_to_str(ast["left"], sub=True) + ast_to_str(ast["op"], op=True) + ast_to_str(ast["right"], sub=True)
    elif expr_type == "BoolOp":
        # BoolOp(boolop op, expr* values)
        sub_stmts = [ast_to_str(val, sub=True) for val in ast["values"]]
        op = ast_to_str(ast["op"], op=True)
        stmt = f" {op} ".join(sub_stmts)
    elif expr_type == "UnaryOp":
        # UnaryOp(unaryop op, expr operand)
        op = ast_to_str(ast["op"], op=True)
        operand = ast_to_str(ast["operand"])
        stmt = f"{op}{operand}"
    elif expr_type == "NamedExpr":
        # NamedExpr(expr target, expr value)
        stmt = ast_to_str(ast["target"]) + " := " + ast_to_str(ast["value"])
    elif expr_type == "Lambda":
        # Lambda(arguments args, expr body)
        stmt = "lambda " + ast_to_str(ast["args"]) + " : " + ast_to_str(ast["body"])
    elif expr_type == "arguments":
        # arguments = (arg* posonlyargs, arg* args, arg? vararg, arg* kwonlyargs, expr* kw_defaults, arg? kwarg, expr* defaults)
        args = [ast_to_str(val) for val in ast["args"]]
        args = ", ".join(args)
        stmt = args
    elif expr_type == "arg":
        # arg = (identifier arg, expr? annotation, string? type_comment)
        # TODO: annotation
        stmt = ast["arg"]
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
    elif expr_type == "Set":
        # Set(expr* elts)
        sub_stmts = [ast_to_str(val) for val in ast["elts"]]
        stmt = ", ".join(sub_stmts)
        stmt = "{" + f"{stmt}" + "}"
    elif expr_type == "Dict":
        # Dict(expr* keys, expr* values)
        keys = [ast_to_str(val) for val in ast["keys"]]
        values = [ast_to_str(val) for val in ast["values"]]
        dictionary = [keys[i] + ": " + values[i] for i in range(len(keys))]
        dictionary = ",".join(dictionary)
        stmt = "{" + dictionary + "}"
    elif expr_type == "SetComp":
        # SetComp(expr elt, comprehension* generators)
        elt = ast_to_str(ast["elt"])
        comprehensions = [ast_to_str(val) for val in ast["generators"]]
        comprehensions = " ".join(comprehensions)
        stmt = "{ " + f"{elt} {comprehensions}" + "}"
    elif expr_type == "DictComp":
        # DictComp(expr key, expr value, comprehension* generators)
        comprehensions = [ast_to_str(val) for val in ast["generators"]]
        comprehensions = " ".join(comprehensions)
        stmt = "{ " + ast_to_str(ast["key"]) + ": " + ast_to_str(ast["value"]) + " " + comprehensions + "}"
    elif expr_type == "GeneratorExp":
        # GeneratorExp(expr elt, comprehension* generators)
        comprehensions = [ast_to_str(val) for val in ast["generators"]]
        comprehensions = " ".join(comprehensions)
        stmt = "(" + ast_to_str(ast["elt"]) + " " + comprehensions + ")"
    elif expr_type == "FormattedValue":
        # FormattedValue(expr value, int? conversion, expr? format_spec)
        # TODO: format spec
        stmt = "{" + ast_to_str(ast["value"]) + "}"
    elif expr_type == "JoinedStr":
        # JoinedStr(expr* values)
        # TODO: handle string space weirdness
        values = [ast_to_str(val) for val in ast["values"]]
        values = "".join(values)
        stmt = values
    elif expr_type == "Attribute":
        # Attribute(expr value, identifier attr, expr_context ctx)
        stmt = ast_to_str(ast["value"]) + "." + ast["attr"]
    elif expr_type == "Starred":
        # Starred(expr value, expr_context ctx)
        stmt = "*" + ast_to_str(ast["value"])
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
    elif expr_type == "Await":
        # Await(expr value)
        stmt = "await " + ast_to_str(ast["value"])
    elif expr_type == "keyword":
        # keyword = (identifier? arg, expr value)
        stmt = ast["arg"] + "=" + ast_to_str(ast["value"])
    elif expr_type == "ListComp":
        # ListComp(expr elt, comprehension* generators)
        # related: comprehension, IfExp, Compare
        # TODO: why generator list?
        elt = ast_to_str(ast["elt"])
        # comprehension = ast_to_str(ast["generators"][0])
        comprehensions = [ast_to_str(val) for val in ast["generators"]]
        comprehensions = " ".join(comprehensions)
        stmt = f"[ {elt} {comprehensions}]"
    elif expr_type == "comprehension":
        # comprehension = (expr target, expr iter, expr* ifs, int is_async)
        stmt = ast_to_str(ast["target"]) + " in " + ast_to_str(ast["iter"])
        ifs = ["if " + ast_to_str(val) for val in ast["ifs"]]
        ifs = " ".join(ifs)
        stmt = "for " + stmt + " " + ifs
    elif expr_type == "Compare":
        # Compare(expr left, cmpop* ops, expr* comparators)
        # cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
        comparators = [ast_to_str(val) for val in ast["comparators"]]
        ops = [ast_to_str(val, op=True) for val in ast["ops"]]
        left = ast_to_str(ast["left"])
        right = [ops[i]+" " + comparators[i] for i in range(len(ops))]
        right = " ".join(right)
        stmt = left + " " + right
    elif expr_type == "IfExp":
        # IfExp(expr test, expr body, expr orelse)
        stmt = ast_to_str(ast["body"]) + " if " + ast_to_str(ast["test"]) + " else " + ast_to_str(ast["orelse"])
    elif expr_type == "Subscript":
        # Subscript(expr value, slice slice, expr_context ctx)
        value = ast_to_str(ast["value"])
        slice_exp = ast_to_str(ast["slice"])
        stmt = f"{value}[{slice_exp}]"
    elif expr_type == "Slice":
        # Slice(expr? lower, expr? upper, expr? step)
        slice_vals = [ast_to_str(ast["lower"]), ast_to_str(ast["upper"]), ast_to_str(ast["step"])]
        slice_vals = ['' if val == None else val for val in slice_vals[0:2] ] + [val for val in slice_vals[2:] if val != None ]
        stmt = ":".join(slice_vals)
    elif expr_type == "Index":
        # Index(expr value)
        stmt = ast_to_str(ast["value"])
    else:
        return f"unimplemented: {expr_type}"
    
    if sub and expr_type not in TERMINALS:
        return "("+stmt+")"
    else:
        return stmt

def find_branch_conditions(ast):
    return []

def find_assignment_stmts(ast):
    """
    function to find assignment stmts

    assignment stmts:
        Assign(expr* targets, expr value, string? type_comment)
        AugAssign(expr target, operator op, expr value)
            -- 'simple' indicates that we annotate simple name without parens
        AnnAssign(expr target, expr annotation, expr? value, int simple)
    """
    stmt_list = []
    for key in ast:
        if key == "_type":
            if ast["_type"] == "Assign" or ast["_type"] == "AugAssign":
                stmt_list.append(ast_to_str(ast))
            elif ast["_type"] == "AnnAssign":
                if ast["value"] != None:
                    stmt_list.append(ast_to_str(ast))
            elif ast["_type"] == "NamedExpr":
                stmt_list.append(ast_to_str(ast))
        elif isinstance(ast[key], dict):
            stmt_list += find_assignment_stmts(ast[key])
        elif isinstance(ast[key], list):
            for node in ast[key]:
                stmt_list += find_assignment_stmts(node)

    return stmt_list

def log_results(assignments, branches, loops, opt, tofile=False):
    def _print_list(lst):
        for element in lst:
            print(element)
        print("\n")

    if opt == "assign" or opt == "all":
        print("Assignment Statements:")
        _print_list(assignments)

    if opt == "branch" or opt == "all":
        print("Branch Conditions:")
        _print_list(branches)
        print("Loop Conditions:")
        _print_list(loops)
    


if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()

    ast_file = sys.argv[1]
    opt = sys.argv[2]


    ast = json.loads(open(ast_file).read())

    assignments = []
    branches = []
    loops = []

    if opt == "assign":
        assignments = find_assignment_stmts(ast)
    elif opt == "branch":
        branches = find_branch_conditions(ast)
    elif opt == "all":
        assignments = find_assignment_stmts(ast)
        branches = find_branch_conditions(ast)
    else:
        print(f"unknown option {opt}")
        usage()
    
    log_results(assignments, branches, loops, opt, tofile=True)