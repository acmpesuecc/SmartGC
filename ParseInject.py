import sys
import json
import os

import parser


def inject_deallocation_code(input_file, output_file, json_file):
    try:
        print("Loading deallocation points from JSON file...")
        with open(json_file, 'r') as f:
            try:
                deallocation_data = json.load(f)
                print("Deallocation points loaded successfully.")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON file {json_file}: {e}")
                sys.exit(1)
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file}' not found.")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading JSON file '{json_file}': {e}")
        sys.exit(1)

    deallocation_points = deallocation_data.get('deallocations', [])

    try:
        print("Reading original source code...")
        with open(input_file, 'r') as f:
            source_code = f.readlines()
        print("Original source code read successfully.")
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading input file '{input_file}': {e}")
        sys.exit(1)

    try:
        with open(output_file, 'w') as f:
            print("Injecting deallocation code...")
            for i, line in enumerate(source_code, start=1):
                f.write(line)
                for deallocation_point in deallocation_points:
                    if i == deallocation_point.get('line_number'):
                        variable_name = deallocation_point.get('variable_name')
                        if variable_name:
                            f.write(f'\tfree({variable_name});\n')
                            print(f"Freeing memory for variable '{variable_name}' at line {i}")
                        else:
                            print(f"Warning: 'variable_name' is missing for line {i} in JSON data.")
            print("Deallocation code injected successfully.")
    except IOError as e:
        print(f"Error writing to output file '{output_file}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python preprocess.py input_file output_file json_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    json_file = sys.argv[3]

    # Ensure input and JSON files exist
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    if not os.path.exists(json_file):
        print(f"Error: JSON file '{json_file}' does not exist.")
        sys.exit(1)

    try:
        parser.main(input_file, json_file)
    except Exception as e:
        print(f"Error in parser: {e}")
        sys.exit(1)

    inject_deallocation_code(input_file, output_file, json_file)

