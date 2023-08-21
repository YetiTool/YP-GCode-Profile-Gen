import shutil
import os

#Key vars
cutterDiameter = 6 # mm
depthOfCut = 5 # mm 
spindleSpeed = 23000 # RPM
minFeed = 2000 # mm/min
maxFeed = 6000 # mm/min
numberOfFeeds = 3
safeDistance = 5 #mm
directionOfCut = "y" #"x" or "y"

#Standard vars
fileName = 'Def.gcode'
fileFolder = 'Latest'
verificationDepth = 1 # mm
verificationFeed = 2000 # mm/min
plungeSpeed = 250 # mm/min
trenchLength = 420 # mm
nominalTrenchGap = 5 # mm
cutVerificationLine = False # True or False
appendFeedsToFileName = True # True or false
trenchesPerFeed = 3

def checkForInvert(): #Do the axes need to be swapped
    if "y" in directionOfCut.lower():
        return True
    else:
        return False

# Calculated variables
if checkForInvert():
    fileName = "y " + fileName
fileName = fileFolder + "/" + fileName
if appendFeedsToFileName:    
    fileName = fileName[:len(fileName)-6] + " ø" + str(cutterDiameter) + " " + str(minFeed//1000) + "-" + str(maxFeed//1000) + "k.gcode"
feedIncrement = ((maxFeed-minFeed)//(numberOfFeeds-1))
feeds = list(range(minFeed,maxFeed+1,feedIncrement))
print(feeds)

def addLine(variable, line):
    variable = variable + str(line) + "\n"
    return variable

def drawLine(dimension, direction, feedRate):
    gcode = ""
    feedRate = str(feedRate)
    dimension = str(dimension)
    if direction == 1: #0 = +X , 1 = -X
        dimension = "10"
    # gcode = addLine(gcode, "G90G1 X" + dimension + "F" + feedRate)  
    gcode = "G90G1 X" + str(dimension) + "F" + str(feedRate)
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
    trench = 1
    #MAIN CUT
    gcode = addLine(gcode, "*LEA00FF") #Magenta because it's cute
    gcode = addLine(gcode, "G90G0 Z" + str(safeDistance)) # Lift Z    
    gcode = addLine(gcode, "M3 S" + str(spindleSpeed)) #Start spindle
    gcode = addLine(gcode, "*LFFFFFF") #White because filming
    gcode = addLine(gcode, "G90G0 X-5Y-5\nG90G0 X0Y0") # Remove backlash
    gcode = addLine(gcode, "G90G0 X" + str(cutterDiameter/2)) #Move up to half cutter diameter
    gcode = addLine(gcode, "G90G0 Z-1") # Plunge z
    gcode = addLine(gcode, "\n(MAIN CUT)\n")
    for feed in feeds:
        
        gcode = addLine(gcode, "(New feed: " + str(feed) + ")\n")
        gcode = addLine(gcode, "G90G1 Z" + str(-1*depthOfCut) + "F" + str(plungeSpeed)) # Plunge Z    

        direction = 0 # OUT
        gcode = addLine(gcode, drawLine(trenchLength-cutterDiameter, direction, feed)) #Cut entire length squggle  
        gap = (nominalTrenchGap + cutterDiameter) * trench
        gcode = addLine(gcode, moveOver(gap, feed)) #Move over  
        trench += 1

        direction = 1 # RTN
        gcode = addLine(gcode, drawLine(trenchLength-cutterDiameter, direction, feed)) #Cut entire length squggle  
        gap = (nominalTrenchGap + cutterDiameter) * trench
        gcode = addLine(gcode, moveOver(gap, feed)) #Move over  
        trench += 1

        direction = 0 # OUT
        gcode = addLine(gcode, drawLine(trenchLength-cutterDiameter, direction, feed)) #Cut entire length squggle  

        # RESET TO NEXT START POS
        gcode = addLine(gcode, "G90G0 Z2") #Lift Z    
        gap = (nominalTrenchGap + cutterDiameter) * trench
        gcode = addLine(gcode, moveOver(gap, feed)) #Move over  
        trench += 1

        gcode = addLine(gcode, "G90G0 X" + str(cutterDiameter/2)) #Rtn to X start 

               

    if (cutVerificationLine):    
        #VERIFICATION LINE
        direction = 0
        gcode = addLine(gcode, "M3 S" + str(spindleSpeed) + "\nG90G0 X-5Y-5Z0\nG90G0 X0Y0") #Start spindle AND remove backlash
        gcode = addLine(gcode, "G90G1 Z" + str(-1*verificationDepth) + "F" + str(plungeSpeed)) # Plunge Z    
        gcode = addLine(gcode, "\n(VERIFICATION CUT)")
        for i in range(len(feeds)):     
            gcode = addLine(gcode, "(new line)")
            gap = nominalTrenchGap * (i) + cutterDiameter * (i)
            gcode = addLine(gcode, moveOver(gap, verificationFeed)) #Move over  
            gcode = addLine(gcode, drawLine(trenchLength-cutterDiameter, direction, verificationFeed)) #Cut entire length squggle  
            direction = not(direction) #Invert direction for next pass
        
    gcode = addLine(gcode, "G90G0 Z2") #Lift Z    
    gcode = addLine(gcode, "M5") #Stop spindle
    f.write(gcode)
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

