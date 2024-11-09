def check_long_lines(file_path):
    long_lines = []  # List to track lines with more than 100 characters
    
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if len(line) > 100:  # Check if line length exceeds 100 characters
                long_lines.append((line_number, line.strip()))  # Store line number and content without trailing spaces

    # Output the result
    if long_lines:
        print(f"\nLines with more than 100 characters:")
        for line_number, line in long_lines:
            print(f"Line {line_number}: {line}")
    else:
        print(f"\nNo lines with more than 100 characters found.")

# Test the function with the given file path
check_long_lines("../tests/test-files/masha.c")
