import shutil
import os

#User defined variables
fileName = 'Deflection lines test.gcode'
fileFolder = 'Latest'
cutterDiameter = 3 #mm
depthOfCut = 6 #mm 
verificationDepth = 1 #mm
verificationFeed = 2000 #mm/min
spindleSpeed = 19000 #RPM
plungeSpeed = 250 #mm/min
trenchLength = 580 #mm
minFeed = 2000 #mm/min
maxFeed = 5000 #mm/min
numberOfFeeds = 4
nominalTrenchGap = 5 #mm
feedConstantInBothDirections = True #True or False
cutVerificationLine = False # True or False
appendFeedsToFile = True #True or false

#Calculated variables
fileName = fileFolder + "/" + fileName
if appendFeedsToFile:    
    fileName = fileName[:len(fileName)-6] + " " + str(minFeed//1000) + "-" + str(maxFeed//1000) + "k.gcode"
stepSize = ((maxFeed-minFeed)//(numberOfFeeds-1))
print(stepSize)
feeds = list(range(minFeed,maxFeed+1,stepSize))

if feedConstantInBothDirections:
    newFeeds = []
    for feed in feeds:
        newFeeds.append(feed)
        newFeeds.append(feed)
    feeds = newFeeds
print(feeds)

def addLine(variable, line):
    variable = variable + str(line) + "\n"
    return variable

def drawLine(dimension, direction, feedRate):
    gcode = ""
    feedRate = str(feedRate)
    dimension = str(dimension)
    if direction == 1: #0 = +X , 1 = -X
        dimension = "0"
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
    gcode = addLine(gcode, "M3 S" + str(spindleSpeed) + "\nG90G0 X-5Y-5Z0\nG90G0 X0Y0") #Start spindle AND remove backlash
    gcode = addLine(gcode, "G90G1 Z" + str(-1*depthOfCut) + "F" + str(plungeSpeed)) # Plunge Z    
    gcode = addLine(gcode, "\n(MAIN CUT)")
    for i in range(len(feeds)):     
        gcode = addLine(gcode, "(new line)")
        gap = nominalTrenchGap * (i) + cutterDiameter * (i)
        gcode = addLine(gcode, moveOver(gap, feeds[i])) #Move over  
        gcode = addLine(gcode, drawLine(trenchLength-cutterDiameter, direction, feeds[i])) #Cut entire length squggle  
        direction = not(direction) #Invert direction for next pass
        
    gcode = addLine(gcode, "G90G0 Z2") #Lift Z        

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

