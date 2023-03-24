#User defined variables
fileName = 'SpeedNFeed testing.gcode'
fileFolder = 'Latest'
cutterDiameter = 3 #mm
depthOfCut = 3 #mm 
plungeSpeed = 250 #mm/min
nominalTrenchGap = 5 #mm
numberOfTrenches = 5
markerSize = 2 #mm
trenchLength = 1200 #mm
numberOfSpeedSegments = 5
minSpindleSpeed = 15000 #RPM
maxSpindleSpeed = 23000 #RPM
minFeed = 1000 #mm/min
maxFeed = 8000 #mm/min
numberOfFeedTrenches = 8
appendFeedsToFile = True #True or false

#Calculated variables
fileName = fileFolder + "/" + fileName
if appendFeedsToFile:    
    fileName = fileName[:len(fileName)-6] + " " + str(minFeed//1000) + "-" + str(maxFeed//1000) + "k.gcode"
gapBetweenLines = nominalTrenchGap + cutterDiameter
speedSegmentLength = trenchLength / numberOfSpeedSegments
speedRange = list(range(minSpindleSpeed, maxSpindleSpeed+1, int((maxSpindleSpeed-minSpindleSpeed)/(numberOfSpeedSegments-1))))
speedRange.insert(0, minSpindleSpeed)
positionRange = list(range(0, trenchLength+1, int(trenchLength/(numberOfSpeedSegments))))
feedRange = list(range(minFeed, maxFeed+1, int((maxFeed-minFeed)/(numberOfFeedTrenches-1))))

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
    f.write("G90\nG0X0Z0\n")
    #Loop through feed segments
    for segment in range(numberOfFeedTrenches):
        f.write(moveOverTo(segment, nominalTrenchGap, cutterDiameter))
        f.write(cutTrench(feedRange[segment], positionRange, speedRange, minSpindleSpeed, depthOfCut, plungeSpeed))
        f.write(moveBack())        
    f.write("G1 Z0F" + str(plungeSpeed) + "\nM5")        
f.close()

print(fileName + " written")

