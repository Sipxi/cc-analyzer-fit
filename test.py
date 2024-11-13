import re

def check_pointer_operations(file_path):
    """
    Scans a C source code file for pointer manipulation operations involving 
    dereferencing with increment (++) or decrement (--) operators, such as:
    `*i++`, `**i++`, `***i++`, `****i--`, etc.

    Args:
        file_path (str): The path to the C source code file that will be scanned.
    
    Returns:
        list of tuples: A list of tuples where each tuple contains:
            - A matched pointer operation (str)
            - The line number (int) where the operation was found.
        
        If no pointer operations are found, returns an empty list.
    """
    
    # Define the refined pattern for pointer operations involving dereferencing
    pointer_patterns = [
        r'(\*+)\s*\w+\+\+',  # Matches *i++, **i++, ***i++, etc.
        r'(\*+)\s*\w+\-\-',   # Matches *i--, **i--, ***i--, etc.
    ]

    # Combine the patterns into one regex
    pattern = '|'.join(pointer_patterns)
    
    found_operations = []
    
    with open(file_path, 'r') as f:
        # Read the file line by line
        lines = f.readlines()
    
    # Iterate over each line and check for matches
    for line_number, line in enumerate(lines, start=1):
        matches = re.findall(pattern, line)
        
        # If matches are found, add them to the list
        for match in matches:
            # Since match is a tuple, we need to reconstruct the entire operation
            dereference_part = match[0]  # This is the *+ part (e.g., *, **, ***)
            # We capture the entire matched string, which includes the dereference and operator
            full_match = dereference_part + line[line.find(dereference_part)+len(dereference_part):].strip()
            found_operations.append((full_match, line_number))
    
    return found_operations





a = check_pointer_operations("felix.c")
print(a)