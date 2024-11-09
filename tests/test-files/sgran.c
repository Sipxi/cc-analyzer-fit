/*
 * Project: T nine
 * Author:  Behari Youssef
 * Date:    21 October 2024
 * Version: 1.0
 *
 * Description:
 * T9 algorithm analog. Finding data in contacts by 9 numbers.
 */
#include <stdio.h>
#include <string.h>
#include <ctype.h>

#define MAX_LENGTH 101
#define MAX_CONTACTS 50

/*
 * Structure, describes contact entity.
 * Each contact contains name, phone and coded name.
*/
typedef struct contact {
    char name[MAX_LENGTH];
    char phone_number[MAX_LENGTH];
    char name_coded[MAX_LENGTH];
} Contact;

/*
 * Function, which sets each letter in string to lower
*/
void to_lower_case(char *str) {
    for (int str_idx = 0; str_idx < (int)strlen(str); str_idx++) {
        str[str_idx] = tolower(str[str_idx]);
    }
}

/*
 * Function, which codes name, using t9 table
*/
void code_name(char *name, char *coded) {
    char table[][5] = {"", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"};
    int coded_count = 0;
    for (int name_idx = 0; name_idx < (int)strlen(name); name_idx++) {
        for (int table_idx = 0; table_idx < (int)(sizeof(table)/sizeof(table[0])); table_idx++) {
            if (strchr(table[table_idx], name[name_idx])) {
                coded[coded_count] = table_idx + '0';
                coded_count++;
            }
        }
    }
}

/*
 * Deletes 0 from criteria, for searching in names
*/
void clear_criteria(char *criteria, char *new_criteria, int crit_len) {
    int new_crit_idx = 0;
    for (int crit_idx = 0; crit_idx < crit_len; crit_idx++) {
        if (criteria[crit_idx] != '0') {
            new_criteria[new_crit_idx] = criteria[crit_idx];
            new_crit_idx++;
        }
    }
}

/*
 * Searchs by criterition in name, and phone in each contact in contacts array.
*/
int search_contact(Contact contacts[], int contacts_lenght, char* criteria) {
    Contact fnd_contacts[MAX_CONTACTS];
    char cleared_crit[MAX_LENGTH] = "";
    clear_criteria(criteria, cleared_crit, (int)strlen(criteria));

    int fnd_count = 0;
    for (int iterator = 0; iterator < contacts_lenght; iterator++) {
        if (criteria[0] == '0') {criteria[0] = '+';}
        if (strstr(contacts[iterator].phone_number, criteria) || strcmp(criteria, "-1") == 0) {
            strcpy(fnd_contacts[fnd_count].name, contacts[iterator].name);
            strcpy(fnd_contacts[fnd_count].phone_number, contacts[iterator].phone_number);
            fnd_count++;
            continue;
        }
        if (strstr(contacts[iterator].name_coded, cleared_crit)) {
            strcpy(fnd_contacts[fnd_count].name, contacts[iterator].name);
            strcpy(fnd_contacts[fnd_count].phone_number, contacts[iterator].phone_number);
            fnd_count++;
        }
    }

    if (!fnd_count) {
        printf("Not found\n");
        return 0;
    }

    for (int fnd_inx = 0; fnd_inx < fnd_count; fnd_inx++) {
        printf("%s, %s\n", fnd_contacts[fnd_inx].name, fnd_contacts[fnd_inx].phone_number);
    }
    return 1;
}

/*
 * Entery point, reads from stdin, writes data to contacts list, calls search.
*/
int main(const int argc, char** argv) {
    char temp[MAX_LENGTH+1];
    Contact contacts[MAX_CONTACTS];

    int added_contacts = 0;
    int iterator = 0;

    while (scanf("%102[^\n]%*c", temp) == 1) {
        to_lower_case(temp);
        if (strlen(temp) > 101) {
            printf("Too long\n");
            break;
        }
        if (!iterator) {
            code_name(temp, contacts[added_contacts].name_coded);
            strcpy(contacts[added_contacts].name, temp);
            iterator = 1;
        }
        else {
            strcpy(contacts[added_contacts].phone_number, temp);
            added_contacts++;
            iterator = 0;
        }
    }

    if (argc == 2) {
        for (int crit_idx = 0; crit_idx < (int)strlen(argv[1]); crit_idx++) {
            if (!isdigit(argv[1][crit_idx])) {
                fprintf(stderr, "Criteria is not digit\n");
                return 1;
            }
        }
        search_contact(contacts, added_contacts, argv[1]);
    }
    else if (argc == 1) {
        search_contact(contacts, added_contacts, "-1");
    }
    else {
        fprintf(stderr, "Too many arguments\n");
        return 1;
    }
    return 0;
}
