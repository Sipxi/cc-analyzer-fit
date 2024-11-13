#include <stdio.h>
#include <string.h>
#include <ctype.h>

// Creating an array to match numbers and letters
char *digit_array[] = {
  "0+", "1", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"
};

// Check if the symbol "a" matches the entered digit or number
int matches_digit(char a, char digit) {
  if (!(digit >= '0' && digit <= '9')) {
    return 0;
  }
  a = tolower(a); // convert a character to lower case
  int digit_index = digit - '0'; // calculation of digit_index, which is needed to determine the character string in digit_array
  return strchr(digit_array[digit_index], a) != NULL; // check if character 'a' is in string digit_array[digit_index] if character 'a' is found return 1
}

// Searches the string "name" for a sequence of characters that are in "criterion"
int matches_name(char *name, char *criterion) {
  int len_name = strlen(name);
  int len_criterion = strlen(criterion);

  for (int index = 0; index <= len_name - len_criterion; index++) {
    // inside each pass of the main loop match = 1 is set, when checking the function matches_digit if the symbol does not match "match" is set to 0 and abort
    int match = 1; 
    for (int index2 = 0; index2 < len_criterion; index2++) { 
      if (!matches_digit(name[index + index2], criterion[index2])) { 
        match = 0;
        break;
      }
    }
    if (match) { // if the sequence is not interrupted, it will output 1, indecating that a "match" was found
      return 1;
    }
  }
  return 0;
}

// Searches the string "phone" for a sequence of characters that are in "criterion"
int matches_phone_number(char *phone, char *criterion) {
  int len_phone = strlen(phone);
  int len_criterion = strlen(criterion);

  for (int index = 0; index <= len_phone - len_criterion; index++) {
    int match = 1;
    for (int index2 = 0; index2 < len_criterion; index2++) {
      if (phone[index + index2] != criterion[index2]) {
        // checking additional criterion if "phone" is + and "criterion" is 0, then match remains 1
        if (!(phone[index + index2] == '+' && criterion[index2] == '0')) { 
          match = 0;
          break;
        }
      }
    }
    if (match) {
      return 1;
    }
  }
  return 0;
}

int main (int argc, char *argv[]) {
  int max_contact = 100;
  int max_lenght = 102;
  char contacts[max_contact][2][max_lenght];
  int contact_count = 0;
  char line[max_lenght];

  while (fgets(line, sizeof(line), stdin)) {
    line[strcspn(line, "\n")] = '\0'; // removes the newline character
    if ((int)strlen(line) >= max_lenght) { //Check that the line does not exceed 100 symbol
      fprintf(stderr, "First or last name is very long, line should not exceed 100 characters\n");
      return 1;
    }
    strcpy(contacts[contact_count][0], line);

    if (fgets(line, sizeof(line), stdin)) {
      line[strcspn(line, "\n")] = '\0';
      if ((int)strlen(line) >= max_lenght) { //Check that the line does not exceed 100 symbol
      fprintf(stderr, "First or last name is very long, line should not exceed 100 characters\n");
      return 1;
      }
      strcpy(contacts[contact_count][1], line);
      contact_count++;
    }
  }
  int found = 0;
  char *criteria;

  if (argc > 1){
    // check with the command "strspn", if all characters are digits
    if (argc == 2) {
      if (strspn(argv[1], "0123456789") == strlen(argv[1])) { 
        criteria = argv[1];
      }
      else {
        fprintf(stderr, "Argument must be all digit\n");
        return 1;
      }
    }
    else {
      fprintf(stderr, "Too many arguments\n");
      return 1;
    }
  }
  else{
    criteria = "";
  }


  // Finding and displaying matches
  for (int index = 0; index < contact_count; index++) {
    int match_name = matches_name(contacts[index][0], criteria);
    int match_phone = matches_phone_number(contacts[index][1], criteria);

    if (match_name || match_phone) {
      printf("%s, %s\n", contacts[index][0], contacts[index][1]);
      found = 1;
    }
  }
  if (!found) {
    printf("Not found\n");
    return 0;
  }

  return 0;
}