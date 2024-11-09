/**
 * @file tnine.c
 * @author Yelysei Podolskyi (xpodol07@vutbr.cz)
 * @brief
 * Program, který emuluje zjednodušený algoritmus hledání kontaktů zadaných pomocí posloupnosti číslic.
 * Vstupem programu je posloupnost číslic.
 * Výstup programu obsahuje seznam kontaktů, které odpovídají zadanému číselnému filtru.
 * @version 1.2
 * @date 2024-10-20
 *
 * @copyright Copyright (c) 2024
 *
 */

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAX_CONTACT_LENGTH 102  // Maximum length for both contact name and phone number

// Enum representing the result of reading a contact
typedef enum {
    READERR,
    NO_CONTACT,
    READ_SUCCESS
} ReadResult;

// Struct to hold contact details (name and phone number)
typedef struct
{
    char name[MAX_CONTACT_LENGTH];
    char phone[MAX_CONTACT_LENGTH];
} Contact;

/**
 * @brief Check if a string consists only of digits.
 *
 * @param ch Pointer to the string to check.
 * @return bool - true If the string contains only digits. false If the string contains non-digit characters.
 */
bool isNum(char *ch) {
    for (int i = 0; ch[i] != '\0'; i++) {
        if (!isdigit(ch[i])) {
            return false;  // if any non-digit character is found
        }
    }
    return true;  // All characters are digits
}

/**
 * @brief Check if the line exceeds a certain length and handle the newline character.
 *
 * @param line The string to check.
 * @param n The maximum allowed length (including null terminator).
 * @return bool - true If the line exceeds the length limit. false If the line is within the limit.
 */
bool isLineOverflow(char *line, int n) {
    int len = strlen(line);

    if (len == n - 1 && line[len - 1] != '\n') {  // check if I have length of line equal to 101 because last char must be '\n'
        return true;
    }
    if (line[len - 1] == '\n') {
        line[len - 1] = '\0';
    }

    return false;
}

/**
 * @brief Custom improved fgets function that skips empty lines.
 *
 * @param str Buffer to store the read string.
 * @param n Maximum number of characters to read.
 * @param f File stream to read from.
 * @return char* Pointer to the string read, or NULL on EOF.
 */
char *ffgets(char *str, int n, FILE *f) {
    char *p;
    while ((p = fgets(str, n, f)) != NULL && str[0] == '\n');
    return p;
}

/**
 * @brief Check if a given numeric string (T9 digits) matches any substring in the contact's name or phone number.
 * AKA checking if a string str2 is in str1
 *
 * @param str1 The string to search in (e.g., contact name or phone).
 * @param str2 The numeric string to search for (based on T9 mapping).
 * @return bool - false If no match is found, true If the numeric string matches part of the contact string.
 */
bool isSubstring(char *str1, char *str2) {
    char map[10][6] = {
        "0+",
        "1",
        "2abc",
        "3def",
        "4ghi",
        "5jkl",
        "6mno",
        "7pqrs",
        "8tuv",
        "9wxyz"};

    int str_len = strlen(str1);
    int substr_len = strlen(str2);

    // Loop through the contact string and attempt to match the numeric string
    for (int i = 0; i <= str_len - substr_len; i++) {
        int j;

        // Compare characters in str1 with the corresponding T9 mappings of str2
        for (j = 0; j < substr_len; j++) {
            int ch_num = str2[j] - '0';          // Convert digit character to integer
            char *variant = map[ch_num];         // Get the T9 mapping for this digit
            int variants_len = strlen(variant);  // Number of possible letters for this digit
            bool found = false;

            // Check if the current character in str1 matches any of the letters for the digit in str2
            for (int k = 0; k < variants_len; k++) {
                if (tolower(str1[i + j]) == tolower(variant[k])) {
                    found = true;
                    break;  // Exit inner loop if a match is found
                }
            }

            // If no match was found for this character, exit the comparison loop
            if (!found) {
                break;
            }
        }

        // If the entire substring matches, return true
        if (j == substr_len) {
            return true;
        }
    }
    return false;  // No match found
}

/**
 * @brief Read a contact's name and phone number from stdin.
 *
 * @param contact Pointer to a Contact struct to store the read data.
 * @return ReadResult The result of the read operation (success, error, or end of input).
 */
ReadResult readContact(Contact *contact) {  // int - ReadResult   (every enum)
    if (ffgets(contact->name, sizeof(contact->name), stdin) == NULL) {
        return NO_CONTACT;  // No more contacts to read (EOF reached)
    };

    // Check if the name exceeds the length limit
    if (isLineOverflow(contact->name, sizeof(contact->name))) {
        return READERR;
    }

    if (ffgets(contact->phone, sizeof(contact->phone), stdin) == NULL) {
        return READERR;  // Reading error (e.g., EOF or invalid input)
    };

    // Check if the phone number exceeds the length limit
    if (isLineOverflow(contact->phone, sizeof(contact->phone))) {
        return READERR;
    }
    return READ_SUCCESS;
}

/**
 * @brief Main function to handle input, process contacts, and perform contact search.
 *
 * @param argc Number of command line arguments.
 * @param argv Array of command line arguments.
 * @return int Exit code (0 for success, 1 for error).
 */
int main(int argc, char *argv[]) {
    char *arg = NULL;  // Stores the optional search argument (numeric filter)

    // Validate the number of command-line arguments
    if (argc > 2) {
        fprintf(stderr, "Invalid argument\n");
        return 1;
    } else if (argc == 2) {
        if (!isNum(argv[1])) {
            fprintf(stderr, "Error: Argument should be a number\n");
            return 1;
        }
        arg = argv[1];  // Store the search filter
    }
    ReadResult result;
    Contact contact;
    int counter = 0;  // Count the number of matching contacts (succeeded printf in loop while)

    while (1) {
        result = readContact(&contact);
        if (result == NO_CONTACT) {
            break;  // Exit the loop when there are no more contacts to read
        } else if (result == READERR) {
            fprintf(stderr, "Failed to read contact\n");
            return 1;  // Exit with an error code if there was a read error
        }

        // If no filter is provided, or if the name or phone matches the filter, print the contact
        if (arg == NULL || isSubstring(contact.name, arg) || isSubstring(contact.phone, arg)) {
            printf("%s, %s\n", contact.name, contact.phone);
            counter++;
        }
    }

    // If a filter was provided but no contacts matched, print "Not found"
    if (arg != NULL && counter == 0) {
        printf("Not found\n");
    }

    return 0;
}
