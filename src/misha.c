#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <ctype.h>

// Array with letters associated with the digits on the old phone keypad
char *numbers[8] = 
{
	"abc",	// 2
	"def",	// 3
	"ghi",	// 4
	"jkl",	// 5
	"mno",	// 6
	"pqrs",	// 7
	"tuv",	// 8
	"wxyz"	// 9
};


// Function to check for mistakes in the argument
int CheckForErrors(int argc, char *argv)
{
	// Returning an error, if we have more than 1 sequence of digits
	if(argc > 2)
	{
		 fprintf(stderr, "Too many arguments (%d)", argc);
		 return 1;
	}

	// Returning an error, if sequence of digits contains errors
	if(argc != 1)
	{
		int i = 0;
		while(argv[i] != '\0')
		{
			if(isdigit(argv[i]) == 0)
			{
				fprintf(stderr, "Letters were detected: %d", argc);
				return 1;
			}
			i++;
		}
	}

	return 0;

}

// Function to check if a letter corresponds to a specific digit on the phone keypad
bool CheckSymbol(int digit, char letter)
{
	int keypad_index = digit - 2;	// Finding the needed set of letters, using corresponding number and array index
	int i = 0;

	// Returning false, if we have 1 (no letter corresponds to it)
	if(digit == 1)
	{
		return 0;
	}

	// Additional check for "+"
	if(digit == 0)
	{
		if(letter == '+')
		{
			return 1;
		}
		return 0;
	}
	
	// Comparing letter to the corresponding digit (2-9)
	while(numbers[keypad_index][i] != '\0')
	{
		if( (letter == numbers[keypad_index][i]) || (tolower(letter) == numbers[keypad_index][i]))
		{
			return 1;
		}
		i++;
	}
	
	
	

	return 0;
}


// Function to check, if name contains set of digits (based on the old phone keypad mapping)
bool CheckForLetters(char *digit, int digit_length, char *name)
{
	// No need to compare, if set of digits is longer than the name
	if(digit_length > (int)strlen(name))
	{
		return 0;
	}

	int count = 0;

	// Looping through the name to find matching sequences of letters for the digit sequence
	for(int i = 0; i <= (int)strlen(name) - digit_length; i++)
	{
		for(int j = 0; j < digit_length; j++)
		{
			// Converting the digit character to its integer equivalent
			int converted_digit = digit[j] - '0';	
			// Checking if the letter in the name matches the corresponding digit on the keypad
			if(CheckSymbol(converted_digit, name[i+j]) == 1)
			{
				count++;
			}
		}

		if(count == digit_length)
		{
			return 1;
		}
		count = 0;
	}

	return 0;
}


// Function to compare a sequence of digits with a phone number string
bool CheckForNumbers(char *digit, char *number)
{
	int number_length = strlen(number);
	int digit_length = strlen(digit);

	int count = 0;
	for(int i = 0; i <= number_length - digit_length; i++)
	{
		for(int j = 0; j < digit_length; j++)
		{
			// Checking if the digits matche, also an additional check for "+" in the beginning
			if( (number[i+j] == digit[j]) || ( (number[i+j] == '+') && (i+j == 0) ))
			{
				count++;
			}
		}

		if(count == digit_length)
		{
			return 1;
		}
		count = 0;
	}

	return 0;
}


int main(int argc, char *argv[])
{
	char input_line[256];			// buffer for reading names and numbers
	char list[200][1024];			// A list of names and phone numbers
	char current_entry[1024] = "";	// Temporary array, to store name or phone number
	int list_count = 0;				// Number of names/phone numbers in the list


	// Reading from stdin and converting it to the array with each name and number having a seperate index
	while(fgets(input_line, sizeof(input_line), stdin) != NULL)
	{
		if(list_count >= 200)
		{
			break;
		}
		
		int i = 0;
		while(input_line[i] != '\0')
		{
			// Converting big letters to small ones
			input_line[i] = tolower(input_line[i]); 
			i++;
		}

		strcat(current_entry, input_line);

		// Storing an entry and resetting buffer, if newline detected
		if(strlen(current_entry) > 0)
		{
			if(current_entry[strlen(current_entry) - 1] == '\n')
			{
				// Removing "\0" from the end
				current_entry[strlen(current_entry) - 1] = '\0';	
			}

			strcpy(list[list_count], current_entry);
			list_count++;
			current_entry[0]='\0';
		}
	}


	// Checking for errors in the arguments
	if(CheckForErrors(argc, argv[1]))
	{
		return 1;
	}

	// Printing the whole list if no argument provided
	if(argc == 1)
	{
		for(int i = 0; i < list_count - 1; i+=2)
		{
			printf("%s, %s\n", list[i], list[i+1]);
		}
		return 0;
	}


	int not_found_check = 0;	// Flag to keep track if mathc was found
	int digit_length = strlen(argv[1]);

	for(int i = 0; i < list_count; i++)
	{
		// Searching for the match in numbers in every second array
		if((i+1)%2 == 0)
		{
			if(CheckForNumbers(argv[1], list[i]))
			{
				printf("%s, %s\n", list[i-1], list[i]);
				i++;
				not_found_check = 1;
			}
		}
		else
		{
			// Searching for the match in letters
			if(CheckForLetters(argv[1], digit_length, list[i]))
			{
				printf("%s, %s\n", list[i], list[i+1]);
				i++;
				not_found_check = 1;
			}
		}
	}

	if(not_found_check == 0)
	{
		printf("Not found\n");
	}


	return 0;
}

