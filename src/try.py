data = ['global', 'variable', '16', '../tests/test-files/masha.c', 'int', 'global;', 'need', 'variable', '18', '../tests/test-files/masha.c', 'char', '*need;', 'phone_digits', 'variable', '5', '../tests/test-files/masha.c', 'char', 'phone_digits[29]', '=', '{', 'phone_digits', 'variable', '20', '../tests/test-files/masha.c', 'char', 'phone_digits[3]', '=', '{']


# Initialize an empty dictionary to store the results
result_dict = {}


for i in range(0, len(data)-2, 6):  # Start at 0, end before 15, increment by 6
    print(data[i], data[i + 2])


print(result_dict)
