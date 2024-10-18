import json
from clang.cindex import CursorKind, Index
import os

def traverse_ast(node, references, start_line=None, end_line=None):
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
        traverse_ast(child, references, start_line, end_line)

    if node.kind == CursorKind.FOR_STMT or node.kind == CursorKind.WHILE_STMT:
        for var_name, line_number in references.items():
            if start_line <= line_number <= end_line:
                references[var_name] = end_line


def check_allocation_in_line(line, var_name):
    """
    Checks if the line contains an allocation for the given variable name.
    """
    return "alloc" in line and f"*{var_name}" in line


def find_allocation(filename, line_number, var_name):
    """
    Searches for an allocation for the given variable in the file, starting at the given line number.
    """
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            if 0 <= line_number < len(lines):
                for line in lines[line_number - 1:]:
                    if check_allocation_in_line(line, var_name):
                        return True
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except IOError as e:
        print(f"Error reading file '{filename}': {e}")
    return False


def extract_deallocation_points(input_file, references):
    """
    Extracts deallocation points by checking for allocations for variables referenced in the source code.
    """
    deallocations = []
    for var_name, line_number in references.items():
        if find_allocation(input_file, line_number, var_name):
            deallocations.append({"line_number": line_number, "variable_name": var_name})
    return deallocations


def write_deallocation_to_json(deallocations, json_file):
    """
    Writes the deallocation data to a JSON file.
    """
    if deallocations:
        output = {"deallocations": deallocations}
        try:
            with open(json_file, 'w') as f:
                json.dump(output, f, indent=4)
            print(f"Deallocation points written to {json_file}")
        except IOError as e:
            print(f"Error writing to JSON file '{json_file}': {e}")
    else:
        print("No deallocation points found.")


def main(input_file, json_file):
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        return

    index = Index.create()
    try:
        tu = index.parse(input_file, args=['-std=c11'])
        print(f'Translation unit: {tu.spelling}')
    except Exception as e:
        print(f"Error parsing file '{input_file}': {e}")
        return

    references = {}
    for node in tu.cursor.get_children():
        if node.kind == CursorKind.FUNCTION_DECL:
            traverse_ast(node, references)

    # Extract deallocation points based on references
    deallocations = extract_deallocation_points(input_file, references)

    # Write the deallocation points to a JSON file
    write_deallocation_to_json(deallocations, json_file)
