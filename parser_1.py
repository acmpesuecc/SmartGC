import json
from clang.cindex import Config, CursorKind, Index

Config.set_library_file(r'C:\Program Files\LLVM\bin\libclang.dll')  


index = Index.create()

deallocations = []
references = {}


def traverse_ast(node, start_line=None, in_main_function=False,end_line = None):
    if node.kind == CursorKind.FUNCTION_DECL and node.spelling == "main":
        in_main_function = True
        print(f"Entered main function at line {node.location.line}")

         
    if in_main_function:
        if start_line is None:
            start_line = node.location.line

        if node.kind == CursorKind.FOR_STMT or node.kind == CursorKind.WHILE_STMT:
            start_line = node.location.line
            end_line = node.extent.end.line

        if node.kind == CursorKind.DECL_REF_EXPR:
            if node.referenced and node.referenced.kind == CursorKind.VAR_DECL:
                var_name = node.spelling
                references[var_name] = node.location.line

        for child in node.get_children():
            traverse_ast(child, start_line, in_main_function,end_line)

        if node.kind == CursorKind.FOR_STMT or node.kind == CursorKind.WHILE_STMT:
            for iterator in references.keys():
                line_number = references[iterator]
                if start_line <= line_number <= end_line:
                    references[iterator] = end_line

    if node.kind == CursorKind.FUNCTION_DECL and node.spelling == "main":
        in_main_function = False


def check_alloc_term(filename, line_number, var_name):
    with open(filename, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "alloc" in line and ("*" + var_name) in line:
                print(f"Allocation found for {var_name} at line {i+1}")
                return True
    return False


def main(input_file, json_file):
    index = Index.create()
    tu = index.parse(input_file, args=['-std=c11'])
    print('Translation unit:', tu.spelling)

    for node in tu.cursor.get_children():
        if node.kind == CursorKind.FUNCTION_DECL:
            traverse_ast(node)

    for iterator in references.keys():
        references[iterator] = int(references[iterator])
        line_number = references[iterator]
        if check_alloc_term(input_file, line_number, iterator):
            deallocations.append({"line_number": line_number, "variable_name": iterator})

    output = {
        "deallocations": deallocations
    }
    #print(deallocations)

    if deallocations:
        with open(json_file, 'w') as f:
            json.dump(output, f, indent=4)
        print("Data written to references.json")
    else:
        print("No deallocations found.")
