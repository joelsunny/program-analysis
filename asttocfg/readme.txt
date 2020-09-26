Usage:
=====
    Dependencies:
    -------------
        python 3.8
        asttojson library
        graphviz python library
        graphviz tool
        Image utility capable of displaying 'svg' (any web browser)

    Other pre-reqs:
    ---------------
    1. Give write and execute permissions to the directory containing the run.sh file
    2. Give execute permission for the contents of source directory
    3. We assume python can be invoked using 'python3' keyword

    ./run.sh <python_file>
    Example:
        1. sh run.sh testcases/while_test.py

    Output:
    -------
    The files generated as part of execution are placed under the "temp" folder in the same directory of the run.sh file.
    The files generated for a program 'sample_prog.py' are:
        1) AST json - 'sample_prog.json'
        2) dot file corresponding to the CFG - 'sample_prog.gv'
        3) graphviz rendered image. The image is in scalable vector graphics(svg) format - 'sample_prog.gv.svg'
    
    Notes about the CFG Image:
    ---------------------
    1. The program when run, will try to open the output image by default. If it fails to find a suitable tool, 
       an exception will be raised.
    
    2. The nodes in the output CFG are color coded into three categories for ease of understanding.
        i. Green  - Special ENTRY and EXIT blocks
       ii. Yellow - Normal basic blocks
      iii. Red    - Dummy nodes added at the end of an if else ladder, not followed by any other statement, within a loop.
                    This is done to avoid two back edges (one from the if body, another from else body) to the loop condition, so
                    that the resulting CFG is more human friendly. eg. see output of testcases/mixed_while_if_test.py

Code Structure
================
The 'source' directory contains two python scripts.
    1) astgen.py   - generates the json dump of the program AST
    2) asttostr.py - analyses the ast to output the required statements
    3) asttocfg.py - generates control flow graph from AST

The 'testcases' directory contains the python scripts used for testing and their corresponding output CFGs as 'svg' images.
For eg. the output corresponding to if_test.py is stored in if_test.svg

Explanation of Our approach
===========================
