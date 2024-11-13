import re

class FunctionArgCounter:
    def __init__(self, c_file_path):
        self.c_file_path = c_file_path
        self.magic_constants = []  # List to store magic constants

    def check_for_magic_constants(self):
        # Pattern for numbers (excluding 0, 1, 2) not inside string or character literals
        number_pattern = r"(?<!['\"//])\b(?!1\b|0\b|2\b)\d+\b(?!['\"//])"
        numeric_pattern = re.compile(number_pattern)  # Matches integers (excluding 0, 1, and 2)
        
        # Regular expression to detect string and character literals
        string_literal_pattern = r'"([^"\\]*(\\.[^"\\]*)*)"'
        char_literal_pattern = r"'([^'\\]*(\\.[^'\\]*)*)'"

        with open(self.c_file_path, 'r') as file:
            inside_block_comment = False  # Track whether inside a block comment

            for line_number, line in enumerate(file, start=1):
                stripped_line = line.strip()

                # Skip lines that are preprocessor directives (e.g., #define)
                if stripped_line.startswith("#define"):
                    continue

                # Handle block comment start and end
                if "/*" in stripped_line:
                    inside_block_comment = True
                if "*/" in stripped_line:
                    inside_block_comment = False

                # Skip line if inside a comment block or line comment
                if inside_block_comment or "//" in stripped_line:
                    continue

                # Ignore numbers inside string literals or character literals
                # First find all string and char literals and mark them
                string_literals = re.findall(string_literal_pattern, line)
                char_literals = re.findall(char_literal_pattern, line)

                # Remove numbers in literals by replacing them with a placeholder
                for literal in string_literals + char_literals:
                    line = line.replace(literal[0], ' ' * len(literal[0]))  # Replace literal with spaces

                # Find all matches of numbers in the current line, excluding those in literals
                numeric_matches = numeric_pattern.findall(line)
                for match in numeric_matches:
                    self.magic_constants.append((line_number, match))

        # Print the result of magic constants
        print(f"Magic constants: {self.magic_constants}\n")

# Usage
def main():
    # Replace with the path to your C file
    c_file_path = "../tests/test-files/sgran.c"  
    
    # Create an instance of the FunctionArgCounter class
    counter = FunctionArgCounter(c_file_path)
    
    # Get the magic constants (excluding numbers defined in #define)
    counter.check_for_magic_constants()

if __name__ == "__main__":
    main()
