import subprocess
import re
import inspect

class CCodeAnalyzer:
    MAX_MAIN_LENGTH = 30
    MAX_FUNCTION_LENGTH = 100
    
    def __init__(self, c_file_path):
        self.c_file_path = c_file_path
        self.global_vars = self.__get_declarations("v")
        self.long_rows = []
        self.magic_constants = []
        self.short_vars = []
        self.explicit_casts = []
        self.all_func_declaration = self.__get_declarations("f")
        self.bad_functions = []
        self.main_info = []
        self.func_args_count = self.__get_count_function_arguments()

    def __get_declarations(self, mode = "v") -> list:
        """_summary_

        Args:
            mode (str, optional): find v = variable, f = function. Defaults to 'v'.

        Returns:
            list: _description_
        """
        if mode != "v" and mode != "f":
            return None
        
        #   Using ctags, don't want to think mich
        command = f"ctags -x --c-kinds={mode} {self.c_file_path}"

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
    
    def __get_function_length(self, start_line):
        func_length = 1
        brackets_to_close = 0
        inside_block_comment = False
        initial_bracket = False
        with open(self.c_file_path, 'r') as f:
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
            
            func_length += 1    

            # Only increment the function length for non-empty, non-comment lines
        return func_length

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
    
    def check_functions_length(self):
        for func, start_line in self.all_func_declaration:
            func_length = self.__get_function_length(start_line-1)
            if func != "main":
                if func_length >= self.MAX_FUNCTION_LENGTH:
                    self.bad_functions.append((func, start_line, func_length))
            elif func == "main":
                if func_length >= self.MAX_MAIN_LENGTH:
                    self.main_info.append((func, start_line, func_length))
        
        print(f"Functions are too long{self.bad_functions}\n")
        
        if self.main_info:
            print(f"Main exceed max length{self.main_info}\n")
    
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

    def check_comments_in_c_file(self, threshold=40):  
        with open(self.c_file_path, 'r') as file:
            lines = file.readlines()

        lines_without_comments = 0
        start_line = None
        segments = []

        for i, line in enumerate(lines):
            stripped_line = line.strip()

            # Skip empty lines
            if not stripped_line:
                continue

            # Check if the line contains a comment
            if stripped_line.startswith('//') or '/*' in stripped_line or '*/' in stripped_line:
                # Record segment if it meets the threshold
                if lines_without_comments >= threshold:
                    segments.append((start_line + 1, lines_without_comments))
                lines_without_comments = 0
                start_line = None
            else:
                # Start a new uncommented segment if needed
                if lines_without_comments == 0:
                    start_line = i
                lines_without_comments += 1

        # Add final segment if it meets the threshold
        if lines_without_comments >= threshold:
            segments.append((start_line + 1, lines_without_comments))

        # Output results
        if segments:
            average_length = sum(count for _, count in segments) / len(segments)
            print(f"Large code segments without comments ({threshold} or more lines) found:")
            for start, count in segments:
                print(f"Start Line: {start}, Lines without comments: {count}")
            print(f"\nTotal segments: {len(segments)}")
            print(f"Average lines per segment: {average_length:.2f}")
        else:
            print(f"No large segments with {threshold} or more lines without comments.")
        
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

    def check_long_lines(self):
        with open(self.c_file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                if len(line) > 100: 
                    self.long_rows.append((line_number, len(line))) 
        print(f"Long rows: {self.long_rows}\n") 
    
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
                    self.short_vars.append((var, line_num))
        print(f"Short vars: {self.short_vars}\n")
    
    def check_explicit_casts(self):
        # Regular expression pattern to match explicit type casts.
        # The pattern looks for parentheses around a type followed by a variable or expression.
        cast_pattern = re.compile(r'\(\s*(int|float|double|char|long|short|signed|unsigned|void)\s*\)\s*([a-zA-Z_]\w*(\s*\*)?)')

        self.explicit_casts = []

        with open(self.c_file_path, 'r') as file:
            lines = file.readlines()

        # Go through each line to find matches
        for line_number, line in enumerate(lines, start=1):
            # Find all matches in the line for explicit casts
            matches = cast_pattern.findall(line)
            if matches:
                for match in matches:
                    # Append the match (line_number, cast type, variable) to the list
                    self.explicit_casts.append((line_number, match[0], match[1]))

        # Print out all found explicit casts
        if self.explicit_casts:
            print(f"Explicit casts found in {self.c_file_path}:")
            for line_number, cast_type, variable in self.explicit_casts:
                print(f"Line {line_number}: Cast type '{cast_type}' on variable '{variable}'")
        else:
            print(f"No explicit casts found in {self.c_file_path}.")
    
    
    def check_func_args_count(self):
        for func, args_count in self.func_args_count:
            if args_count == 0:
                print(f"Be careful, {func} has {args_count} args. Is it generator?")
            elif args_count >= 5:
                print(f"Be careful, {func} has {args_count} args. Is it much?")
    
    def __get_count_function_arguments(self):
        # Get the list of function declarations (name and line number)
        function_args_count = []

        with open(self.c_file_path, 'r') as file:
            lines = file.readlines()  # Read all lines once

        for func_name, line_number in self.all_func_declaration:
            # Ensure we are within the file's line range
            if line_number - 1 >= len(lines):  # line_number is 1-based
                print(f"Warning: Line {line_number} is out of range in the file.")
                continue

            # Get the specific line where the function is declared
            func_line = lines[line_number - 1].strip()  # Adjust to 0-based index

            # If the signature is split across multiple lines, join them together
            while not func_line.endswith(')'):  # Keep reading lines until we get the closing parenthesis
                line_number += 1
                if line_number - 1 >= len(lines):  # Check if next line exists
                    #print(f"Warning: Line {line_number} is out of range in the file.")
                    break
                func_line += lines[line_number - 1].strip()

            # Extract the function signature (content between parentheses)
            signature = func_line.split('(')[1].split(')')[0]  # Get content between '(' and ')'
            
            # Handle complex argument types like arrays and pointers
            args = self._parse_arguments(signature)

            # Count the arguments
            function_args_count.append((func_name, line_number, len(args)))

        return function_args_count

    def _parse_arguments(self, signature):
        # Split by commas to count arguments (ignoring empty spaces and 'void')
        args = []
        current_arg = ""
        inside_parentheses = 0

        for char in signature:
            if char == ',' and inside_parentheses == 0:
                if current_arg.strip():  # Add non-empty arguments
                    args.append(current_arg.strip())
                current_arg = ""
            else:
                if char == '(':
                    inside_parentheses += 1
                elif char == ')':
                    inside_parentheses -= 1
                current_arg += char

        if current_arg.strip():  # Add last argument
            args.append(current_arg.strip())

        # Ignore 'void' arguments
        return [arg for arg in args if arg != 'void' and arg.strip()]
    def check_func_args_count(self):
        if not self.func_args_count:
            return
        for func_name, line, args_count in self.func_args_count:
            if args_count >= 6 or args_count == 0:
                self.print_error("WARNING",inspect.currentframe().f_code.co_name,
                                 func_name, line)
                print(f"Are you sure, that much args({args_count}) needed?")
    
    def check_for_global_vars(self):
        if not self.global_vars:
            return
        print("[GLOBAL VAR] Be careful, found global var")
        for global_var, line in self.global_vars:
            self.print_error("WARNING", inspect.currentframe().f_code.co_name,
                             global_var, line)
    
    
    def print_error(self, mode, func_that_checked, var_print, line_print):
        """Fancy printing for error

        Args:
            mode (string): Mode in string
            func_that_checked (string): what func checked it
            var_print (string): variable to print
            line_print (int): line in which error was found
        """
        print(f"[{mode}][{func_that_checked}] found: {var_print} at Line: {line_print}")
        
            


if __name__ == "__main__":
    c_file = "../tests/test-files/medina.c"
    analyzer = CCodeAnalyzer(c_file)
    analyzer.check_for_global_vars()
    analyzer.check_for_magic_constants()
    analyzer.check_long_lines()
    analyzer.check_short_vars()
    analyzer.check_explicit_casts()
    analyzer.check_functions_length()
    analyzer.check_comments_in_c_file()
    analyzer.check_func_args_count()

