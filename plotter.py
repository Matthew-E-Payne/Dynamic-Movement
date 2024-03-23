#-=-=-=-=-=-=| Authors |-=-=-=-=-=-=-#
#            Matthew Payne           #
#             Will Cecil             #
#-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-#

import math
from matplotlib import pyplot as plt
from Init import platWhat

inFileName = 'TrajectoryData.txt' 

class Character:
    def __init__(self, steerType):
        self.rows = 0
        self.steerType = steerType
        self.posX = []
        self.posZ = []
        self.velX = []
        self.velZ = []
        self.linX = []
        self.linZ = []
        self.orientationX = []
        self.orientationZ = []


    def plotPosition(self):
        plt.plot(self.posX, self.posZ, color = 'red', linewidth = 1.2)

        startPos = (self.posX[0] , self.posZ[0])

        circle = plt.Circle(startPos, 2, color = 'red', fill = True) 
        plt.gcf().gca().add_artist(circle)

        steeringBehaviorCode = {1 : 'Continue', 2 : 'Stop',  3 : 'Align', 6 : 'Seek', 7 : 'Flee', 8 : 'Arrive', 11 : 'Follow Path'}
        plt.text(startPos[0] + 3, startPos[1] + 1, steeringBehaviorCode[self.steerType], fontsize = 10, color = 'red')

    def plotLinear(self):
        for i in range(self.rows):
            x = [self.posX[i], self.posX[i] + self.linX[i]]
            z = [self.posZ[i], self.posZ[i] + self.linZ[i]]

            plt.plot(x, z, color = 'blue', linewidth = 1)

    def plotVelo(self):
        for i in range(self.rows):
            x = [self.posX[i], self.posX[i] + self.velX[i] * 2]
            z = [self.posZ[i], self.posZ[i] + self.velZ[i] * 2]

            plt.plot(x, z, color = 'lime', linewidth = 1)


    def plotOrientation(self):
        for i in range(self.rows):
            x = [self.posX[i], self.posX[i] + self.orientationX[i]]
            z = [self.posZ[i], self.posZ[i] + self.orientationZ[i]]

            plt.plot(x, z, color = 'blue', linewidth = 1)

class PathFollow:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def plotPath():
        followPathX = []
        followPathY = []

        followPath = [PathFollow(0, 90), PathFollow(-20, 65), PathFollow(20, 40),
                    PathFollow(-40, 15), PathFollow(40, -10), PathFollow(-60, -35),
                    PathFollow(60, -60), PathFollow(0, -85)]

        for i in followPath:
            followPathX.append(i.x)
            followPathY.append(i.y)
        
        plt.plot(followPathX, followPathY, color = 'grey', linestyle = 'dashed', linewidth = 0.9)
       
        for i in range(len(followPathX)):
            plt.annotate("({:.1f}, {:.1f})".format(followPathX[i], followPathY[i]), (followPathX[i], followPathY[i]), fontsize = 7, color = 'grey')

plt.figure(edgecolor = 'black', figsize = [10, 10])
plt.xlim([-100, 100])
plt.ylim([-100, 100])
plt.plot([-100, 100], [0, 0], color = 'lightgrey', linestyle = 'dashed', linewidth = 2)
plt.plot([0, 0], [-100, 100], color = 'lightgrey', linestyle = 'dashed', linewidth = 2)
plt.title('Movement Trajectory', fontsize = 20)
plt.xlabel('X', fontsize = 20)
plt.ylabel('Z', fontsize = 20)

plt.plot([0, 0], [0, 0], color = 'red', label = 'position') if platWhat['position'] == True else None
plt.plot([0, 0], [0, 0], color = 'lime', label = 'velocity') if platWhat['velocity'] == True else None
plt.plot([0, 0], [0, 0], color = 'blue', label = 'linear') if platWhat['linear'] == True else None
plt.plot([0, 0], [0, 0], color = 'yellow', label = 'orientation') if platWhat['orientation'] == True else None
plt.plot([0, 0], [0, 0], color = 'grey', label = 'path') if platWhat['paths'] == True else None
plt.legend(loc = 'lower right')

inFile = open(inFileName, 'r')
lines = inFile.readlines()

characters = {} # contains all characters that need plotted

for line in lines: 
    data = line.split(',') # split each line to get each value
    data = [float(i) for i in data if i not in ["True", "False", "True\n", "False\n"]] 

    ID = data[1]
    
    # add charecter to list if its not already in list
    if ID not in characters:
        steerType = data[9]
        characters[ID] = Character(steerType)

    characters[ID].rows += 1
    characters[ID].posX.append(data[2])
    characters[ID].posZ.append(data[3])
    characters[ID].velX.append(data[4])
    characters[ID].velZ.append(data[5])
    characters[ID].linX.append(data[6])
    characters[ID].linZ.append(data[7])
    characters[ID].orientationX.append(math.cos(data[8]) + data[2])
    characters[ID].orientationZ.append(math.sin(data[8]) + data[3])

# plotting data for each character
for ID in characters:
    character = characters[ID]

    character.plotLinear() if platWhat['linear'] == True else None
    character.plotVelo() if platWhat['velocity'] == True else None
    character.plotPosition()  if platWhat['position'] == True else None
    character.plotOrientation() if platWhat['orientation'] == True else None
    PathFollow.plotPath() if platWhat['paths'] == True else None


plt.gca().invert_yaxis()
plt.savefig("outputPlot.png")
plt.close()