import astgen
import sys

def ast_to_3ac(ast):
    """
    traverse a node in post order fashion to produce the three address code.

    algorithm description:
        1. on visiting any binary operator node, generate a new temporary variable to store the intermediate value
        2. on branch instructions generate two labels.
            eg. if (c1) then
                    b1
                else:
                    b2
            gets translated to:
            if c1 goto L1:
            ast_to_3ac(b2)
            goto L2:
            L1: ast_to_3ac(b1)
            L2:
    """
    pass

if __name__ == '__main__':
    ast = sys.argv[1]
    # load AST json
    ast = json.loads(open(ast_file).read())

    res = ast_to_3ac(ast)