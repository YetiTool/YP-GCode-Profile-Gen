fileName = 'SNF test 0-2k, 15-23k.gcode'
fileFolder = 'Latest'

file = fileFolder + "/" + fileName
file2 = fileFolder + "/Y " + fileName

# Open the input file
with open(file, 'r') as input_file:
    # Read the contents of the input file
    contents = input_file.read()

# Replace all instances of "x" with "y" and vice versa
contents = contents.replace('x', 'temp')
contents = contents.replace('y', 'X')
contents = contents.replace('temp', 'Y')
contents = contents.replace('X', 'temp')
contents = contents.replace('Y', 'X')
contents = contents.replace('temp', 'Y')

# Open the output file
with open(file2, 'w+') as output_file:
    # Write the modified contents to the output file
    output_file.write(contents)
    output_file.close()
    print(file2 + " written")
