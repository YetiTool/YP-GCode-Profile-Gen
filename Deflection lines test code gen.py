import shutil
import os

# Key vars
cutterDiameter = 8.0 # mm ALWAYS SPEC AT LEAST 1 DP, even if 0 as convention, as a measure to catch the imperial accuracies
depthOfCut = 4 # mm 
spindleSpeed = 22000 # RPM
minFeed = 5000 # mm/min
maxFeed = 8000 # mm/min
numberOfFeeds = 4

# Standard vars
fileName = 'Def.gcode'
fileFolder = 'Latest'
verificationDepth = 1 # mm
verificationFeed = 2000 # mm/min
plungeSpeed = 250 # mm/min
trenchLength = 440 # mm
nominalTrenchGap = 5 # mm
cutVerificationLine = False # True or False
appendFeedsToFileName = True # True or false
trenchesPerFeed = 3

# Calculated variables
fileName = fileFolder + "/" + fileName
if appendFeedsToFileName:    
    fileName = fileName[:len(fileName)-6] + " ø" + str(cutterDiameter) + " " + str(minFeed//1000) + "-" + str(maxFeed//1000) + "k " + str(depthOfCut) + "deep.gcode"
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

    
# Write GCODE file
with open(fileName,"w+") as f:

    gcode = ""
    trench = 1
    # MAIN CUT
    gcode = addLine(gcode, "G90G0 Z2") # Lift Z    
    gcode = addLine(gcode, "M3 S" + str(spindleSpeed)) #Start spindle
    gcode = addLine(gcode, "G90G0 X-5Y-5\nG90G0 Z-1\nG90G0 X0Y0") # Ident test-start AND remove backlash
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
        gcode = addLine(gcode, "G90G0 X0") #Rtn to X start 

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

f.close()
print(fileName + " written")

