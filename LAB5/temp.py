input_file_name = "input_file1.txt"

ptr1 = open(input_file_name, "r")
input_file = []

for line in ptr1:
    temp = line.split()
    temp = [int(i) for i in temp]
    input_file.append(temp)

print(input_file)