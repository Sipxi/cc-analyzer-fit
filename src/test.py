import subprocess
import re
import platform

class CCodeAnalyzer:
    MAX_MAIN_LENGTH = 20
    def __init__(self, c_file_path):
        self.c_file_path = c_file_path
        self.global_vars = []
        self.long_rows = []
        self.magic_constants = []
        self.main_length = self.get_main_length()
        
    def check_for_global_vars(self):
        # Determine the platform to use the appropriate command
        if platform.system() == "Windows":
            command = f"ctags -x {self.c_file_path} | findstr \"variable\""
        else:  # For Linux and other Unix-like systems
            command = f"ctags -x {self.c_file_path} | grep \"variable\""
        
        # Run the command
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)

        lines = result.stdout.splitlines()
        for line in lines:
            tokens = line.split()  # Split by whitespace
            if len(tokens) >= 3:  # Ensure there are at least 3 tokens
                key = tokens[0]  # First token (variable name)
                value = tokens[2]  # Third token (line number)
                self.global_vars.append((key, value))
        print(f"Global var: {self.global_vars}\n")
        
    def check_for_magic_constants(self):
        number_pattern = r"(?<!['\"//])\b(?!1\b|0\b)\d+\b(?!['\"//])"
        
        numeric_pattern = re.compile(number_pattern)  # Matches integers (excluding 0 and 1)
        with open(self.c_file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                # Find all matches of numbers in the current line
                numeric_matches = numeric_pattern.findall(line)
                for match in numeric_matches:
                    self.magic_constants.append((line_number, match))
        print(f"Magic constants: {self.magic_constants}\n")
        
    def check_long_lines(self):
        with open(self.c_file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                if len(line) > 100: 
                    self.long_rows.append((line_number, len(line))) 
        print(f"Long rows: {self.long_rows}\n") 
        
    def get_main_length(self):
        in_main = False
        brace_count = 0
        main_length = 0
        in_block_comment = False
        opened_brace = False  # Track if we've encountered the opening brace

        with open(self.c_file_path, 'r') as file:
            for line in file:
                # Remove inline comments and check for single-line comments
                line = re.sub(r'//.*', '', line).strip()
                
                # Handle block comments
                if not in_block_comment:
                    # Check if the line starts a block comment
                    if '/*' in line:
                        in_block_comment = True
                        # Remove everything after the start of the block comment
                        line = re.sub(r'/\*.*', '', line).strip()
                else:
                    # Check if the line ends a block comment
                    if '*/' in line:
                        in_block_comment = False
                        # Remove everything up to the end of the block comment
                        line = re.sub(r'.*\*/', '', line).strip()
                    else:
                        # Skip the line if it’s within a block comment
                        continue

                # Skip if the line is empty after removing comments and whitespace
                if not line:
                    continue

                # Detect the start of the main function (first part of signature)
                if not in_main and re.search(r"\bint\s+main\s*\(", line):
                    in_main = True
                    # We found the main function, check if the brace is on the same line
                    if '{' in line:
                        brace_count += line.count('{')
                        main_length += 1  # Count the signature line as part of the function
                        opened_brace = True  # Opening brace is on the same line

                # If the opening brace wasn't on the same line, check for it on the next lines
                if in_main and not opened_brace:
                    if '{' in line:
                        brace_count += line.count('{')
                        opened_brace = True
                        main_length += 1  # Count the line with the opening brace

                # If inside main, count lines and track braces
                if in_main and opened_brace:
                    # Count lines inside the main function
                    main_length += 1
                    brace_count += line.count('{') - line.count('}')
                    
                    # If brace count is zero, we've reached the end of main
                    if brace_count == 0:
                        break

        return main_length if in_main else 0
    def check_main_length(self):    
        if self.main_length >= 40:
            print(f"Exceeded max main length: {self.main_length}")


if __name__ == "__main__":
    c_file = "../tests/test-files/veronika.c"
    analyzer = CCodeAnalyzer(c_file)
    analyzer.check_for_global_vars()
    analyzer.check_for_magic_constants()
    analyzer.check_long_lines()
    analyzer.check_main_length()
