import sys
import json
from ast import parse
from ast2json import ast2json
from os.path import basename

def dumpjson(ast, outfile):
    json.dump(ast, open(outfile, 'w'), indent=4)

def generate_ast(file):
    try:
        program = open(file).read()
    except:
        print(f"failed to read {file}")
    
    ast = ast2json(parse(program))
    return ast

if __name__ == '__main__':
    source = sys.argv[1]
    outfile = sys.argv[2]

    # generate ast json and write to file
    ast = generate_ast(source)
    dumpjson(ast, outfile)