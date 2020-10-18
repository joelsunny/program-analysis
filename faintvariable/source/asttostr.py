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

# operators in python
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
    "Not": "not ",
    "UAdd": "+",
    "USub": "-",
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
PRECEDENCE = {"BinOp", "BoolOp", "Compare"}


def ast_to_str2(ast, block, faint, idx, op=False, sub=False, join=False, prefix=0, OrElse=False):
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
        if join and isinstance(ast["value"], str):
            # if join is true and the constant is a string, then part of JoinedExpr. Don't return the quotes
            stmt = ast["value"]
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

        # disable parenthisation for string concatenation, for clearer output
        if ast["left"]["_type"] == "Constant":
            if isinstance(ast["left"]["value"], str):
                sub=False
        elif ast["right"]["_type"] == "Constant":
            if isinstance(ast["right"]["value"], str):
                sub=False

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
    elif expr_type == "Expr":
        # Expr(expr value)
        stmt = ast_to_str(ast["value"])
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
        values = [ast_to_str(val, join=True) for val in ast["values"]]
        values = "".join(values)
        stmt = "f" + "\"" + values + "\""
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
        left = ast_to_str(ast["left"], sub=True)
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
    elif expr_type == "If":
        # If(expr test, stmt* body, stmt* orelse)
        test = ast_to_str(ast["test"])
        body = [ast_to_str(i, prefix=prefix+1) for i in ast["body"]]
        body = f"\n".join(body)
        body = body
        orelse = ""
        if len(ast["orelse"]) > 0:
            # orelse = [ast_to_str(i, OrElse=True, prefix=prefix) for i in ast["orelse"]]
            if ast["orelse"][0]["_type"] == "If":
                orelse = [ast_to_str(i, OrElse=True, prefix=prefix) for i in ast["orelse"]]
                orelse = "\n".join(orelse)
            else:
                orelse = "else:"
                for i, node in enumerate(ast["orelse"]):
                    orelse += "\n" + ast_to_str(node, prefix=prefix+1)

        if OrElse == True:
            stmt = f"elif {test}:\n{body}\n{orelse}"
        else: 
            stmt = f"if {test}:\n{body}\n{orelse}"
    elif expr_type == "While":
        # While(expr test, stmt* body, stmt* orelse)
        test = ast_to_str(ast["test"])
        body = ""
        for i, node in enumerate(ast["body"]):
            body += "\n" + ast_to_str(node, prefix=prefix+1)
        stmt = f"while {test}:{body}"
    else:
        return f"unimplemented: {expr_type}"
    
    pfix = "\t"*prefix
    if sub and (expr_type not in TERMINALS):
        return pfix + "("+stmt+")"
    else:
        return pfix+stmt



def ast_to_str(ast, op=False, sub=False, join=False, prefix=0, OrElse=False):
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
        if join and isinstance(ast["value"], str):
            # if join is true and the constant is a string, then part of JoinedExpr. Don't return the quotes
            stmt = ast["value"]
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

        # disable parenthisation for string concatenation, for clearer output
        if ast["left"]["_type"] == "Constant":
            if isinstance(ast["left"]["value"], str):
                sub=False
        elif ast["right"]["_type"] == "Constant":
            if isinstance(ast["right"]["value"], str):
                sub=False

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
    elif expr_type == "Expr":
        # Expr(expr value)
        stmt = ast_to_str(ast["value"])
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
        values = [ast_to_str(val, join=True) for val in ast["values"]]
        values = "".join(values)
        stmt = "f" + "\"" + values + "\""
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
        left = ast_to_str(ast["left"], sub=True)
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
    elif expr_type == "If":
        # If(expr test, stmt* body, stmt* orelse)
        test = ast_to_str(ast["test"])
        body = [ast_to_str(i, prefix=prefix+1) for i in ast["body"]]
        body = f"\n".join(body)
        body = body
        orelse = ""
        if len(ast["orelse"]) > 0:
            # orelse = [ast_to_str(i, OrElse=True, prefix=prefix) for i in ast["orelse"]]
            if ast["orelse"][0]["_type"] == "If":
                orelse = [ast_to_str(i, OrElse=True, prefix=prefix) for i in ast["orelse"]]
                orelse = "\n".join(orelse)
            else:
                orelse = "else:"
                for i, node in enumerate(ast["orelse"]):
                    orelse += "\n" + ast_to_str(node, prefix=prefix+1)

        if OrElse == True:
            stmt = f"elif {test}:\n{body}\n{orelse}"
        else: 
            stmt = f"if {test}:\n{body}\n{orelse}"
    elif expr_type == "While":
        # While(expr test, stmt* body, stmt* orelse)
        test = ast_to_str(ast["test"])
        body = ""
        for i, node in enumerate(ast["body"]):
            body += "\n" + ast_to_str(node, prefix=prefix+1)
        stmt = f"while {test}:{body}"
    else:
        return f"unimplemented: {expr_type}"
    
    pfix = "\t"*prefix
    if sub and (expr_type not in TERMINALS):
        return pfix + "("+stmt+")"
    else:
        return pfix+stmt

def find_loop_conditions(ast):
    """
    function to find loop conditions.

    loop conditions:
        For(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
        AsyncFor(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
        While(expr test, stmt* body, stmt* orelse)
    """
    stmt_list = []
    for key in ast:
        if key == "_type":
            if ast["_type"] == "For":
                # For(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
                stmt_list.append(ast_to_str(ast["target"]) + " in " + ast_to_str(ast["iter"]))
            elif ast["_type"] == "While":
                # While(expr test, stmt* body, stmt* orelse)
                stmt_list.append(ast_to_str(ast["test"]))
            elif ast["_type"] == "AsyncFor":
                # AsyncFor(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
                stmt_list.append(ast_to_str(ast["target"]) + " in " + ast_to_str(ast["iter"]))
        elif isinstance(ast[key], dict):
            stmt_list += find_loop_conditions(ast[key])
        elif isinstance(ast[key], list):
            for node in ast[key]:
                stmt_list += find_loop_conditions(node)

    return stmt_list

def find_branch_conditions(ast):
    """
    function to find branch conditions.

    branch conditions:
        If(expr test, stmt* body, stmt* orelse)
    """
    stmt_list = []
    for key in ast:
        if key == "_type":
            if ast["_type"] == "If":
                stmt_list.append(ast_to_str(ast["test"]))
        elif isinstance(ast[key], dict):
            stmt_list += find_branch_conditions(ast[key])
        elif isinstance(ast[key], list):
            for node in ast[key]:
                stmt_list += find_branch_conditions(node)

    return stmt_list

def find_assignment_stmts(ast):
    """
    function to find assignment stmts

    assignment stmts:
        Assign(expr* targets, expr value, string? type_comment)
        AugAssign(expr target, operator op, expr value)
            -- 'simple' indicates that we annotate simple name without parens
        AnnAssign(expr target, expr annotation, expr? value, int simple)
        NamedExpr(expr target, expr value)
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

def log_results(assignments, branches, loops, opt, outfile=None):
    """
    function to output the results of the analysis. If outfile parameter is
    supplied, the output is written to the file. Otherwise printed to stdout
    """
    if outfile != None:
        sys.stdout = outfile

    def _print_list(lst):
        for element in lst:
            print(element)
        print("\n")

    if opt == "assign" or opt == "all":
        print("Assignment Statements:\n")
        _print_list(assignments)

    if opt == "branch" or opt == "all":
        print("Branch Conditions:\n")
        _print_list(branches)
        print("Loop Conditions:\n")
        _print_list(loops)
    


if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()

    # read inputs to the script
    ast_file = sys.argv[1]
    opt = sys.argv[2]

    # load AST json
    ast = json.loads(open(ast_file).read())

    # intitialize the result arrays
    assignments = []
    branches = []
    loops = []

    if opt == "assign":
        assignments = find_assignment_stmts(ast)
    elif opt == "branch":
        branches = find_branch_conditions(ast)
        loops = find_loop_conditions(ast)
    elif opt == "all":
        assignments = find_assignment_stmts(ast)
        branches = find_branch_conditions(ast)
        loops = find_loop_conditions(ast)
    else:
        print(f"unknown option {opt}")
        usage()

    print("INFO: Output:\n")
    log_results(assignments, branches, loops, opt, outfile=None)