Usage:
=====
    Dependencies:
    -------------
        python 3.8
        asttojson library
        graphviz python library
        graphviz tool

    Other pre-reqs:
    ---------------
    1. Give write and execute permissions to the directory containing the run.sh file
    2. Give execute permission for the contents of source directory
    3. We assume python can be invoked using 'python3' keyword

    ./run.sh <python_file>
    Example:
        1. sh run.sh testcases/test3.py

    Output:
    -------
    The optimized program is placed under the temp directory. Various intermediate files generated as part of execution are 
    also placed under the "temp" folder in the same directory of the run.sh file.
    The files generated for a program 'sample_prog.py' are:
        1) AST json - 'sample_prog.json'
        2) dot file corresponding to the CFG - 'sample_prog.gv'
        3) graphviz rendered image. The image is in scalable vector graphics(svg) format - 'sample_prog.gv.svg' 
        4) optimized program after faint variable analysis - sample_prog_optimized.py 

    The statements removed by the tool are also displayed in the console.
    
Implementation details
======================
Details about the algorithm and Implementation are included in the report