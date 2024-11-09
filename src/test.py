import subprocess
import re

class CCodeAnalyzer:
    def __init__(self, c_file_path):
        self.c_file_path = c_file_path
        self.global_vars = []
        self.magic_constants = []
        
    def check_for_global_vars(self):
        result = subprocess.run(f"ctags -x {self.c_file_path} | findstr \"variable\"", shell=True, capture_output=True, text=True, check=True)

        lines = result.stdout.splitlines()
        for line in lines:
            tokens = line.split()  # Split by whitespace
            if len(tokens) >= 3:  # Ensure there are at least 3 tokens
                key = tokens[0]  # First token (variable name)
                value = tokens[2]  # Third token (line number)
                self.global_vars.append((key, value))
        print(self.global_vars)
        
    def check_for_magic_constants(self):
        number_pattern = r"(?<!['\"//])\b(?!1\b|0\b)\d+\b(?!['\"//])"
        
        numeric_pattern = re.compile(number_pattern)  # Matches integers (excluding 0 and 1)
        with open(self.c_file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                # Find all matches of numbers in the current line
                numeric_matches = numeric_pattern.findall(line)
                for match in numeric_matches:
                    self.magic_constants.append((line_number, match))
        print(self.magic_constants)

        
if __name__ == "__main__":
    c_file = "../tests/test-files/masha.c"
    analyzer = CCodeAnalyzer(c_file)
    analyzer.check_for_global_vars()
    analyzer.check_for_magic_constants()