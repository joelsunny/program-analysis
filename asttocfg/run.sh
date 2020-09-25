
# function definitions
usage() {
    echo "sh run.sh <python_file> [option]"
    echo "    option - possible values are 'assign', 'branch' or empty."
    echo "Examples:"
    echo "    1. To print all assignment statements"
    echo "        sh run.sh testcases/assignments_test.py assign"
    echo "    2. To print all branch,loop conditions"
    echo "        sh run.sh testcases/ifelse_test.py branch"
    echo "    3. To print assignment statements as well as branch, loop conditions"
    echo "        sh run.sh testcases/while_test.py"

    exit 0
} 

init() {
    if [ $# -lt 1 ]; then
        usage
    fi
    SCRIPT=$(readlink -f $0)
    DIR=$(dirname $SCRIPT)

    # get file base name, which will be used to store the ast json
    prog=$1
    fname=$(basename $prog)
    fname=$(echo $fname | cut -d "." -f1)
    tempdir="$DIR/temp"
    ast="$tempdir/${fname}.json"

    
    if [ ! -d "$tempdir" ]; then
        mkdir -p $tempdir
        chmod 777 $tempdir
    fi
    
    if [ -f "$ast" ]; then
        rm -f $ast
    fi

}

generate_ast() {
    if [ ! -f $prog ]; then
        echo "ERROR: couldn't locate file ${prog}"
        exit 1
    fi
    echo "INFO: generating ast"
    # echo "INFO: python $DIR/source/astgen.py $prog $ast"
    python $DIR/source/astgen.py $prog $ast
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: received exit code $exit_code"
        exit 1
    fi
}

generate_3ac() {
    echo "INFO: invoking tool to generate CFG"
    python $DIR/source/asttocfg.py $ast 
}

# main
init $@
generate_ast
generate_3ac
