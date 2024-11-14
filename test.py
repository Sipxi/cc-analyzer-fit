import re

def check_struct_variable_naming(c_file_content):
    # Regex pattern to find typedef struct declarations and their contents
    struct_pattern = r'typedef\s+struct\s*\{([^}]+)\}\s*(\w+);'
    
    # Regex patterns for camelCase (first letter uppercase) and snake_case (all lowercase with underscores)
    camel_case_pattern = r'\b[A-Z][a-zA-Z0-9]*\b'
    snake_case_pattern = r'\b[a-z_]+\b'

    # Find all typedef struct blocks and their content
    structs = re.findall(struct_pattern, c_file_content)

    for struct_content, struct_name in structs:
        print(f"Checking struct: {struct_name}")
        
        # Find all variables inside the struct (i.e., names before the array sizes or semicolons)
        struct_vars = re.findall(r'\s*(\w+)\s*\[', struct_content)  # Match variable names before '['

        for var in struct_vars:
            if re.match(camel_case_pattern, var):
                print(f'  {var} follows CamelCase style (uppercase first letter).')
            elif re.match(snake_case_pattern, var):
                print(f'  {var} follows snake_case style (all lowercase with underscores).')
            else:
                print(f'  {var} does not follow the standard naming conventions.')

# Example usage with the C code
c_code = """
typedef struct{
    char name[MAX_CONTACT_INFO_LENGTH];
    char number[MAX_CONTACT_INFO_LENGTH];
} contact;

typedef struct{
    char name[MAX_CONTACT_INFO_LENGTH];
    char number[MAX_CONTACT_INFO_LENGTH];
} Contact;

typedef struct{
    char name[MAX_CONTACT_INFO_LENGTH];
    char number[MAX_CONTACT_INFO_LENGTH];
} contact_t;

typedef struct{
    char name[MAX_CONTACT_INFO_LENGTH];
    char number[MAX_CONTACT_INFO_LENGTH];
} contact_thelp;

typedef struct{
    int id;
    char description[100];
} product;
"""

check_struct_variable_naming(c_code)
