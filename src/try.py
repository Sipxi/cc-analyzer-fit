from pycparser import parse_file, c_ast

class VariableVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.variables = []

    def visit_Decl(self, node):
        if isinstance(node.type, c_ast.TypeDecl):
            self.variables.append((node.name, node.coord))
        self.generic_visit(node)

# Parse the C file and print all variables with their locations
ast = parse_file('../tests/test-files/veronika.c', use_cpp=True)  # use_cpp=True handles preprocessing
visitor = VariableVisitor()
visitor.visit(ast)

for var_name, location in visitor.variables:
    print(f"Variable: {var_name} at {location}")
