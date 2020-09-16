Usage:
=====
    Dependencies:
        python 3.8
        asttojson library

    Other pre-reqs:
    ---------------
    1. Give write and execute permissions to the directory containing the run.sh file
    2. Give execute permission for the contents of source directory
    3. We assume python can be invoked using 'python3' keyword

    ./run.sh <python_file> [option]
        option - possible values are "assign", "branch" or empty.
    Examples:
        1. To print assignment statements as well as branch, loop conditions 
            sh run.sh testcases/while_test.py
        2. To print just the assignment statements
            sh run.sh testcases/assignments_test.py assign
        3. To print just the branch and loop conditions
            sh run.sh testcases/ifelse_test.py branch

    Output:
    -------
    The generated AST will be dumped to "temp" folder in the same directory of the run.sh file.
    The output of the AST analysis will be displayed in the stdout.

Code Structure
================
The 'source' directory contains two python scripts.
    1) astgen.py   - generates the json dump of the program AST
    2) asttostr.py - analyses the ast to output the required statements

The 'testcases' directory contains the python scripts used for testing and their corresponding outputs in .txt format.
For eg. the output corresponding to assignments_test.py is stored in assignments_test.txt

Explanation of Our approach
===========================

    Structure of AST nodes:
    ----------------------
    The abstract grammar which describes the structure of nodes in the AST is given in 
    https://docs.python.org/3.8/library/ast.html#abstract-grammar. 

    For eg. the node corresponding to assignment statements is: Assign(expr* targets, expr value, string? type_comment).
    This translates to a node of type "Assign" with child nodes "targets", which is a list of expressions, and "value",
    which is of type expression, and an optional child node "type_comment" which is a string.

    Source reconstruction from AST:
    -------------------------------
    Once the structure of AST nodes of each type is known, they can be easily translated to get back the source code.
    For eg: a node corresponding to an assignment statement can be translated back as follows:
        statement = ast_to_str(node["targets"]) + " = " + ast_to_str(node["value"])

    This is done in asttostr.py file. The AST is traversed in a depth first manner and the statements are reconstructed
    from the nodes which are of interest to us. The bulk of the work is done in the ast_to_str function, which takes a 
    node of the AST as input and reconstructs the source from the node fields.