import subprocess
import re

def get_function_declarations(c_file_path):
    """
    Get function declarations from a C file using ctags.
    Returns a list of tuples: (function_name, starting_line).
    """
    command = f"ctags -x --c-kinds=f {c_file_path}"

    # Run the command to get function declarations
    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    lines = result.stdout.splitlines()
    
    function_declarations = []
    for line in lines:
        tokens = line.split()  # Split by whitespace
        if len(tokens) >= 3:  # Ensure there are at least 3 tokens
            func_name = tokens[0]  # First token (function name)
            line_number = int(tokens[2])  # Third token (line number)
            function_declarations.append((func_name, line_number))
    return function_declarations



def get_function_length(start_line, c_file_path):
    func_length = 1
    brackets_to_close = 0
    inside_block_comment = False
    initial_bracket = False
    with open(c_file_path, 'r') as f:
        lines = f.readlines()
    
    for i in range(start_line, len(lines)):
        line = lines[i].strip()  # Remove leading/trailing whitespaces

        # Skip empty lines
        if not line:
            continue
        
        # Skip single-line comments
        if line.startswith("//"):
            continue
        
        # Handle block comments
        if "/*" in line:
            inside_block_comment = True
        if inside_block_comment:
            if "*/" in line:
                inside_block_comment = False
            continue
        
        # Now process the non-comment lines
        for j in range(len(line)):
            if line[j] == '{':
                if initial_bracket == False:
                    initial_bracket = True
                brackets_to_close += 1
            elif line[j] == '}':
                brackets_to_close -= 1

        if brackets_to_close == 0 and initial_bracket == True:
            initial_bracket = False
            break

        # Only increment the function length for non-empty, non-comment lines
        func_length += 1
    return func_length



def check_function_lengths(c_file_path):
    """
    Calculate the length (in lines) of each function in the given C file, excluding whitespaces and comments.
    """
    # Get function declarations from the ctags output
    function_declarations = get_function_declarations(c_file_path)
    print(function_declarations)
    print(get_function_length(function_declarations[0][1]-1, c_file_path))



if __name__ == "__main__":
    # Specify the path to your C file
    c_file_path = "../tests/test-files/veronika.c"  # Replace with the actual file path
    
    check_function_lengths(c_file_path)
