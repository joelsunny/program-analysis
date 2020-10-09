
# function definitions
usage() {
    echo "sh run.sh <python_file> [option]"

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
    python3 $DIR/source/astgen.py $prog $ast
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: received exit code $exit_code"
        exit 1
    fi
}

faintvariable_optimise() {
    echo "INFO: invoking tool for faint variable optimisation"
    python3 $DIR/source/faintvariable.py $ast 
}

# main
init $@
generate_ast
faintvariable_optimise
