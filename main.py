import subprocess
import re
import inspect
import sys


class CCodeAnalyzer:
    MAX_MAIN_LENGTH = 39
    MAX_FUNCTION_LENGTH = 100
    LONG_LINE_THRESHOLD = 100
    COMMENTS_OCCURANCE_THRESHOLD = 40
    
    def __init__(self, c_file_path):
        self.c_file_path = c_file_path
        self.global_vars = self.__get_declarations("v")
        self.all_func_declaration = self.__get_declarations("f")
        self.long_lines = self.__get_long_lines()
        self.magic_constants = self.__get_magic_constants()
        self.short_vars = self.__get_short_vars()
        self.explicit_casts = self.__get_explicit_casts()
        self.too_long_functions = self.__get_functions_length()
        self.func_args_count = self.__get_count_function_arguments()
        self.comment_occurance = self.__get_comments_occurance()

    def __get_declarations(self, mode: str = "v") -> list:
        """
        Retrieves declarations of variables or functions from a C file using ctags.

        Args:
            mode (str, optional): The type of declarations to retrieve. Defaults to 'v' (variable).
                - 'v': Retrieves variable declarations.
                - 'f': Retrieves function declarations.

        Returns:
            list: A list of tuples containing the name and line number of each declaration.

        Raises:
            subprocess.CalledProcessError: If the ctags command fails.
        """
        if mode not in ["v", "f"]:
            return None

        # Use ctags to extract declarations
        command = f"ctags -x --c-kinds={mode} {self.c_file_path}"

        # Run the command and capture output
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()

        # Parse the output to extract declaration information
        declarations = []
        for line in lines:
            tokens = line.split()  # Split by whitespace
            if len(tokens) >= 3:  # Ensure there are at least 3 tokens
                name = tokens[0]  # First token (name)
                line_number = int(tokens[2])  # Third token (line number)
                declarations.append((name, line_number))
        return declarations
    
    def __get_func_len(self, start_line) -> int:
        """
        Calculates the length of a function in the C code file, starting from the given line number.

        Args:
            start_line (int): The line number where the function starts.

        Returns:
            int: The length of the function in lines.
        """
        func_length = 1
        brackets_to_close = 0
        inside_block_comment = False
        initial_bracket = False

        # Open the C code file and read all lines
        with open(self.c_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Iterate through the lines, starting from the given start line
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

            # If the brackets are closed, we've reached the end of the function
            if brackets_to_close == 0 and initial_bracket == True:
                initial_bracket = False
                break

            # Increment the function length for non-empty, non-comment lines
            func_length += 1

        return func_length
    
    def __get_functions_length(self) -> tuple[list, list]:
        """
        Calculates the length of each function in the C code and identifies functions that exceed the maximum allowed length.

        Returns:
            tuple[list, list]: A tuple containing two lists:
                - The first list contains tuples of functions that exceed the maximum allowed length, excluding the main function.
                - The second list contains tuples of the main function if it exceeds the maximum allowed length.

        Note:
            - Each tuple contains the function name, start line number, and function length.
        """
        long_funcs = []
        for func, start_line in self.all_func_declaration:
            func_length = self.__get_func_len(start_line - 1)
            if func == "main":
                if func_length >= self.MAX_MAIN_LENGTH:
                    long_funcs.append((func, start_line, func_length))
            elif func_length >= self.MAX_FUNCTION_LENGTH:
                long_funcs.append((func, start_line, func_length))
        return long_funcs
    
    def __get_magic_constants(self) -> list:
        """
        Extracts magic constants from the C code file.

        Magic constants are numeric values used in the code without clear explanation or definition.

        Returns:
            list: A list of tuples containing the magic constant value and its line number.
        """
        # Pattern for numbers (excluding 0, 1, 2) not inside string or character literals
        number_pattern = r"(?<!['\"//])\b(?!1\b|0\b|2\b)\d+\b(?!['\"//])"
        numeric_pattern = re.compile(number_pattern)  # Matches integers (excluding 0, 1, and 2)

        # Regular expression to detect string and character literals
        string_literal_pattern = r'"([^"\\]*(\\.[^"\\]*)*)"'
        char_literal_pattern = r"'([^'\\]*(\\.[^'\\]*)*)'"

        magic_constants = []
        
        with open(self.c_file_path, 'r', encoding='utf-8') as file:
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
                    magic_constants.append((match, line_number))
        return magic_constants
        
    def __get_comments_occurance(self, threshold=COMMENTS_OCCURANCE_THRESHOLD) -> list:
        """
        Identifies segments of code with a high occurrence of comments.

        Args:
            threshold (int, optional): The minimum number of uncommented lines required to consider a segment. Defaults to 40.

        Returns:
            list: A list of tuples containing the start line number and length of each segment.
        """
        with open(self.c_file_path, 'r', encoding='utf-8') as file:
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
        return segments
    
    def __get_long_lines(self) -> list:
        """
        Identifies lines in the C code file that exceed the maximum allowed length.

        Returns:
            list: A list of tuples containing the line number and length of each long line.
        """
        long_lines = []
        with open(self.c_file_path, 'r', encoding='utf-8') as file:

            for line_number, line in enumerate(file, start=1):
                if len(line) > self.LONG_LINE_THRESHOLD: 
                    long_lines.append((line_number, len(line))) 
        return long_lines
    
    def __get_short_vars(self) -> list:
    
        """
        Extracts short variable names (1 or 2 characters) from the C code file.

        Returns:
            list: A list of tuples containing the short variable name and its line number.
        """
        with open(self.c_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        short_vars = []

        # Regular expression patterns to match:
        # - Short variable names (1 or 2 characters)
        var_pattern = r'\b[a-zA-Z]{1,2}\b'
        # - Quoted strings (to exclude from variable matching)
        quote_pattern = r'(["\']).*?\1'
        # - Comments (to exclude from variable matching)
        comment_pattern = r'//.*|/\*[\s\S]*?\*/'

        # List of variables to exclude from the results
        exclude_vars = {'i', 'j', 'c', 'if', 'n'}

        inside_block_comment = False  # Flag to track if we're inside a block comment

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
                    short_vars.append((var, line_num))
        return short_vars 

    def __get_count_function_arguments(self) -> list:
        """
        Extracts the number of arguments for each function declaration in the C code file.

        Returns:
            list: A list of tuples containing the function name, line number, and argument count.
        """
        function_args_count = []

        with open(self.c_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()  # Read all lines once

        for func_name, line_number in self.all_func_declaration:
            # Ensure we are within the file's line range
            if line_number - 1 >= len(lines):  # line_number is 1-based
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
            args = self.__parse_arguments(signature)

            # Count the arguments
            function_args_count.append((func_name, line_number, len(args)))

        return function_args_count

    def __get_explicit_casts(self) -> list:
    
        """
        Extracts explicit type casts from the C code file.

        Returns:
            list: A list of tuples containing the line number, cast type, and variable name for each explicit cast.
        """
        
        # Regular expression pattern to match explicit type casts.
        # The pattern looks for parentheses around a type followed by a variable or expression.
        cast_pattern = re.compile(r'\(\s*(int|float|double|char|long|short|signed|unsigned|void)\s*\)\s*([a-zA-Z_]\w*(\s*\*)?)')

        explicit_casts = []

        # Open the C code file and read all lines
        with open(self.c_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Iterate through each line to find matches
        for line_number, line in enumerate(lines, start=1):
            # Find all matches in the line for explicit casts
            matches = cast_pattern.findall(line)
            if matches:
                # Iterate through each match and extract the line number, cast type, and variable name
                for match in matches:
                    # Append the match to the list of explicit casts
                    explicit_casts.append((line_number, match[0], match[1]))
        return explicit_casts

    def __parse_arguments(self, signature) -> list:
        """
        Parses the function signature and extracts the argument names.

        Args:
            signature (str): The function signature containing the argument types and names.

        Returns:
            list: A list of argument names, excluding 'void' and empty arguments.
        """
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
    
    def check_comments_occurance(self) -> None:
        """
        Checks if the number of comments in the code exceeds the threshold and prints an error message.

        Returns:
            None
        """
        if not self.comment_occurance:
            return
        for start_line, length in self.comment_occurance:
            additional_info = f"Number of lines without comments exceeded: {length}"
            self.print_error("ERROR", inspect.currentframe().f_code.co_name, "Without comments from", start_line, additional_info)
    
    def check_functions_length(self) -> None:
        """
        Checks if any functions in the analyzed C code exceed the maximum allowed length.

        If a function exceeds the maximum length, an error message is printed indicating the function name, start line, and the length of the function.

        :return: None
        """
        if not self.too_long_functions:
            return
        for func, start_line, func_length in self.too_long_functions:
            additional_info = f"Function length exceeded: {func_length}"
            if func == "main":
                additional_info = f"Main function length exceeded: {func_length}"
            self.print_error("ERROR", inspect.currentframe().f_code.co_name, func, start_line, additional_info)
    
    def check_magic_constants(self) -> None:
        """
        Checks for magic constants in the code and prints an error message for each magic constant found.

        Magic constants are numeric values used in the code without clear explanation or definition.

        Returns:
            None
        """
        if not self.magic_constants:
            return
        for const, line in self.magic_constants:
            self.print_error("ERROR", inspect.currentframe().f_code.co_name, const, line)
            
    def check_long_lines(self) -> None:
        """
        Checks for lines in the C code file that exceed the maximum allowed length and prints an error message for each long line.

        Returns:
            None
        """
        if not self.long_lines:
            return
        for line_num, line_length in self.long_lines:
            self.print_error("ERROR", inspect.currentframe().f_code.co_name, line_length, line_num)
    
    def check_short_vars(self) -> None:
        """
        Checks for short variable names (1 or 2 characters) in the C code file and prints an error message for each short variable found.

        Returns:
            None
        """
        if not self.short_vars:
            return
        for var, line in self.short_vars:
            self.print_error("ERROR", inspect.currentframe().f_code.co_name, var, line)
            
    def check_explicit_casts(self) -> None:
        """
        Checks for explicit type casts in the C code and prints an error message for each cast.

        Returns:
            None
        """
        if not self.explicit_casts:
            return
        for line_num, cast_type, var in self.explicit_casts:
            additional_info = f"Variable {var} is casted to {cast_type}"
            self.print_error("ERROR", inspect.currentframe().f_code.co_name, cast_type, line_num, additional_info)
    
    def check_func_args_count(self) -> None:
        """
        Checks the number of arguments in each function and prints a warning 
        if the number of arguments is greater than or equal to 6 or equal to 0.

        Returns:
            None
        """
        if not self.func_args_count:
            return
        for func_name, line, args_count in self.func_args_count:
            if args_count >= 6 or args_count == 0:
                self.print_error("WARNING", inspect.currentframe().f_code.co_name,
                                func_name, line)
                print(f"Are you sure, that much args({args_count}) needed?\n")
        
    def check_for_global_vars(self) -> None:
        """
        Checks for global variables in the code and prints a warning for each global variable found.

        Returns:
            None
        """
        if not self.global_vars:
            return
        for global_var, line in self.global_vars:
            self.print_error("WARNING", inspect.currentframe().f_code.co_name,
                            global_var, line)
    
    def print_error(self, mode, func_that_checked, var_print, line_print, additional_info = "") -> None:
        """Fancy printing for error

        Args:
            mode (string): Mode in string
            func_that_checked (string): what func checked it
            var_print (string): variable to print
            line_print (int): line in which error was found
            additional_info (string, optional): Additional info. Defaults to "".
        
        """
        print(f"[{mode}] [{func_that_checked}] found: {var_print} at Line: {line_print}, {additional_info}")
    
    def analyze(self) -> None:
        """
        Analyzes the C code file and prints out the results.

        Returns:
            None
        """
        self.check_for_global_vars()
        self.check_magic_constants()
        self.check_long_lines()
        self.check_short_vars()
        self.check_explicit_casts()
        self.check_functions_length()
        self.check_comments_occurance()
        self.check_func_args_count()
        

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_c_file>")
        return
    
    c_file = sys.argv[1]
    analyzer = CCodeAnalyzer(c_file)
    analyzer.analyze()

if __name__ == "__main__":
    main()
