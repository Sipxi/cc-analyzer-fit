import re

def find_short_vars_with_lines(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Regular expressions to match:
    #   - Variables that are one or two characters long
    #   - Ignore characters in single/double quotes or in comments
    var_pattern = r'\b[a-zA-Z]{1,2}\b'  # Matches words with 1 or 2 characters
    quote_pattern = r'(["\']).*?\1'  # Matches anything inside '' or ""
    comment_pattern = r'//.*|/\*[\s\S]*?\*/'  # Matches both // and /* ... */ (multiline)
   # doc_comment_pattern = r'(@brief|@param|@return|@example|@see)'  # Detects documentation tags

    # List of variables to exclude
    exclude_vars = {'i', 'j', 'c', 'if', 'n'}

    results = []
    inside_block_comment = False

    for line_num, line in enumerate(lines, start=1):
        # Skip lines that start with preprocessor directives (e.g., #include, #define)
        if line.strip().startswith("#"):
            continue

        # Check for block comment start and end
        if '/*' in line:
            inside_block_comment = True
        if '*/' in line:
            inside_block_comment = False
            continue  # Skip line containing end of block comment

        # Skip the line if we are inside a block comment
        if inside_block_comment:
            continue

        # Skip lines with documentation comments (e.g., @brief, @param)
      #  if re.search(doc_comment_pattern, line.strip()):
      #      continue

        # Remove inline comments and quoted strings from the line
        line_no_quotes = re.sub(quote_pattern, '', line)
        line_no_comments = re.sub(comment_pattern, '', line_no_quotes)

        # Find variables with 1 or 2 characters in the cleaned line
        matches = re.findall(var_pattern, line_no_comments)

        # Filter out variables that are in the exclude list
        matches = [var for var in matches if var not in exclude_vars]

        if matches:
            for var in matches:
                results.append((var, line_num, line.strip()))

    if results:
        print("Variables that are 1 or 2 characters long (excluding '1', '2', 'i', 'j', and 'c') and their locations:")
        for var, line_num, line_content in results:
            print(f"Variable '{var}' found on line {line_num}: {line_content}")
    else:
        print("No variables found that match the criteria.")

# Replace 'your_file.c' with the path to your C file
find_short_vars_with_lines('../tests/test-files/yelesey.c')
