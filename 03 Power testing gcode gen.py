#User defined variables
fileName = 'Power testing.gcode'
fileFolder = 'Latest'
cutterDiameter = 6 #mm
depthOfCut = 5 #mm 
plungeSpeed = 250 #mm/min
nominalTrenchGap = 5 #mm
numberOfTrenches = 4
trenchLength = 700 #mm
spindleSpeed = 23000 #RPM
feed = 6000 #mm/min
appendSeedToFile = True #True or False
directionOfCut = "x" #"x" or "y"

def checkForInvert(): #Do the axes need to be swapped
    if "y" in directionOfCut.lower():
        return True
    else:
        return False

#Calculated variables
if checkForInvert():
    fileName = "y " + fileName
fileName = fileFolder + "/" + fileName
if appendSeedToFile:    
    fileName = fileName[:len(fileName)-6] + " " + str(spindleSpeed//1000) + "k.gcode"
gapBetweenLines = nominalTrenchGap + cutterDiameter
halfCutterDiameter = cutterDiameter / 2

def addLine(variable, line):
    variable = variable + str(line) + "\n"
    return variable

def drawLine(dimension, direction, feedRate):
    gcode = ""
    feedRate = str(feedRate)
    dimension = str(dimension)
    if direction == 1: #0 = +X , 1 = -X
        dimension = str(halfCutterDiameter)
    gcode = addLine(gcode, "G90G1 X" + dimension + "F" + feedRate)  
    return gcode

def moveOver(dimension, feed):
    gcode = ""
    dimension = str(dimension)
    feed = str(feed)
    gcode = addLine(gcode, "G90G1 Y" + dimension + "F" + feed)
    return gcode

    
#Write GCODE file
with open(fileName,"w+") as f:
    gcode = ""
    #MAIN CUT
    direction = 0
    gcode = addLine(gcode, "*LFFFFFF") #White because filming
    gcode = addLine(gcode, "M3 S" + str(spindleSpeed) + "\nG90G0 X-5Y-5Z-2\nG90G0 X0Y0Z0") #Start spindle AND remove backlash
    gcode = addLine(gcode, "G90G0 X" + str(cutterDiameter/2)) #Move up to half cutter diameter
    gcode = addLine(gcode, "G90G1 Z" + str(-1*depthOfCut) + "F" + str(plungeSpeed)) # Plunge Z  

    gcode = addLine(gcode, "\n(MAIN CUT)")

    for i in range(numberOfTrenches):
        gcode = addLine(gcode, "(new trench)")

        gap = nominalTrenchGap * (i) + cutterDiameter * (i)
        gcode = addLine(gcode, moveOver(gap, feed))
        gcode = addLine(gcode, drawLine(trenchLength-halfCutterDiameter, direction, feed))
        direction = not(direction)     

    gcode = addLine(gcode, "G90G0 Z2") #Lift Z        
    gcode = addLine(gcode, "M5") #Stop spindle

    f.write(gcode)#write to file

    if checkForInvert():
        f.close()
        with open(fileName,"r+") as f:
            print("Inverting file")
            contents = f.read()
            contents = contents.replace('x', 'temp')
            contents = contents.replace('y', 'X')
            contents = contents.replace('temp', 'Y')
            contents = contents.replace('X', 'temp')
            contents = contents.replace('Y', 'X')
            contents = contents.replace('temp', 'Y')
            f.close()
            with open (fileName,"w") as f:
                f.write(contents)  
f.close()

print(fileName + " written")
