#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>
char phone_digits[29] = {
    '0', // +
    '2', '2', '2', // a, b, c
    '3', '3', '3', // d, e, f
    '4', '4', '4', // g, h, i
    '5', '5', '5', // j, k, l
    '6', '6', '6', // m, n, o
    '7', '7', '7', '7', // p, q, r, s
    '8', '8', '8', // t, u, v
    '9', '9', '9', '9', // w, x, y, z
};
// This is an array of digits, where each value stands for a corresponding letter in the alphabet.


void letters_to_digits(const char *name, char *result) {
    int i=0, j=0;
    while (name[i] != '\0') {
        if (isalpha(name[i])) {
            result[j++] = phone_digits[tolower(name[i]) - 'a' + 1];
        } else if (isdigit(name[i])) {
            result[j++] = name[i];
            
        } else if (name[i] == '0' || name[i] == '+') {
            result[j++] = '0';
        }
        i++;
    }
    result[j] = '\0';
}
// This function takes string symbol by symbol and checks whether it is a letter. 
// If so, the letter is converted into a number and added into a new array.
// If not, the number itself is added into a new array.
// '+' is converted into '0'.

void read_str(char *str) {
    scanf( " %[^\n]", str);
}
// This function reads string from standard input.

int is_num(char *arg){
    char str[101];
        strcpy(str, arg);
    for (unsigned int i = 0; i < strlen(arg); i++) {
        if (!isdigit(str[i])) {
            fprintf(stderr, "error");
            return 1;
        }
    }
    return 0;
}
// This function is meant to check if the symbols are numbers.

int main(int arg_c, char *arg_v[]) {

    char name[2048];
    name[0] = '\0'; 
    char *digits_input; 
    char phone[2048]; 
    phone[0] = '\0'; 
    char name_in_digits[2048];
    // Storage of the contact's name converted into digits.
    char phone_in_digits[2048];
    // Storage of the contact's phone number converted into digits (to make sure '+' is included).
    name_in_digits[0] = '\0';
    
    if (arg_c > 1) {
       if (is_num(arg_v[1]) == 1) {
        return 1;
        }  
    }
    // This statement checks that the input sympols are numbers.

    if (arg_c > 2) {
        fprintf(stderr, "\n");
        return 1;
    }
    // This statement sends an error message if the maximum number of input arguments is exceeded.
    
    digits_input = arg_v[1];

    int count = 0; 
    // This variable is going to indicate the number of found strings.

    while (scanf( " %[^\n]", name) != EOF) {

        if (strlen(name) == 0) {
            break;
        }
        // Name is read. If the string is empty, loop is exited.

        read_str(phone);
        
        if (strlen(phone) == 0) {
            break;
        }
        // Phone number is read. If the string is empty, loop is exited.

        letters_to_digits(name, name_in_digits);

        letters_to_digits(phone, phone_in_digits);

        if (arg_c == 1) {
            printf("%s, %s\n", name, phone);
            count = 1;
            continue;
        }
        // If an empty string is read, all the contacts are printed.

        if (strstr(name_in_digits, digits_input) != NULL || strstr(phone_in_digits, digits_input) != NULL) {
            printf("%s, %s\n", name, phone);
            count++;            
        }
        // This statement checks, if numbers read from stdin are a substring of any string in list.
        // If so, the corresponding strings are printed.
        
        if (strstr(name_in_digits, digits_input) == NULL && strstr(phone_in_digits, digits_input) == NULL) {
            continue;
        }
        // If no matches are in input string and contacts, cycle goes on untill end of file,
        // then breaks. 
    }
    if (count == 0) {
        printf("Not found");
    }
    // This condition is implemented when no matches have been found.

    return 0;    
}    
    
    
        
        
   

    
    
    
