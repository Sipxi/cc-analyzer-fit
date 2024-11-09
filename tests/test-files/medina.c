#include <stdio.h>
#include <string.h>

struct contact_list
{
    // 100 + '\0'
    char name[101];
    char number[101];
};

int is_valid_user_input(char user_input[102]);

// Ziskani kontaktu ze stdin, kontrola spravnosti dat
int find_contacts(char mode, char user_input[102]);

// Pripravit kontaktni udaje, vyhledat 1 shodu -> spustit rekurzivni funkce
int tnine_solver(char mode, char user_input[102], struct contact_list contact_book);

// Rekurzivni funkce pro vyhledani posloupnosti znaku
int is_next_matching(int user_input_step, int contact_book_step,
                     char user_input[102], char book_name_or_number[101],
                     int user_input_lenght, int contact_length);

// Rekurzivni funkce pro vyhledani prerusene posloupnosti znaku
int is_any_matching(int user_input_step, int contact_book_step,
                     char user_input[102], char book_name_or_number[101],
                     int user_input_lenght, int contact_length);

int main(int argc, char* argv[])
{
    char* user_input;
    int valid_input, valid_find;
    int argument_length;

    if(argc > 3)
    {
        // 2, protoze uzivatel nevidi nulovy argument
        fprintf(stderr, "ERROR code 21, input %i args., max number of args. is 2.\n", argc);
        return 21;
    }

    if(argc == 3)
    {
        argument_length = strlen(argv[1]);
        if(argument_length != 2)
        {
            fprintf(stderr,"ERROR code 27, the argument: %s length must be: 2 \n", argv[1]);
            return 27;
        }
        if(argv[1][0] != '-' || argv[1][1] != 's')
        {
            fprintf(stderr,"ERROR code 28, the argument: %s can only be: -s \n", argv[1]);
            return 28;
        }

        user_input = argv[2];
        valid_input = is_valid_user_input(user_input);
        if(valid_input != 0)
        {
            return valid_input;
        }

        valid_find = find_contacts('s', user_input);
        if(valid_find != 0)
        {
            return valid_find;
        }
    }

    if(argc == 2)
    {
        user_input = argv[1];
        valid_input = is_valid_user_input(user_input);
        if(valid_input != 0)
        {
            return valid_input;
        }

        valid_find = find_contacts('f', user_input);
        if(valid_find != 0)
        {
            return valid_find;
        }
    }

    if(argc == 1)
    {
        char empty_string[102] = "";
        find_contacts('a', empty_string);
    }

    return 0;
}


int is_valid_user_input(char user_input[102])
{
    int user_input_length;
    user_input_length = strlen(user_input);
    if(user_input_length > 100)
    {
        fprintf(stderr,"ERROR code 22, user input string length is longer than 100.\n");
        return 22;
    }
    for(int i=0; i < user_input_length; i++)
    {
        // Cislo obsahuje pouze cisla
        if(user_input[i]  < 48  ||
           user_input[i]  > 57)
        {
            fprintf(stderr, "ERROR code 24, the user input: %s", user_input);
            fprintf(stderr, " must consist of 0...9 \n");
            return 24;
        }
    }
    return 0;
}


// Dostupne mody: 'a' = vytahnout kazdy kontakt;
//                'f' = vystup kazdeho kontaktu posloupnosti znaku user_input
//                's' = vystup kazdeho kontaktu prerusene posloupnosti znaku user_input
int find_contacts(char mode, char user_input[102])
{
    struct contact_list contact_book;

    // Cekani na dokonceni cteciho cyklu NULL
    char* name_fgets_end = 0;
    char* number_fgets_end = 0;
    
    // 103 protoze konec by mohl byt '\n' '\r' '\0'.
    char name_raw_input[103];
    char number_raw_input[103];
    int name_raw_length;
    int number_raw_length;

    int contact_name_length;
    int contact_number_length;

    int valid_tnine;
    int valid_tnine_counter = 0;

    // V kazdem kroku cyklu se precte a zkontroluje 1 kontakt (jmeno a cislo).
    while(1)
    {
        name_fgets_end = fgets(name_raw_input, sizeof(name_raw_input), stdin);
        number_fgets_end = fgets(number_raw_input, sizeof(number_raw_input), stdin);
        
        // Dokoncit cteni souboru, pokud jiz nejsou zadne dalsi radky ke cteni.
        if(name_fgets_end == NULL)
        {
            break;
        }

        if(number_fgets_end == NULL)
        {
            fprintf(stderr, "ERROR code 23, the last contact");
            fprintf(stderr, " doesn't have a number\n");
            return 23;
        }

        name_raw_length = strlen(name_raw_input);
        number_raw_length = strlen(number_raw_input);

        //Pokud je vstup z textoveho souboru a radky jsou oddeleny znakem \r\n
        if(name_raw_input[name_raw_length-1] == 10 &&
           name_raw_input[name_raw_length-2] == 13)
        {
            for(int i=0; i < name_raw_length-2; i++)
            {
                contact_book.name[i] = name_raw_input[i];
            }
            contact_book.name[name_raw_length-2] = '\0';
        }
        if(name_raw_input[name_raw_length-1] == 10 &&
           name_raw_input[name_raw_length-2] != 13)
        {
            if(name_raw_length > 101)
            {
                fprintf(stderr, "ERROR code 33, Incorrect Data: name ");
                fprintf(stderr, "must not be greater than 100 characters\n");
                return 33;
            }
            for(int i=0; i < name_raw_length-1; i++)
            {
                contact_book.name[i] = name_raw_input[i];
            }
            contact_book.name[name_raw_length-1] = '\0';
        }
        if(name_raw_input[name_raw_length-1] != 10 &&
           name_raw_input[name_raw_length-2] != 13)
        {
            fprintf(stderr, "ERROR code 32, Input Overflow: name ");
            fprintf(stderr, "must not be greater than 100 characters\n");
            return 32;
        }
        
        if(number_raw_input[number_raw_length-1] == 10 &&
           number_raw_input[number_raw_length-2] == 13)
        {
            for(int i=0; i < number_raw_length-2; i++)
            {
                contact_book.number[i] = number_raw_input[i];
            }
            contact_book.number[number_raw_length-2] = '\0';
        }
        if(number_raw_input[number_raw_length-1] == 10 &&
           number_raw_input[number_raw_length-2] != 13)
        {
            if(number_raw_length > 101)
            {
                fprintf(stderr, "ERROR code 33, Incorrect Data: number ");
                fprintf(stderr, "must not be greater than 100 characters\n");
                return 33;
            }
            for(int i=0; i < number_raw_length-1; i++)
            {
                contact_book.number[i] = number_raw_input[i];
            }
            contact_book.number[number_raw_length-1] = '\0';
        }
        if(number_raw_input[number_raw_length-1] != 10 &&
           number_raw_input[number_raw_length-2] != 13)
        {
            fprintf(stderr, "ERROR code 32, Input Overflow: number ");
            fprintf(stderr, "must not be greater than 100 characters\n");
            return 32;
        }

        // kdyz telefonni cislo ma prazdne jmeno
        if(name_raw_length == 2 &&
           name_raw_input[0] == 13 &&
           name_raw_input[1] == 10)
        {
            fprintf(stderr, "ERROR code 30, the number's: ");
            for(int j=0; j < number_raw_length-2; j++)
            {
                fprintf(stderr, "%c", number_raw_input[j]);
            }
            fprintf(stderr, " name is empty\n");
            return 30;
        }
        if(name_raw_length == 1 &&
           name_raw_input[0] == 10)
        {
            fprintf(stderr, "ERROR code 30, the number's: ");
            for(int j=0; j < number_raw_length-1; j++)
            {
                fprintf(stderr, "%c", number_raw_input[j]);
            }
            fprintf(stderr, " name is empty\n");
            return 30;
        }

        if(number_raw_length == 2 &&
           number_raw_input[0] == 13 &&
           number_raw_input[1] == 10)
        {
            fprintf(stderr, "ERROR code 31, the name's: ");
            for(int j=0; j < name_raw_length-2; j++)
            {
                fprintf(stderr, "%c", name_raw_input[j]);
            }
            fprintf(stderr, " number is empty\n");
            return 31;
        }
        if(number_raw_length == 1 &&
           number_raw_input[0] == 10)
        {
            fprintf(stderr, "ERROR code 31, the name's: ");
            for(int j=0; j < name_raw_length-1; j++)
            {
                fprintf(stderr, "%c", name_raw_input[j]);
            }
            fprintf(stderr, " number is empty\n");
            return 31;
        }
        
        contact_name_length = strlen(contact_book.name);
        contact_number_length = strlen(contact_book.number);

        if(contact_book.name[0] == 32 ||
           contact_book.name[contact_name_length-1] == 32)
        {
            fprintf(stderr, "ERROR code 34, the name: [");
            for(int j=0; j < contact_name_length; j++)
            {
                fprintf(stderr, "%c", contact_book.name[j]);
            }
            fprintf(stderr, "] must not begin or end with a space\n");
            return 34;
        }
        
        for(int i=0; i < contact_name_length; i++)
        {
            if(contact_book.name[i] < 0)
            {
                fprintf(stderr, "ERROR code 26, the name: ");
                for(int j=0; j < contact_name_length; j++)
                {
                    fprintf(stderr, "%c", contact_book.name[j]);
                }
                fprintf(stderr, " must consist of english letters\n");
                return 26;
            }
            if(i < contact_name_length-2)
            {
                if(contact_book.name[i] == 32 && 
                   contact_book.name[i+1] == 32)
                {
                    fprintf(stderr, "ERROR code 35, the name: [");
                    for(int j=0; j < contact_name_length; j++)
                    {
                        fprintf(stderr, "%c", contact_book.name[j]);
                    }
                    fprintf(stderr, "] must not contain 2 spaces in a row\n");
                    return 35;
                }
            } 
        }

        for(int i=0; i < contact_number_length; i++)
        {
            // Cislo obsahuje pouze cislice nebo znamenko plus.
            if((contact_book.number[i]  < 48  ||
                contact_book.number[i]  > 57) &&
                contact_book.number[i] != 43)
            {
                fprintf(stderr, "ERROR code 24, the number: ");
                for(int j=0; j < contact_number_length; j++)
                {
                    fprintf(stderr, "%c", contact_book.number[j]);
                }
                fprintf(stderr, " must consist of 0...9 or '+' \n");
                return 24;
            }
            if(i != 0 && contact_book.number[i] == 43)
            {
                fprintf(stderr, "ERROR code 25, the '+': ");
                for(int j=0; j < contact_number_length; j++)
                {
                    fprintf(stderr, "%c", contact_book.number[j]);
                }
                fprintf(stderr, " must be at the beginning \n");
                return 25;
            }
        }

        // Zobrazeni vsech kontaktu
        if(mode == 'a')
        {
            valid_tnine_counter = 1;
            for(int i=0; i < contact_name_length; i++)
            {
                printf("%c", contact_book.name[i]);
            }
            printf(", ");
            for(int i=0; i < contact_number_length; i++)
            {
                printf("%c", contact_book.number[i]);
            }
            printf("\n");
        }

        // Vystup tech pinu, ktere obsahuji sekvence
        if(mode == 'f')
        {
            valid_tnine = tnine_solver(mode, user_input, contact_book);
            if(valid_tnine == 0 || valid_tnine == 1)
            {
                valid_tnine_counter += valid_tnine;
            }
            else
            {
                return valid_tnine;
            }
        }

        // Vystup tech vyvodu, ktere obsahuji prerusenou sekvenci.
        if(mode == 's')
        {
            valid_tnine = tnine_solver(mode, user_input, contact_book);
            if(valid_tnine == 0 || valid_tnine == 1)
            {
                valid_tnine_counter += valid_tnine;
            }
            else
            {
                return valid_tnine;
            }
        }

        if(mode != 'a' && mode != 'f' && mode != 's')
        {
            fprintf(stderr, "ERROR code 29, the mode: %c", mode);
            fprintf(stderr, "is incorrect, avaliable modes are: 'a', 'f', 's' \n");
            return 29;
        }

    }

    // Pokud nejsou nalezeny zadne kontakty, ktere by splnovaly pozadavky
    if(valid_tnine_counter == 0)
    {
        printf("Not found\n");
    }
    return 0;
}


// Dostupne mody: 's' = Hledani poskozenych sekvenci
// ve vychozim stavu 'f' = Vyhledavani sekvenci
int tnine_solver(char mode, char user_input[102], struct contact_list contact_book)
{
    // Pocet vystupnich kontaktu
    int is_contact_print = 0;

    int user_input_length;
    int contact_name_length;
    int contact_number_length;

    user_input_length = strlen(user_input);
    contact_name_length = strlen(contact_book.name);
    contact_number_length = strlen(contact_book.number);

    // Ciselne vyjadreni kontaktu
    // (pismena jmena prevedena na cislice telefonni klavesnice)
    struct contact_list numeric_book;

    char check_character;

    for(int i=0; i < contact_number_length; i++)
    {
        numeric_book.number[i] = contact_book.number[i];
    }

    if(contact_book.number[0] == '+')
    {
        numeric_book.number[0] = '0';
    }

    for(int i=0; i < contact_name_length; i++)
    {

        numeric_book.name[i] = contact_book.name[i];

        check_character = contact_book.name[i];

        // Vyrazeni intervalu bez pismen
        // od A
        if(check_character < 65 && check_character != 43)
        {
            continue;
        }

        // od Z do a
        if(check_character > 91 && check_character < 97)
        {
            continue;
        }

        // od z
        if(check_character > 122)
        {
            continue;
        }

        // Prevod malych pismen na velka
        // od a do z; a -> A
        if(check_character >= 97 && check_character <= 122)
        {
            check_character = check_character - 32;
        }

        // Prevest kazde pismeno jmena na odpovidajici cislo
        // A...C, a...c
        if(check_character >= 65 && check_character <= 67)
        {
            numeric_book.name[i] = '2';
        }

        // D...F, d...f
        if(check_character >= 68 && check_character <= 70)
        {
            numeric_book.name[i] = '3';
        }

        // G...I, g...i
        if(check_character >= 71 && check_character<= 73)
        {
            numeric_book.name[i] = '4';
        }

        // J...L, j...l
        if(check_character >= 74 && check_character <= 76)
        {
            numeric_book.name[i] = '5';
        }

        // M...O, m...o
        if(check_character >= 77 && check_character <= 79)
        {
            numeric_book.name[i] = '6';
        }

        // P...S, p...s
        if(check_character >= 80 && check_character <= 83)
        {
            numeric_book.name[i] = '7';
        }

        // T...V, t...v
        if(check_character >= 84 && check_character <= 86)
        {
            numeric_book.name[i] = '8';
        }

        // W...Z, w...z
        if(check_character >= 87 && check_character <= 90)
        {
            numeric_book.name[i] = '9';
        }

        // '+'
        if(check_character == 43)
        {
            numeric_book.name[i] = '0';
        }
    }

    // Vyhledani shody mezi prvnim cislem uzivatele a aktualnim cislem kontaktu.
    // Spusteni definice sekvence pro nasledujici cisla
    for(int i=0; i < contact_number_length; i++)
    {
        if(user_input[0] == numeric_book.number[i])
        {
            if(user_input_length == 1)
            {
                is_contact_print += 1;
            }
            else if(user_input_length-1 < contact_number_length-i)
            {
                // Nalezeni prerusene sekvence
                if (mode == 's')
                {
                    is_contact_print += is_any_matching(1,
                                                        i+1,
                                                        user_input,
                                                        numeric_book.number,
                                                        user_input_length,
                                                        contact_number_length);
                }
                // Vyhledavani sekvenci
                else
                {
                    is_contact_print += is_next_matching(1,
                                                         i+1,
                                                         user_input,
                                                         numeric_book.number,
                                                         user_input_length,
                                                         contact_number_length);
                }

            }
        }
    }

    // Vyhledani shody mezi prvnim cislem uzivatele a jmenem aktualniho kontaktu.
    // Spusteni definice sekvence pro nasledujici cisla
    for(int i=0; i < contact_name_length; i++)
    {
        if(user_input[0] == numeric_book.name[i])
        {
            if(user_input_length == 1)
            {
                is_contact_print += 1;
            }
            else if(user_input_length-1 < contact_name_length-i)
            {
                // Nalezeni prerusene sekvence
                if (mode == 's')
                {
                    is_contact_print += is_any_matching(1,
                                                        i+1,
                                                        user_input,
                                                        numeric_book.name,
                                                        user_input_length,
                                                        contact_name_length);
                }
                // Vyhledavani sekvenci
                else
                {
                    is_contact_print += is_next_matching(1,
                                                         i+1,
                                                         user_input,
                                                         numeric_book.name,
                                                         user_input_length,
                                                         contact_name_length);
                }
            }

        }
    }
    // Vypise kontakt, pokud je nalezena alespon jedna shoda.
    if(is_contact_print >= 1)
    {
        for(int i=0; i < contact_name_length; i++)
        {
            printf("%c", contact_book.name[i]);
        }
        printf(", ");
        for(int i=0; i < contact_number_length; i++)
        {
            printf("%c", contact_book.number[i]);
        }
        printf("\n");
        return 1;
    }
    return 0;
}

// Rekurzivni funkce pro vyhledani prerusene posloupnosti znaku
int is_any_matching(int user_input_step, int contact_book_step,
                    char user_input[102], char book_name_or_number[101],
                    int user_input_lenght, int contact_length)
{
    // Pokud je to posledni cislo, zkontrolujte ho a ukoncete rekurzi.
    if(user_input_step == user_input_lenght-1)
    {
        for(int i=contact_book_step; i < contact_length; i++)
        {
            if(user_input[user_input_step] == book_name_or_number[i])
            {
                return 1;
            }
        }
        return 0;
    }
    // Zkontrolujte, zda se aktualni cislo shoduje se zbyvajicimi znaky jmena/cisla.
    for(int i=contact_book_step; i < contact_length; i++)
    {
        if(user_input[user_input_step] == book_name_or_number[i])
        {
            return is_any_matching(user_input_step+1,
                                   i+1,
                                   user_input,
                                   book_name_or_number,
                                   user_input_lenght,
                                   contact_length);
        }
    }
    return 0;
}

// Rekurzivni funkce pro vyhledani posloupnosti znaku
int is_next_matching(int user_input_step, int contact_book_step,
                     char user_input[102], char book_name_or_number[101],
                     int user_input_lenght, int contact_length)
{
    // Pokud je to posledni cislo, zkontrolujte ho a ukoncete rekurzi.
    if(user_input_step == user_input_lenght-1)
    {
        if(user_input[user_input_step] == book_name_or_number[contact_book_step])
        {
            return 1;
        }
        else
        {
            return 0;
        }
    }
    // Zkontrolovat, zda se aktualni cislo shoduje se znakem jmena/cisla.
    if(user_input[user_input_step] == book_name_or_number[contact_book_step])
    {
        return is_next_matching(user_input_step+1,
                                contact_book_step+1,
                                user_input,
                                book_name_or_number,
                                user_input_lenght,
                                contact_length);
    }
    else
    {
        return 0;
    }
}
