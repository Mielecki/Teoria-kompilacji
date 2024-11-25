import AST
from collections import defaultdict
from SymbolTable import *

ttype = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

for op in ['<', '>', '>=', '<=', '==', '!=']:
    ttype[op]['int']['int'] = 'boolean'
    ttype[op]['float']['float'] = 'boolean'
    ttype[op]['int']['float'] = 'boolean'
    ttype[op]['float']['int'] = 'boolean'

for op in ['+', '-', '*', '/', '+=', '-=', '*=', '/=']:
    ttype[op]['int']['int'] = 'int'
    ttype[op]['float']['float'] = 'float'
    ttype[op]['int']['float'] = 'float'
    ttype[op]['float']['int'] = 'float'
    ttype[op]['matrix']['matrix'] = 'matrix'

for op in ['.+', '.-', '.*', './']:
    ttype[op]['matrix']['matrix'] = 'matrix'
    ttype[op]['matrix']['int'] = 'matrix'
    ttype[op]['matrix']['float'] = 'matrix'
    ttype[op]['int']['matrix'] = 'matrix'
    ttype[op]['float']['matrix'] = 'matrix'

class NodeVisitor(object):

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)


    def generic_visit(self, node):        # Called if no explicit visitor function exists for a node.
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        else:
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, AST.Node):
                            self.visit(item)
                elif isinstance(child, AST.Node):
                    self.visit(child)

    # simpler version of generic_visit, not so general
    #def generic_visit(self, node):
    #    for child in node.children:
    #        self.visit(child)



class TypeChecker(NodeVisitor):
    def __init__(self):
        self.symbol_table = SymbolTable(None, "program")
        self.errors = []

    def print_errors(self):
        for err in self.errors:
            print(err)
    
    def new_error(self, msg):
        print(msg)
        self.errors.append(msg)

    def visit_Instructions(self, node):
        for instruction in node.instructions:
            self.visit(instruction)

    def visit_Assignment(self, node):
        self.visit(node.expr)
        self.visit(node.var)
        op = node.op

        if op == '=':
            if node.expr.type == "matrix":
                self.symbol_table.put(node.var.name, VariableSymbol(node.var.name, "matrix", node.expr.size))
                return
            self.symbol_table.put(node.var.name, VariableSymbol(node.var.name, node.expr.type, None))
            return 
        else:
            type_var = self.visit(node.var)
            type_res = ttype[op][type_expr][type_var]
            if type_res == None:
                self.new_error(f"Assignment error: Wrong types ({type_var}, {type_expr})")
                return
            
            self.symbol_table.put(node.var.name, VariableSymbol(node.var.name, type_res))

            return type_res

    def visit_Var(self, node):
        symbol = self.symbol_table.get(node.name)
        if symbol is not None:
            node.type = symbol.type
            node.size = symbol.size
        return


    def visit_Number(self, node):
        if isinstance(node.value, int):
            node.type = "int"
        else:
            node.type = "float"
    
    def visit_Matrix(self, node):
        self.visit(node.matrix)

        first_len = node.matrix[0].size
        if not all([vector.size == node.matrix[0].size for vector in node.matrix]):
            self.new_error("Matrix error: All vectors must have the same size")

        node.type = "matrix"
        node.size = (len(node.matrix), first_len)
        return
        
    def visit_Vector(self, node):
        self.visit(node.vector)
        if node.vector[0].type not in ("int", "float"):
            self.new_error(f"Vector error: Wrong element type ({node.vector[0].type})")
            return

        if not all([element.type == node.vector[0].type for element in node.vector]):
            self.new_error(f"Vector error: All elements must have the same type ({node.vector[0].type})")
            return

        node.type = "vector"
        node.size = (1, len(node.vector))
        return

    def visit_BinExpr(self, node):
        self.visit(node.left)
        self.visit(node.right)   
        op    = node.op
        type = ttype[op][node.left.type][node.right.type]
        if type is None:
            self.new_error(f"BinExpr error: Wrong types ({node.left.type}, {node.right.type})")
            return 
        
        if type == "matrix" and node.left.size != node.right.size:
            self.new_error(f"BinExpr error: Wrong matrix sizes")
            return

        node.type = type
        node.size = node.left.size
        return

