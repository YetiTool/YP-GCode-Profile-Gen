#User defined variables
fileName = 'SNF test.gcode'
fileFolder = 'Latest'
cutterDiameter = 3.19 #mm
depthOfCut = 2 #mm 
plungeSpeed = 250 #mm/min

directionOfCut = "y" #"x" or "y"

nominalTrenchGap = 5 #mm

markerSize = cutterDiameter/2 #mm

trenchLength = 650 #mm

numberOfSpeedSegments = 5
minSpindleSpeed = 15000 #RPM
maxSpindleSpeed = 23000 #RPM

minFeed = 500 #mm/min
maxFeed = 2000 #mm/min
numberOfFeedTrenches = 4

appendFeedsToFile = True #True or false
compensateCutterDiameter = True #True or false

def checkForInvert(): #Do the axes need to be swapped
    if "y" in directionOfCut.lower():
        return True
    else:
        return False

#Calculated variables
if checkForInvert():
    fileName = "y " + fileName
fileName = fileFolder + "/" + fileName
if appendFeedsToFile:    
    fileName = fileName[:len(fileName)-6] + " " + str(minFeed//1000) + "-" + str(maxFeed//1000) + "k, " + str(minSpindleSpeed//1000) + "-" + str(maxSpindleSpeed//1000) + "k.gcode"
gapBetweenLines = nominalTrenchGap + cutterDiameter
speedSegmentLength = trenchLength / numberOfSpeedSegments
speedRange = list(range(minSpindleSpeed, maxSpindleSpeed+1, int((maxSpindleSpeed-minSpindleSpeed)/(numberOfSpeedSegments-1))))
speedRange.insert(0, minSpindleSpeed)

feedRange = list(range(minFeed, maxFeed+1, int((maxFeed-minFeed)/(numberOfFeedTrenches-1))))
halfCutterDiameter = cutterDiameter/2

if compensateCutterDiameter:
    sectionLength = (trenchLength - halfCutterDiameter) / numberOfSpeedSegments
    positionRange = []
    for i in range(numberOfSpeedSegments+1):
        positionRange.append(round(sectionLength*i, 1))
    positionRange[0] = halfCutterDiameter
else:
    positionRange = list(range(0, trenchLength+1, int(trenchLength/(numberOfSpeedSegments))))
    
print(feedRange)
print(speedRange[1:])


def cutTrench(cutFeed, positionRange, speedRange, minSpindleSpeed, depthOfCut, plungeSpeed):
    cutFeed = str(cutFeed)
    minSpindleSpeed = str(minSpindleSpeed)
    depthOfCut = str(depthOfCut)
    plungeSpeed = str(plungeSpeed)
    trench = "\n(NEW TRENCH)\nM3 S" + minSpindleSpeed + "\nG1 Z-" + depthOfCut + "F" + plungeSpeed + "\n"

    for segmentNumber in range(len(positionRange)):
        line = "(new speed)\nG1 X" + str(positionRange[segmentNumber]) + "F" + cutFeed + "S" + str(speedRange[segmentNumber]) + "\n" + "G91G1 Y" + str(markerSize) + "F1000\nG91G1 Y-" + str(markerSize) + "F1000\nG90\n"
        trench = trench + line
    return trench + "G0 Z2S"+ str(minSpindleSpeed) + "\n"

def moveBack():
    return "G0 X0\n"

def moveOverTo(trenchNumber, nominalTrenchGap, cutterDiameter):
    distanceToTravel = (nominalTrenchGap + cutterDiameter)*trenchNumber
    return "G0 Y" + str(distanceToTravel) +"\n"
    
#Write GCODE file
with open(fileName,"w+") as f:
    f.write("*LFFFFFF\n")
    f.write("M3 S" + str(minSpindleSpeed) + "\n")
    f.write("G90\nG0X0Z0\n")
    #Loop through feed segments
    for segment in range(numberOfFeedTrenches):
        f.write(moveOverTo(segment, nominalTrenchGap, cutterDiameter))
        f.write(cutTrench(feedRange[segment], positionRange, speedRange, minSpindleSpeed, depthOfCut, plungeSpeed))
        f.write(moveBack())        
    f.write("G1 Z0F" + str(plungeSpeed) + "\nM5")

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

