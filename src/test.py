import subprocess
import re

#*DONE # tnine.c:7: magicka konstanta '102'
#*DONE # tnine.c:57: funkce 'main' je prilis dlouha (48 radku)
#*DONE # tnine.c:93: pouziti explicitniho pretypovani (int)
#*DONE # tnine.c:121: identifikator je prilis kratky: 'k
#*DONE check for global vars
#*DONE # tnine.c:113: obtizne citelny kod, prilis dlouhy radek (108 znaku)
#*DONE # tnine.c:22: identifikator nezacina malym pismenem: 'CheckForErrors'

#TODO # tnine.c: nedostatek komentaru: 0%
#TODO # tnine.c:1: velky segment kodu bez komentaru (83 radku)
#TODO # tnine.c:113: obtizne citelny kod, prilis dlouhy radek (108 znaku)
#? # tnine.c:123: funkce 'find_contacts' je prilis dlouha (253 radku)
#TODO # tnine.c:123: funkce 'find_contacts' je extremne slozita! (67 cest)
#TODO # tnine.c:623: funkce 'is_any_matching' ma prilis mnoho parametru (6)
#TODO # tnine.c: obtizne citelny kod, prilis husty (10%)
#TODO
#TODO

class CCodeAnalyzer:
    MAX_MAIN_LENGTH = 20
    MAX_FUNCTION_LENGTH = 100
    def __init__(self, c_file_path):
        self.c_file_path = c_file_path
        self.global_vars = []
        self.long_rows = []
        self.magic_constants = []
        self.short_vars = []
        self.explicit_casts = []
        self.bad_function_declarations = []
        self.functions_length = []
    
    
    def __remove_comments(self, lines):
        # This function removes both single-line and multi-line comments
        code_lines = []
        in_comment_block = False

        for line in lines:
            line = line.strip()
            
            if in_comment_block:
                if '*/' in line:
                    in_comment_block = False
                    # Everything after the closing comment marker is ignored for this line
                    line = line.split('*/', 1)[1].strip()
                else:
                    continue  # Skip the entire line if it's inside a comment block
            if not in_comment_block:
                # Remove single-line comments
                if '//' in line:
                    line = line.split('//', 1)[0].strip()

                # Check if the line starts a multi-line comment block
                if '/*' in line:
                    in_comment_block = True
                    line = line.split('/*', 1)[0].strip()
                
                # Only add non-empty lines with actual code
                if line:
                    code_lines.append(line)
        
        return code_lines
    
    def count_function_lines(self):
        with open(self.c_file_path, 'r') as file:
            lines = file.readlines()

        function_regex = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*\s+\*?[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*\{')
        inside_function = False
        function_name = ""
        start_line = -1
        line_count = 0
        braces_count = 0

        for line_num, line in enumerate(lines, start=1):
            line = line.strip()  # Remove leading/trailing whitespace
            if function_regex.match(line):  # Found function signature
                if inside_function:
                    self.functions_length.append((function_name, line_count, start_line))
                function_name = line.split()[1]  # Extract function name
                inside_function = True
                start_line = line_num
                line_count = 1  # Start counting lines for this function
                braces_count = 1  # Count the opening brace
            elif inside_function:
                # Remove comments from inside the function body
                code_lines = self.__remove_comments([line])
                
                # Skip empty or whitespace-only lines after removing comments
                if code_lines:
                    line_count += 1

                braces_count += line.count('{')
                braces_count -= line.count('}')
                
                if braces_count == 0:  # Function ends when braces match
                    self.functions_length.append((function_name, line_count, start_line))
                    inside_function = False
                    braces_count = 0  # Reset brace counter

        # Check if the last function is still open and needs to be closed
        if inside_function:
            self.functions_length.append((function_name, line_count, start_line))


    
    def check_for_function_declarations(self):
        command = f"ctags -x --c-kinds=f {self.c_file_path}"
        
        # Run the command
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        for line in lines:
            tokens = line.split()  # Split by whitespace
            if len(tokens) >= 3:  # Ensure there are at least 3 tokens
                if tokens[0][0].isupper():
                    key = tokens[0]  # First token (variable name)
                    value = tokens[2]  # Third token (line number)
                    self.bad_function_declarations.append((key, value))
        print(f"Bad function declarations: {self.bad_function_declarations}\n")
    
    def check_for_global_vars(self):
        command = f"ctags -x --c-kinds=v {self.c_file_path}"
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
        
    def check_functions_length(self):    
        self.count_function_lines()
        for function_name, line_count, start_line in self.functions_length:
            if function_name == "main" and line_count >= CCodeAnalyzer.MAX_MAIN_LENGTH:
                print(f"Main function length exceeded. '{function_name}'Line count: {line_count}, Start line: {start_line}\n")
            elif line_count >= CCodeAnalyzer.MAX_FUNCTION_LENGTH:
                print(f"Function length exceeded. '{function_name}'")
    
    def check_short_vars(self):
        with open(self.c_file_path, 'r') as file:
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
            # Remove inline comments and quoted strings from the line
            line_no_quotes = re.sub(quote_pattern, '', line)
            line_no_comments = re.sub(comment_pattern, '', line_no_quotes)

            # Find variables with 1 or 2 characters in the cleaned line
            matches = re.findall(var_pattern, line_no_comments)

            # Filter out variables that are in the exclude list
            matches = [var for var in matches if var not in exclude_vars]

            if matches:
                for var in matches:
                    results.append((var, line_num))
    
    def check_explicit_casts(self):
        # Regular expression pattern to match explicit type casts
        cast_pattern = re.compile(r'\(\s*([a-zA-Z_]\w*(\s*\*)?)\s*\)\s*[\w()]+')

        with open(self.c_file_path, 'r') as file:
            lines = file.readlines()

        for line_number, line in enumerate(lines, start=1):
            matches = cast_pattern.findall(line)
            if matches:
                for match in matches:
                    self.explicit_casts.append((line_number, match[0])) 
        print(f"Explicit casts: {self.explicit_casts}\n")


if __name__ == "__main__":
    c_file = "../tests/test-files/medina.c"
    analyzer = CCodeAnalyzer(c_file)
    # analyzer.check_for_global_vars()
    # analyzer.check_for_magic_constants()
    # analyzer.check_long_lines()
    analyzer.check_functions_length()
    # analyzer.check_short_vars()
    # analyzer.check_explicit_casts()
    #analyzer.check_for_function_declarations()
