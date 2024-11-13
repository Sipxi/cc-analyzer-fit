/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                 VUT FIT
         1. rocnik zimni semestr 
                   IZP
                projekt 1. 
                
                 made by
              Feliks Kulikou 
               [xkulikf00]

    pouziti: 

    ./tnine (-s) (libovolne_cislo) <seznam.txt 
    (v zavorkach jsou volitelne argumenty) 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>


#define STRING_MAX_LENGTH 101       // maximalni delka retezce


const char *intToChar[] = {       // seznam znaku pro t9

            "0+",        // 0
            "1",         // 1
            "2abc",      // 2
            "3def",      // 3
            "4ghi",      // 4
            "5jkl",      // 5
            "6mno",      // 6
            "7pqrs",     // 7
            "8tuv",      // 8
            "9wxyz"      // 9
};


/*

    funkce matchesDigit():

    zjistuje, zda znak contactChar se rovna znaku z retezce possibleChars
    a pokud se rovna, vrati "true", v opacnem pripadu vrati "false"

*/

int MatchesDigit(char contactChar, int toFindDigit) 
{
    const char *possibleChars = intToChar[toFindDigit]; 
    int posCharslength = strlen(possibleChars);

    for (int idx = 0; idx < posCharslength; idx++) {
        if (contactChar == possibleChars[idx]) {
            return 1;
        }
    }
    return 0;
}


/*

funkce contactSearch() :

1) pokud cislo argumentu je 0, vrati "true" aby se
    vytiskly veskere kontakty ze seznamu; pokud ne pokracue bodem 2

2) hleda, zda v retezci existuje pismeno nebo cislice 
   ktere se rovna prvni cislici zadaneho argumentem retezce

3.1) pokud ano, zjisti, zda nasledujici pismena nebo cislice 
     zachovavaji vyzadovanou posloupnost

3.2) pokud ne, zacne bodem 2), zacinajic znakem na kterem se zastavila

4) pokud prechazejic celym retezcem vysledek funkci se nezmenil na "0", 
   tak vysledek funkci bude "1" (true)

*/

int contactSearch(char *toFind, char *contactString, int anyArgs) 
{
    if (anyArgs == 0)
        return 1;         

    int toFindLength = strlen(toFind);        
    int contactStringLength = strlen(contactString);  

    for (int idx = 0; idx < contactStringLength ; idx++) 
    {
        if (contactString[idx] == ' ' || contactString[idx] == ',')
            continue;

        int match = 1;

        for (int jdx = 0; jdx < toFindLength; jdx++) 
        {
            int toFindDigit = toFind[jdx] - '0';

            if (idx+jdx <= contactStringLength)
            {
                if (matchesDigit(contactString[idx + jdx], toFindDigit) == 0) {
                    match = 0;
                    break;
                }
            }
        }

        if (match) 
            return 1; 
    }
    
    return 0; 
}


/*

    funkce contactSearchArg() je podobna predchazejici funkci, ale
    zjistuje, zda posloupnost se zachovava pres cely retezec, nikoliv znak po znaku

*/

int contactSearchArg(char *toFind, char *contactString, int anyArgs)
{
    if (anyArgs == 0)
        return 1;  

    int toFindLength = strlen(toFind);        
    int contactStringLength = strlen(contactString);  
    
    int match = 0;

    for (int idx = 0; idx < contactStringLength; idx++)
    {   
        int toFindDigit = toFind[match] - '0';

        if (matchesDigit(contactString[idx], toFindDigit) == 1) 
        {
            match++;
        }

        if (match == toFindLength) 
        {
            return 1; 
            match = 0;
        }
    }

    return 0;
}


/*
    funkce argCheck() :

    1) zjistuji se, kolik je argumentu (mimo nazev souboru), a

        1.1) pokud > 3, vytiskne chybu na stderr

        1.2) pokud je > 1, pokracuje do bodu 2)

    2) zjisti, zda argument je cislo

        2.1) pokud ano, pokracuje

        2.2) pokud ne, vytiskne chybu na stderr

*/

int argCheck(int arg, char *argStr)
{
    if(arg > 3)
    {
        fprintf(stderr, "Too many arguments (>2). Exiting with error code 1.\n");
        return 0;
    }
    if (arg > 1)
    {
        char argString[STRING_MAX_LENGTH];
        strcpy(argString, argStr);

        for (int idx = 0; argString[idx] != '\0' ; idx++)
        {
            if ((argString[idx] < '0') || (argString[idx] > '9'))
            {
                fprintf(stderr, "The main argument is not a number. Exiting with error code 1.");
                return 0;
            }
        }
    }
    

    return 1;
}


/*
    funkce contactPrint():

    1) nacita retezce z stdin, dela z nich jeden retezec, pak vyvolava
       funkci contactSearch() (nebo contactSearchArg, pokud argc > 1)
       a pokud vrati vysledek "1" tak vytiskne kontakt na stdout

    2) pokud nenalezne zadne odpovidajici argumentovi kontakty, 
       vytiskne "Not found"

*/

int contactPrint(char *num, int argc, int anyArgs)
{
    char inputString[STRING_MAX_LENGTH];
    char contName[STRING_MAX_LENGTH];
    char contNum[STRING_MAX_LENGTH];
    contName[0] = '\0';
    contNum[0] = '\0';
    int isAnyFound = 0;

    for (int idx = 0; scanf(" %[^\n]", inputString) != EOF; idx++)
        {
            if (strlen(inputString) > 100)
            {
                fprintf(stderr, "Invalid input data (>100 chars). Exiting with error code 1.");
                return 1;
            }

            if (idx == 0 && strlen(inputString) < 1)
            {
                fprintf(stderr, "Invalid input data (<1 chars). Exiting with error code 1.");
                return 1;
            }

            if ((idx+1) % 2 != 0)
            {
                strcpy(contName, inputString);
                for (int i = 0; contName[i] != '\0'; i++) 
                    contName[i] = tolower(contName[i]);
            }  
            else
            {
                strcpy(contNum, inputString);
                if (argc == 3)
                {
                    if ((contactSearchArg(num, contName, anyArgs) || 
                            contactSearchArg(num, contNum, anyArgs)) == 1)
                    {
                        isAnyFound = 1;
                        printf("%s, %s\n", contName, contNum);
                    } 
                }
                else
                {
                    if ((contactSearch(num, contName, anyArgs) || 
                            contactSearch(num, contNum, anyArgs)) == 1 || argc == 1)
                    {
                        isAnyFound = 1;
                        printf("%s, %s\n", contName, contNum);
                    }
                }
            }
        }
        if (isAnyFound == 0)
            printf("Not found\n");

    return 0;
}


/*

    funkce bonusArgCheck() zjistuje, zda bonusovy argument je spravny,
    pokud pocet argumentu je 3.
    pokud je spravny, vrati "true", pokud ne, vrati chybove hlaseni

*/

int bonusArgCheck(int argNum, char *bonusArg)
{
    if (argNum == 3)
    {
        if (bonusArg[0] == '-' && bonusArg[1] == 's')
        {
            return 1;
        }
        else
            return 2;
    }
    else
        return 0;
}


/*

    funkce main() 
    
    1) vyvolavanim funkci argCheck() a bonusArgCheck()
        zjistuje spravnost argumentu 

    2) pokracuje funkci contactPrint()
        ktera zjistuje spravnost vstupnich dat nachazi ze vstupnich dat
        odpovidajici argumentovi vytiska je na stdout

*/

int main(int argc, char *argv[])
{

    int anyArgs = 0;
    int argIndex = 1;

    if (argc > 1) 
    {
        if (bonusArgCheck(argc, argv[1]) == 1)
        argIndex = 2;
        else if
            (bonusArgCheck(argc, argv[1]) == 2)
            {
                fprintf(stderr, "Argument error: expected -s as a first parameter. Exitinig with error code 1.");
                return 1;
            }

        if (argCheck(argc, argv[argIndex]))
            anyArgs = 1;
        else
            return 1;
        
    }
    
    // pokud contactPrint() vrati chybove hlaseni (retezec >100 znaku), tak program se zastavi
    if (contactPrint(argv[argIndex], argc, anyArgs) == 1) 
        return 1;

    return 0;
}