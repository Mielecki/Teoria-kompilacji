import sys
from scanner import Scanner
from parser import Mparser
from TreePrinter import TreePrinter
from TypeChecker import TypeChecker

if __name__ == '__main__':

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    text = file.read()
    parser = Mparser()
    lexer = Scanner()

    ast = parser.parse(lexer.tokenize(text))
    ast.printTree(0)
    # Below code shows how to use visitor
    # typeChecker = TypeChecker()   
    # typeChecker.visit(ast)   
    # print(typeChecker.symbol_table.symbols)