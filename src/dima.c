#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

typedef struct {
    char name[102];
    char phone[102];
} Contact;

bool readContact(Contact *contact) {
    if (fgets(contact->name, sizeof(contact->name), stdin) == NULL) {
    return false;
    }
    contact->name[strcspn(contact->name, "\n")] = '\0';
    if (fgets(contact->phone, sizeof(contact->phone), stdin) == NULL) {
        return false;
    }
    contact->phone[strcspn(contact->phone, "\n")] = '\0';
    return strlen(contact->name) > 0 && strlen(contact->phone) > 0;
}

bool matchContact(const Contact *contact, const char *search) {
    const char *mapping[] = {
        "+", 
        "", 
        "abc",
        "def", 
        "ghi",
        "jkl",
        "mno",
        "pqrs",
        "tuv",
        "wxyz"
    };

    size_t searchLen = strlen(search);
    for (size_t i = 0; i <= strlen(contact->name) - searchLen; i++) {
        bool match = true;
        for (size_t j = 0; j < searchLen; j++) {
            char c = tolower(contact->name[i + j]);
            if (!strchr(mapping[search[j] - '0'], c)) {
                match = false;
                break;
            }
        }
        if (match) return true;
    }

    for (size_t i = 0; i <= strlen(contact->phone) - searchLen; i++) {
        bool match = true;
        for (size_t j = 0; j < searchLen; j++) {
            char c = contact->phone[i + j];
            if (!strchr(mapping[search[j] - '0'], c)) {
                match = false;
                break;
            }
        }
        if (match) return true;
    }

    return false;
}

int main(int argc, char *argv[]) {
    if (argc > 2) {
        fprintf(stderr, "Error: Too many arguments\n");
        return 1;
    }

    if (argc == 2) {
        for (size_t i = 0; i < strlen(argv[1]); i++) {
            if (!isdigit(argv[1][i])) {
                fprintf(stderr, "Error: Argument contains non-digit characters\n");
                return 1;
            }
        }
    }

    bool matchFound = false;
    Contact contact;

    while (readContact(&contact)) {
        if (argc == 1 || matchContact(&contact, argv[1])) {
            printf("%s, %s\n", contact.name, contact.phone);
            matchFound = true;
        }
    }

    if (!matchFound) {
        printf("Not Found\n");
    }

    return 0;
}