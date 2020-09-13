#!/usr/bin/env bash

# function definitions
function usage() {
    echo "sh $0 <python_file> [option]"
    echo "  options:"
    echo "       assign - print assignment stmts"
    echo "       branch - print branch and loop conditions"
    echo "       all    - print branch,loop conditions and assignment statements. This is the default"
    exit 0
}

function init() {
    # if [ $# -lt 1 ]; then
    #     usage()
    # fi
    SCRIPT=$(readlink -f $0)
    DIR=$(dirname $SCRIPT)

    # get file base name, which will be used to store the ast json
    prog=$1
    fname=$(basename $prog)
    fname=$(echo $fname | cut -d "." -f1)
    tempdir="$DIR/temp"
    ast="$tempdir/${fname}.json"

    opt="all"
    if [ ! -d "$tempdir" ]; then
        mkdir -p $tempdir
        chmod 777 $tempdir
    fi
    
    if [ -f "$ast" ]; then
        rm -f $ast
    fi

}

function generate_ast() {
    if [ ! -f $prog ]; then
        echo "ERROR: couldn't locate file ${prog}"
    fi
    echo "INFO: generating ast"
    echo "INFO: python $DIR/source/astgen.py $prog $ast"
    python $DIR/source/astgen.py $prog $ast
}

function analyze_ast() {
    echo "INFO: invoking tool to print required statements"
    python $DIR/source/asttostr.py $ast $opt 
}

# main
init $@
generate_ast
analyze_ast 
