# https://github.com/s3r5-robotics/Erebus-2022

import numpy as np
import math
import sys
import cv2 as cv
import copy
from controller import Robot
import struct


# File: "ClassifierTemplate.py"


tilesDict = {
        
        ("straight", "right"): np.array([[0, 0, 0, 0, 1, 1],
                                         [0, 0, 0, 0, 1, 1],
                                         [0, 0, 0, 0, 1, 1],
                                         [0, 0, 0, 0, 1, 1],
                                         [0, 0, 0, 0, 1, 1],
                                         [0, 0, 0, 0, 1, 1]]),

        ("straight", "left"): np.array([[1, 1, 0, 0, 0, 0],
                                        [1, 1, 0, 0, 0, 0],
                                        [1, 1, 0, 0, 0, 0],
                                        [1, 1, 0, 0, 0, 0],
                                        [1, 1, 0, 0, 0, 0],
                                        [1, 1, 0, 0, 0, 0]]),
                                
           ("straight", "up"): np.array([[1, 1, 1, 1, 1, 1],
                                         [1, 1, 1, 1, 1, 1],
                                         [0, 0, 0, 0, 0, 0],
                                         [0, 0, 0, 0, 0, 0],
                                         [0, 0, 0, 0, 0, 0],
                                         [0, 0, 0, 0, 0, 0]]),
                                
        ("straight", "down"): np.array([[0, 0, 0, 0, 0, 0],
                                        [0, 0, 0, 0, 0, 0],
                                        [0, 0, 0, 0, 0, 0],
                                        [0, 0, 0, 0, 0, 0],
                                        [1, 1, 1, 1, 1, 1],
                                        [1, 1, 1, 1, 1, 1]]),

        ("curved", "right-up"): np.array([[0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 1, 0, 0],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0]]),
        

        ("curved", "left-up"): np.array([[0, 0, 0, 0, 0, 0],
                                         [0, 0, 0, 0, 0, 0],
                                         [0, 0, 1, 0, 0, 0],
                                         [0, 0, 0, 0, 0, 0],
                                         [0, 0, 0, 0, 0, 0],
                                         [0, 0, 0, 0, 0, 0]]),
                                
        ("curved", "right-down"): np.array([[0, 0, 0, 0, 0, 0],
                                            [0, 0, 0, 0, 0, 0],
                                            [0, 0, 0, 0, 0, 0],
                                            [0, 0, 0, 0, 0, 0],
                                            [0, 0, 0, 1, 0, 0],
                                            [0, 0, 0, 0, 0, 0]]),
                                
        ("curved", "left-down"): np.array([[0, 0, 0, 0, 0, 0],
                                           [0, 0, 0, 0, 0, 0],
                                           [0, 0, 0, 0, 0, 0],
                                           [0, 0, 1, 0, 0, 0],
                                           [0, 0, 0, 0, 0, 0],
                                           [0, 0, 0, 0, 0, 0]]),
        
        ("curvedwall", "right-up"): np.array([[1, 1, 1, 0, -1, -1],
                                              [1, 1, 1, 0, -1, -1],
                                              [0, 0, 0, 0, 0, 0],
                                              [0, 0, 0, 0, 1, 1],
                                              [0, 0, 0, 0, 1, 1],
                                              [0, 0, 0, 0, 1, 1]]),
        

        ("curvedwall", "left-up"): np.array([[-1, -1, 0, 1, 1, 1],
                                             [-1, -1, 0, 1, 1, 1],
                                             [0, 0, 0, 0, 0, 0],
                                             [1, 1, 0, 0, 0, 0],
                                             [1, 1, 0, 0, 0, 0],
                                             [1, 1, 0, 0, 0, 0]]),
                                
        ("curvedwall", "right-down"): np.array([[0, 0, 0, 0, 1, 1],
                                                [0, 0, 0, 0, 1, 1],
                                                [0, 0, 0, 0, 1, 1],
                                                [0, 0, 0, 0, 0, 0],
                                                [1, 1, 1, 0, -1, -1],
                                                [1, 1, 1, 0, -1, -1]]),
                                
        ("curvedwall", "left-down"): np.array([[1, 1, 0, 0, 0, 0],
                                               [1, 1, 0, 0, 0, 0],
                                               [1, 1, 0, 0, 0, 0],
                                               [0, 0, 0, 0, 0, 0],
                                               [-1, -1, 0, 1, 1, 1],
                                               [-1, -1, 0, 1, 1, 1]])



            }
# File: "UtilityFunctions.py"


# Corrects the given angle in degrees to be in a range from 0 to 360
def normalizeDegs(ang):
    ang = ang % 360
    if ang < 0:
        ang += 360
    if ang == 360:
        ang = 0
    return ang

# Corrects the given angle in radians to be in a range from 0 to a full rotaion
def normalizeRads(rad):
    ang = radsToDegs(rad)
    normAng = normalizeDegs(ang)
    return degsToRads(normAng)

# Converts from degrees to radians
def degsToRads(deg):
    return deg * math.pi / 180

# Converts from radians to degrees
def radsToDegs(rad):
    return rad * 180 / math.pi

# Converts a number from a range of value to another
def mapVals(val, in_min, in_max, out_min, out_max):
    return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Gets x, y coordinates from a given angle in radians and distance
def getCoordsFromRads(rad, distance):
    y = float(distance * math.cos(rad))
    x = float(distance * math.sin(rad))
    return (x, y)

# Gets x, y coordinates from a given angle in degrees and distance
def getCoordsFromDegs(deg, distance):
    rad = degsToRads(deg)
    y = float(distance * math.cos(rad))
    x = float(distance * math.sin(rad))
    return (x, y)

def getRadsFromCoords(coords):
    return math.atan2(coords[0], coords[1])


def getDegsFromCoords(coords):
    rads = math.atan2(coords[0], coords[1])
    return radsToDegs(rads)

# Gets the distance to given coordinates
def getDistance(position):
    return math.sqrt((position[0] ** 2) + (position[1] ** 2))

# Checks if a value is between two values
def isInRange(val, minVal, maxVal):
    return minVal < val < maxVal

def roundDecimal(number, decimal):
    return (round(number * decimal) / decimal)

def multiplyLists(list1, list2):
    finalList = []
    for item1, item2 in zip(list1, list2):
        finalList.append(item1 * item2)
    return finalList

def sumLists(list1, list2):
    finalList = []
    for item1, item2 in zip(list1, list2):
        finalList.append(item1 + item2)
    return finalList

def substractLists(list1, list2):
    finalList = []
    for item1, item2 in zip(list1, list2):
        finalList.append(item1 - item2)
    return finalList

def divideLists(list1, list2):
    finalList = []
    for item1, item2 in zip(list1, list2):
        finalList.append(item1 / item2)
    return finalList

def crop_center(img, cropx):
    y, x = (40, 64)
    img[:, cropx:x - cropx]

# File: "PointCloudToGrid.py"






# Point class for point clou to grid converter
class PointCloudConverterPoint:

    def __init__(self, position):
        self.position = position
        self.count = 1

    # Defines the "==" operator
    def __eq__(self, other):
        return self.position == other.position

    # Defines what to print if I ask to print it
    def __repr__(self):
        return str(self.position + [self.count])
    def __str__(self):
        return str([self.position + [self.count]])


# Converts a point cloud in to tiles with positions
class PointCloudQueManager:

    def __init__(self, queSize, pointMultiplier, queStep = 1):
        self.queSize = queSize # Defines the size of the point cloud que
        self.que = [] # A que of point clouds
        self.queStep = queStep
        self.queActualStep = 0
        self.pointMultiplier = pointMultiplier
        for _ in range(queSize):
            self.que.append([])

    # Converts the point coords in to ints and multiplies it with the point multiplier
    def processPointCloud(self, pointCloud):

        finalPointCloud = []
        for point in pointCloud:
            fpoint = [round(point[0] * self.pointMultiplier), round(point[1] * self.pointMultiplier), 1]
            alreadyInFinal = False
            for finalPoint in finalPointCloud:
                if fpoint[:2] == finalPoint[:2]:
                    finalPoint[2] += 1
                    alreadyInFinal = True
            if not alreadyInFinal:
                finalPointCloud.append(fpoint)
        return finalPointCloud

    # Merges all the point clouds in the que and returns them
    def getTotalPointCloud(self):
        totalPointCloud = []
        isInFinal = False
        for pointCloud in self.que:
            for item in pointCloud:
                for totalItem in totalPointCloud:
                    if item[:2] == totalItem[:2]:
                        isInFinal = True
                        totalItem[2] += item[2]
                if not isInFinal:
                    totalPointCloud.append(item)
        #print("total point cloud: ", totalPointCloud)
        return totalPointCloud

    # Adds a new point cloud to the que and removes the last element
    def update(self, pointCloud):
        if self.queActualStep >= self.queStep:
            self.que.pop(0)
            self.que.append(self.processPointCloud(pointCloud))
            self.queActualStep = 0
        else:
            self.queActualStep += 1



class PointCloudDivider:
    def __init__(self, tileSize, pointMultiplier, pointPermanenceThresh):
        # Defines the size of a tie in the scale of the original coordinates
        self.tileSize = tileSize
         # Defines the number to multiply the coordinates to convert them in to ints
        self.pointMultiplier = pointMultiplier
        # Defines the number of times a point has to repeat to be considered definitive
        self.pointPermanenceThresh = pointPermanenceThresh
        self.realTileSize = self.tileSize * self.pointMultiplier



    def getTile(self, position):
        return (int(position[0] // self.realTileSize), int(position[1] // self.realTileSize))

    def getPosInTile(self, position):
        tile = self.getTile(position)
        tilePosition = multiplyLists(tile, [self.realTileSize, self.realTileSize])
        posInTile = [round(round(position[0]) - tilePosition[0]), round(round(position[1]) - tilePosition[1])]
        return posInTile

    # Returns a list with dictionarys containing the tile number and the position inside of said tile
    def getTiles(self, totalPointCloud):
        tiles = []
        #print("Total Point Cloud: ", totalPointCloud)
        for item in totalPointCloud:
            inTiles = False
            if item[2] >= self.pointPermanenceThresh:
                #print(item[:2])
                itemTile = self.getTile(item[:2])
                itemPosInTile = self.getPosInTile(item[:2])
                for tile in tiles:
                    if tile["tile"] == itemTile:
                        inTiles = True
                        tile["posInTile"].append(itemPosInTile)

                if not inTiles:
                    tiles.append({"tile":itemTile, "posInTile":[itemPosInTile]})
        #print("Tiles: ", tiles)
        return tiles

class PointCloudConverter:

    def __init__(self, tileSize, pointMultiplier):
        self.queManager = PointCloudQueManager(queSize=5, pointMultiplier=pointMultiplier)
        self.divider = PointCloudDivider(tileSize, pointMultiplier, pointPermanenceThresh=30)
        self.totalPointCloud = []


    def loadPointCloud(self, pointCloud):
        self.queManager.update(pointCloud)


    def getTilesWithPoints(self):
        self.totalPointCloud = self.queManager.getTotalPointCloud()
        return (self.divider.getTiles(self.totalPointCloud))


# Uses a dict of tile templates to return the elements present in a tile given points inside that tile
class Classifier:
    def __init__(self, tilesDict):
        self.tilesDict = tilesDict
        self.validTileDictKeys = list(self.tilesDict.keys())
        self.tilesDictPositivesCount = {}
        for key, value in self.tilesDict.items():
            count = 0
            for y in range(len(value)):
                for x in range(len(value[y])):
                    count += value[x][y]
            self.tilesDictPositivesCount[key] = count

    # Returns the similarity of the points imputted to the templates in percentages
    def getCalsificationPercentages(self, pointList):
        elementsDict = {}
        for key in self.validTileDictKeys:
            elementsDict[key] = 0

        for point in pointList:
            for key, modelGrid in self.tilesDict.items():
                elementsDict[key] += modelGrid[point[0]][point[1]]

        return elementsDict

# File: "StateMachines.py"
# Manages states
class StateManager:
    def __init__(self, initialState):
        self.state = initialState

    # Sets the state to a certain value
    def changeState(self, newState):
        self.state = newState
        return True

    # Checks if the state corresponds to a specific value
    def checkState(self, state):
        return self.state == state

# Makes it possible to run arbitrary code sequentially without interrupting other code that must run continuoulsy
class SequenceManager:
    def __init__(self):
        self.lineIdentifier = 0
        self.linePointer = 1
        self.done = False

    # Resets the sequence and makes it start from the first event
    def resetSequence(self):
        self.linePointer = 1
        print("----------------")
        print("reseting sequence")
        print("----------------")

    def seqResetSequence(self):
        if self.check():
            self.resetSequence()
            
            return True
        return False

    # This has to be at the start of any sequence of events
    def startSequence(self):
        self.lineIdentifier = 0
        self.done = False

    # Returns if the line pointer and identifier match and increases the identifier
    # Must be included at the end of any sequential function
    def check(self):
        self.done = False
        self.lineIdentifier += 1
        return self.lineIdentifier == self.linePointer

    # Changes to the next event
    def nextSeq(self):
        self.linePointer += 1
        self.done = True

    # returns if the sequence has reached its end
    def seqDone(self):
        return self.done

    # Can be used to make a function sequential or used in an if statement to make a code block sequential
    def simpleSeqEvent(self, function=None, *args, **kwargs):
        if self.check():
            if function is not None:
                function(*args, **kwargs)
            self.nextSeq()
            return True
        return False

    # The function inputted must return True when it ends
    def complexSeqEvent(self, function, *args, **kwargs):
        if self.check():
            if function(*args, **kwargs):
                self.nextSeq()
                return True
        return False
    
    # When inpuuted any function it returns a sequential version of it that can be used in a sequence
    def makeSimpleSeqEvent(self, function):
        def event(*args, **kwargs):
            if self.check():
                function(*args, **kwargs)
                self.nextSeq()
                return True
            return False
        return event

    # When inputted a function that returns True when it ends returns a sequential version of it that can be used in a sequence
    def makeComplexSeqEvent(self, function):
        def event(*args, **kwargs):
            if self.check():
                if function(*args, **kwargs):
                    self.nextSeq()
                    return True
            return False
        return event
# File: "Analysis.py"










# Class that defines a tile node in the grid
class TileNode:
    __wallFixtureTypes = ("harmed", "secure", "unharmed", "flammable_gas", "poison", "corrosive", "organic_proxide")
    # Tuple with all allowed tile types
    __allowedTypes = ("undefined", "normal", "hole", "swamp", "checkpoint", "start", "connection1-2", "connection2-3")
    __allowedCurvedWalls = ([1, 1], [-1, -1], [-1, 1], [-1, 1])
    __typesToNumbers = {"undefined": "0", "normal": "0", "hole": "2", "swamp": "3", "checkpoint": "4", "start": "5",
                        "connection1-2": "6", "connection1-3": "7", "connection2-3": "8"}

    def __init__(self, tileType="undefined", curvedWall=[0, 0], fixtures=[], obstacles=[]):
        self.dimensions = [0.06, 0.06]  # Dimensions of the tile
        self.__tileType = tileType  # Can be undefined, start, normal, swamp, hole, checkpoint, connection1-2, connection2-3
        self.traversed = False
        self.tileGroup = [0, 0]
        self.curvedWall = curvedWall  # if it is a tile with curved walls and curved wall position
        self.fixtures = fixtures  # List of all fixtures in walls adjacent to tile
        self.obstacles = obstacles  # List of obstacles in tile

    @property
    def tileType(self):
        return self.__tileType

    @tileType.setter
    def tileType(self, value):
        if self.__tileType in ("normal", "undefined") or value in ("start",):
            self.__tileType = value

    def getString(self):
        return self.__typesToNumbers[self.tileType]


# Class that defines a wall node in the grid
class WallNode:
    __wallFixtureTypes = ("H", "S", "U", "F", "P", "C", "O")

    def __init__(self, occupied=False, fixtures=[]):
        self.dimensions = [0.06, 0.06, 0.01]  # Dimensions of the wall
        self.__occupied = occupied  # If there is a wall. Can be True or false.
        self.isFloating = False  # If it is a floating wal
        self.traversed = False
        self.fixtures = fixtures  # List of all fixtures in wall

    @property
    def occupied(self):
        return self.__occupied

    @occupied.setter
    def occupied(self, value):
        if value and not self.traversed:
            self.__occupied = True
        else:
            self.__occupied = False

    def getString(self):
        if len(self.fixtures):
            returnString = "".join(self.fixtures)
        elif self.occupied:
            returnString = "1"
        else:
            returnString = "0"
        return returnString


# Class that defines a vortex node in the grid
class VortexNode:
    def __init__(self, occupied=False):
        self.dimensions = [0.01, 0.01, 0.06]  # Dimensions of the vortex
        self.occupied = occupied  # If there is a vortex. Can be True or false.
        self.traversed = False
        self.victimDetected = False
        self.tileType = "undefined"

    @property
    def occupied(self):
        return self.__occupied

    @occupied.setter
    def occupied(self, value):
        if value and not self.traversed:
            self.__occupied = True
        else:
            self.__occupied = False

    def getString(self):
        return str(int(self.occupied))


# A virtual representation of the competition map
class Grid:
    def __init__(self, chunk, initialSize):
        self.startingSize = initialSize  # The initial size of the grid, cant be 0 and has to be divisible by the size of the chunk
        self.size = [2, 2]  # The actual size of the grid
        self.offsets = [0, 0]  # Offsets of the grid to allow negative indexes
        self.grid = [[]]  # The grid containing the data
        self.chunk = chunk  # A chunk of nodes constituting the grid
        self.chunkSize = (len(chunk), len(chunk[0]))
        self.__constructGrid()

    # Given a string indicating direction returns an array directing to that direction
    def directionToNumber(self, direction):
        if direction == "center" or direction == "centre":
            n = [0, 0]
        elif direction == "right":
            n = [0, 1]
        elif direction == "left":
            n = [0, -1]
        elif direction == "up":
            n = [-1, 0]
        elif direction == "down":
            n = [1, 0]
        elif direction == "right-up" or direction == "up-right":
            n = [1, -1]
        elif direction == "right-down" or direction == "down-right":
            n = [1, 1]
        elif direction == "left-down" or direction == "down-left":
            n = [-1, 1]
        elif direction == "left-up" or direction == "up-left":
            n = [-1, -1]
        return n

    # Constructs the grid
    def __constructGrid(self):
        self.grid = copy.deepcopy(self.chunk)
        for _ in range((self.startingSize[0] // self.chunkSize[0]) - 1):
            self.addColumnAtEnd()
        for _ in range((self.startingSize[1] // self.chunkSize[1]) - 1):
            self.addRowAtEnd()

        self.offsets[0] = self.startingSize[0] // self.chunkSize[0]
        self.offsets[1] = self.startingSize[1] // self.chunkSize[1]
        if not self.offsets[0] % self.chunkSize[0]:
            self.offsets[0] -= 1
        if not self.offsets[1] % self.chunkSize[1]:
            self.offsets[1] -= 1

        self.size = self.startingSize

    # Adds a row at the end of the grid
    def addRowAtEnd(self):
        row = copy.deepcopy(self.chunk)
        if self.size[0] > 1:
            for _ in range((self.size[0] // self.chunkSize[0]) - 1):
                row = np.hstack((row.copy(), copy.deepcopy(self.chunk)))
            self.grid = np.vstack((self.grid.copy(), copy.deepcopy(row)))
            self.size[1] += self.chunkSize[0]

    # Adds a row at the start of the grid
    def addRowAtStart(self):
        row = copy.deepcopy(self.chunk)
        if self.size[0] > 1:
            for _ in range((self.size[0] // self.chunkSize[0]) - 1):
                row = np.hstack((row.copy(), copy.deepcopy(self.chunk)))
            self.grid = np.vstack((copy.deepcopy(row), self.grid.copy()))
            self.size[1] += self.chunkSize[0]
            self.offsets[1] += self.chunkSize[0]

    # Adds a column at the end of the grid
    def addColumnAtEnd(self):
        column = self.chunk.copy()
        if self.size[1] > 1:
            for _ in range((self.size[1] // self.chunkSize[1]) - 1):
                column = np.vstack((column.copy(), copy.deepcopy(self.chunk)))
            self.grid = np.hstack((self.grid.copy(), copy.deepcopy(column)))
            self.size[0] += self.chunkSize[1]

    # Adds a column at the start of the grid
    def addColumnAtStart(self):
        column = copy.deepcopy(self.chunk)
        if self.size[1] > 1:
            for _ in range((self.size[1] // self.chunkSize[1]) - 1):
                column = np.vstack((column.copy(), copy.deepcopy(self.chunk)))
            self.grid = np.hstack((copy.deepcopy(column), self.grid.copy()))
            self.size[0] += self.chunkSize[1]
            self.offsets[0] += self.chunkSize[1]

    # returns the node in the position in the grid taking in to account offsets
    def getRawNode(self, position):
        x = position[0] + self.offsets[0]
        y = position[1] + self.offsets[1]
        return self.grid[y][x]

    # Sets a value in the position in the grid taking in to account offsets
    def setRawNode(self, position, value):
        x = position[0] + self.offsets[0]
        y = position[1] + self.offsets[1]
        self.grid[y][x] = value

    def processedToRawNode(self, position, side=[0, 0]):
        if isinstance(side, str):
            x = position[0] * self.chunkSize[0] + self.directionToNumber(side)[0]
            y = position[1] * self.chunkSize[1] + self.directionToNumber(side)[1]
        else:
            x = position[0] * self.chunkSize[0] + side[0]
            y = position[1] * self.chunkSize[1] + side[1]
        if x < self.offsets[0] * -1:
            raise IndexError("Index too small for list with min index " + str(self.offsets[0] * -1))
        if y < self.offsets[1] * -1:
            raise IndexError("Index too small for list with min index " + str(self.offsets[0] * -1))
        return (x, y)

    def rawToProcessedNode(self, rawNode):
        x = rawNode[0] // self.chunkSize[0]
        y = rawNode[1] // self.chunkSize[1]
        sideX = rawNode[0] % self.chunkSize[0]
        sideY = rawNode[1] % self.chunkSize[1]
        quadrant = [0, 0]
        if sideX > 0: quadrant[0] = 1
        if sideY > 0: quadrant[1] = 1
        return (x, y), quadrant

    # Returns a node given the position of a tile and directions to indicate walls and vertices
    def getNode(self, position, side=[0, 0]):
        return self.getRawNode(self.processedToRawNode(position, side))

    # Sets a node given the position of a tile and directions to indicate walls and vertices
    def setNode(self, position, value, side=[0, 0]):
        self.setRawNode(self.processedToRawNode(position, side), value)

    def getArrayRepresentation(self):
        grid = []
        for y in self.grid:
            row = []
            for node in y:
                row.append(node.getString())
            grid.append(row)
        return np.array(grid)

    def getNumpyPrintableArray(self):
        printableArray = np.zeros(self.size, np.uint8)
        for y in range(len(self.grid)):
            for x, node in enumerate(self.grid[y]):

                if isinstance(node, TileNode):
                    if node.tileType == "start":
                        printableArray[x][y] = 100
                    elif node.tileType == "hole":
                        # print("NEW HOLE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        printableArray[x][y] = 255
                    elif node.tileType == "checkpoint":
                        printableArray[x][y] = 60
                    elif node.tileType == "swamp":
                        printableArray[x][y] = 80

                    elif node.tileType in ("connection1-2", "connection2-3", "connection1-3"):
                        printableArray[x][y] = 120
                    elif node.traversed:
                        printableArray[x][y] = 150

                elif isinstance(node, VortexNode):
                    if node.tileType == "start":
                        printableArray[x][y] = 100
                    elif node.occupied:
                        printableArray[x][y] = 255
                    elif node.traversed:
                        printableArray[x][y] = 150
                    else:
                        printableArray[x][y] = 50

                elif isinstance(node, WallNode):
                    if node.occupied:
                        printableArray[x][y] = 255
                    elif node.traversed:
                        printableArray[x][y] = 150
                    else:
                        printableArray[x][y] = 50

        return np.flip(printableArray, 1)


# aStarNode class for A* pathfinding (Not to be confused with the node grid)
class aStarNode():
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


# Finds the best path to follow
class PathFinder:
    def __init__(self, vortexNode, wallNode, tileNode, grid, searchLimit, startNode):
        self.grid = grid
        self.startVortex = [0, 0]
        self.prevVortex = [0, 0]
        self.objectiveVortex = [0, 0]
        self.vortexNode = vortexNode
        self.wallNode = wallNode
        self.tileNode = tileNode
        self.searchLimit = searchLimit
        self.startNode = startNode

    def isTraversable(self, index):
        node = self.grid.getRawNode(index)
        if isinstance(node, TileNode):
            raise ValueError("Invalid instance")
            return node.tileType != "hole"
        if isinstance(node, WallNode):
            raise ValueError("Invalid instance")
            return not node.occupied
        if isinstance(node, VortexNode):
            if node.occupied:
                return False
            traversable = True
            for adjacentIndex in ((-1, 1), (1, -1), (1, 1), (-1, -1), (0, 1), (0, -1), (1, 0), (-1, 0)):
                adjacent = self.grid.getRawNode((index[0] + adjacentIndex[0], index[1] + adjacentIndex[1]))
                if isinstance(adjacent, TileNode):
                    if adjacent.tileType == "hole":
                        traversable = False
                elif isinstance(adjacent, WallNode):
                    if adjacent.occupied:
                        traversable = False
                else:
                    raise ValueError(("invalid instance: " + str(type(adjacent))))
            return traversable
        return False

    # Returns a list of tuples as a path from the given start to the given end in the given maze
    def aStar(self, start, end):
        # Create start and end node
        startNode = aStarNode(None, (start[0], start[1]))
        startNode.g = startNode.h = startNode.f = 0
        endNode = aStarNode(None, (end[0], end[1]))
        endNode.g = endNode.h = endNode.f = 0
        # Initialize open and closed list
        openList = []
        closedList = []
        # Add the start node
        openList.append(startNode)
        # Loop until end
        while len(openList) > 0:
            # Get the current node
            currentNode = openList[0]
            currentIndex = 0
            for index, item in enumerate(openList):
                if item.f < currentNode.f:
                    currentNode = item
                    currentIndex = index
            # Pop current off open list, add to closed list
            openList.pop(currentIndex)
            closedList.append(currentNode)
            # If found the goal
            if currentNode == endNode:
                path = []
                current = currentNode
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]  # Return reversed path
            # Generate children
            children = []
            for newPosition in ((0, 1), (0, -1), (-1, 0), (1, 0)):  # Adjacent squares
                # Get node position
                nodePosition = (
                currentNode.position[0] + (newPosition[0] * 2), currentNode.position[1] + (newPosition[1] * 2))
                # Make sure walkable terrain
                if not self.isTraversable(nodePosition):
                    continue
                # Create new node
                newNode = aStarNode(currentNode, nodePosition)
                # Append
                children.append(newNode)
            # Loop through children
            for child in children:
                continueLoop = False
                # Child is on the closed list
                for closedChild in closedList:
                    if child == closedChild:
                        continueLoop = True
                        break
                # Create the f, g, and h values
                child.g = currentNode.g + 1
                child.h = ((child.position[0] - endNode.position[0]) ** 2) + (
                    (child.position[1] - endNode.position[1]) ** 2)
                child.f = child.g + child.h
                # Child is already in the open list
                for openNode in openList:
                    if child == openNode and child.g > openNode.g:
                        continueLoop = True
                        break
                if continueLoop:
                    continue
                # Add the child to the open list
                openList.append(child)

    def isBfsAddable(self, index):
        node = self.grid.getRawNode(index)
        if isinstance(node, self.vortexNode):
            for adjacentPos in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                adjacent = [index[0] + adjacentPos[0], index[1] + adjacentPos[1]]
                if not self.grid.getRawNode(adjacent).traversed:
                    return True
            return False
        else:
            return False

    # Breath First Search algorithm
    # Returns the tiles with in order and with the distance of each one
    def bfs(self, start, limit="undefined"):
        visited = []
        queue = []
        found = []
        start = [start[0], start[1], 0]
        visited.append(start)
        queue.append(start)
        while queue:
            if len(found) > 3:
                break
            coords = queue.pop(0)
            y = coords[1]
            x = coords[0]
            dist = coords[2]
            if limit != "undefined":
                if dist > limit:
                    break

            if self.isBfsAddable(coords):
                found.append(coords)
            for newPosition in (0, 1), (0, -1), (-1, 0), (1, 0):
                neighbour = [x + newPosition[0] * 2, y + newPosition[1] * 2, dist + 1]
                inList = False
                for node in visited:
                    if node[0] == neighbour[0] and node[1] == neighbour[1]:
                        inList = True
                        break
                if inList:
                    continue

                # Make sure walkable terrain
                try:
                    if self.isTraversable(neighbour):
                        visited.append(neighbour)
                        queue.append(neighbour)
                except IndexError:
                    pass
        return found

    def getPreferabilityScore(self, node):
        pass

    def setStartVortex(self, startRawVortexPos):
        if not isinstance(self.grid.getRawNode(startRawVortexPos), self.vortexNode):
            raise ValueError("Inputed position does not correspond to a vortex node")
        if self.startVortex != startRawVortexPos:
            self.prevVortex = self.startVortex

        self.startVortex = startRawVortexPos
        if not self.isTraversable(startRawVortexPos):
            print("INITIAL VORTEX NOT TRAVERSABLE")

    def setGrid(self, grid):
        self.grid = grid

    def getBestPath(self, orientation):
        bfsLimits = ("undefined",)
        possibleNodes = []
        if self.isTraversable(self.startVortex):
            bfsStart = self.startVortex
        else:
            bfsStart = self.prevVortex
        for limit in bfsLimits:
            possibleNodes = self.bfs(bfsStart, limit)
            if len(possibleNodes) > 0:
                break

        if len(possibleNodes) > 0:
            bestNode = possibleNodes[0]
            if bestNode[:2] == list(self.startVortex):
                bestNode = possibleNodes[1]
            for posNode in possibleNodes:
                diff = substractLists(self.startVortex, posNode[:2])
                # print("Diff:", diff)
                # print("Multiplied orientation: ", multiplyLists(orientation, [-2, -2]))
                if posNode[2] > 1:
                    break

                elif diff == multiplyLists(orientation, [-2, -2]):
                    bestNode = posNode
                    break
        else:
            bestNode = self.startNode

        bestPath = self.aStar(bfsStart, bestNode)
        print("BFS NODES: ", possibleNodes)
        print("Best Node:", bestNode)
        print("AStar PATH: ", bestPath)
        print("Start Vortex: ", self.startVortex)
        return bestPath


class Analyst:
    def __init__(self, tileSize):
        # Important variables
        self.tileSize = tileSize
        self.posMultiplier = 100
        # Grid
        gridChunk = np.array([[VortexNode(), WallNode()],
                              [WallNode(), TileNode()]])
        self.grid = Grid(gridChunk, (100, 100))
        # Converter
        self.converter = PointCloudConverter(self.tileSize, pointMultiplier=self.posMultiplier)
        # Classifier
        self.classifier = Classifier(tilesDict)
        # Path finder
        self.pathFinder = PathFinder(VortexNode, WallNode, TileNode, self.grid, 10, [0, 0])
        self.pathFinder.setStartVortex((1, 1))
        # self.pathFinder.getBestPath()
        # Variables
        self.direction = None
        self.__bestPath = []
        self.calculatePath = True
        self.stoppedMoving = False
        self.pathIndex = 0
        self.positionReachedThresh = 0.01
        self.prevRawNode = [0, 0]
        self.ended = False

    def getBestPathSafe(self):
        if self.__bestPath is None:
            self.__bestPath = []

        return self.__bestPath

    def getRawAdjacents(self, node, side):
        rawNode = self.grid.processedToRawNode(node, side)
        adjacents = []
        for i in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            adjacents.append(sumLists(rawNode, i))
        return adjacents

    def loadPointCloud(self, pointCloud):
        self.converter.loadPointCloud(pointCloud)
        tilesWithPoints = self.converter.getTilesWithPoints()
        # print("tilesWithPoints: ", tilesWithPoints)
        for item in tilesWithPoints:
            percentages = self.classifier.getCalsificationPercentages(item["posInTile"])
            # print("percentages: ", percentages)
            for key, value in percentages.items():
                wallType, orientation = key
                if wallType == "straight":

                    if value >= 5:
                        self.grid.getNode(item["tile"], orientation).occupied = True
                        for adjacent in self.getRawAdjacents(item["tile"], orientation):
                            adjNode = self.grid.getRawNode(adjacent)
                            if isinstance(adjNode, VortexNode):
                                adjNode.occupied = True

                elif wallType == "curved":
                    if value > 0:
                        # print("Robot tile", self.tile)
                        # print("Curved", orientation, "in sight at", item["tile"])
                        if percentages[("curvedwall", orientation)] > 6:
                            walls = orientation.split("-")
                            for wall in walls:
                                self.grid.getNode(item["tile"], wall).occupied = True

    def loadColorDetection(self, colorSensorPosition, tileType):
        convPos = self.getTile(colorSensorPosition)
        self.grid.getNode(convPos).tileType = tileType
        """
        if tileType == "hole":
            self.calculatePath = True
        """

    def getQuadrant(self, posInTile):
        if posInTile[0] > self.tileSize / 2:
            x = 1
        else:
            x = -1
        if posInTile[1] > self.tileSize / 2:
            y = 1
        else:
            y = -1
        return [x, y]

    def getTile(self, position):
        return (int(position[0] // self.tileSize), int(position[1] // self.tileSize))

    def getPosInTile(self, position):
        return ((position[0] % self.tileSize), (position[1] % self.tileSize))

    def getVortexPosInTile(self, quadrant):
        return [(self.tileSize / 2) + (quadrant[0] * (self.tileSize / 2)),
                (self.tileSize / 2) + (quadrant[1] * (self.tileSize / 2))]

    def getTilePos(self, tile):
        return (tile[0] * self.tileSize, tile[1] * self.tileSize)

    def multiplyPos(self, position):
        return (position[0] * self.posMultiplier, position[1] * self.posMultiplier)

    def getStartRawNodePos(self):
        node, quadrant = self.grid.rawToProcessedNode(self.pathFinder.startVortex)
        nodePos = self.getTilePos(node)

        vortexPos = self.getVortexPosInTile(quadrant)
        return [nodePos[0] + vortexPos[0], nodePos[1] + vortexPos[1]]

    def getQuadrantFromDegs(self, degs):
        if 315 <= degs < 360 or 0 <= degs < 45:
            quadrant = (0, 1)
        elif 45 <= degs < 135:
            quadrant = (1, 0)
        elif 135 <= degs < 225:
            quadrant = (0, -1)
        elif 255 <= 315:
            quadrant = (-1, 0)
        return quadrant

    def blockFront(self):
        front = [self.startRawNode[0] + (self.direction[0] * 2), self.startRawNode[1] + (self.direction[1] * 2)]
        self.grid.getRawNode(front).occupied = True

    def registerStart(self):
        self.pathFinder.startNode = self.startRawNode
        self.grid.getRawNode(self.startRawNode).tileType = "start"
        for i in ((1, 1), (-1, -1), (-1, 1), (1, -1)):
            adjacent = sumLists(self.startRawNode, i)
            self.grid.getRawNode(adjacent).tileType = "start"

    def registerVictim(self):
        self.grid.getRawNode(self.startRawNode).victimDetected = True

    def isRegisteredVictim(self):
        return self.grid.getRawNode(self.startRawNode).victimDetected

    def getArrayRepresentation(self):
        return self.grid.getArrayRepresentation()

    def update(self, position, rotation):
        self.direction = self.getQuadrantFromDegs(rotation)

        posInTile = self.getPosInTile(position)
        quadrant = self.getQuadrant(posInTile)
        self.tile = self.getTile(position)
        startRawNode = self.grid.processedToRawNode(self.tile, quadrant)
        self.startRawNode = startRawNode
        # print("startRawNode: ", startRawNode)
        self.pathFinder.setStartVortex(startRawNode)
        self.pathFinder.setGrid(self.grid)

        vortexPosInTile = self.getVortexPosInTile(quadrant)
        diff = [vortexPosInTile[0] - posInTile[0], vortexPosInTile[1] - posInTile[1]]
        distToVortex = getDistance(diff)
        if distToVortex < self.positionReachedThresh:
            self.grid.getRawNode(self.startRawNode).traversed = True
            for adjacentPos in ((1, 1), (-1, 1), (1, -1), (-1, -1), (0, 1), (1, 0), (-1, 0), (0, -1)):
                adjacent = [self.startRawNode[0] + adjacentPos[0], self.startRawNode[1] + adjacentPos[1]]
                self.grid.getRawNode(adjacent).traversed = True

        if self.stoppedMoving:
            self.blockFront
            self.calculatePath = True

        if len(self.getBestPathSafe()):
            print("Dist to Vortex: ", distToVortex)
            if distToVortex < self.positionReachedThresh and startRawNode == self.__bestPath[self.pathIndex]:
                self.pathIndex += 1

        print("PathLenght: ", len(self.getBestPathSafe()))
        if self.pathIndex >= len(self.getBestPathSafe()):
            self.calculatePath = True

        else:
            bestNode = self.getBestRawNodeToMove()
            if bestNode is not None:
                if not self.pathFinder.isTraversable(bestNode):
                    self.calculatePath = True

        if self.calculatePath:
            # print("Calculating path")
            self.__bestPath = self.pathFinder.getBestPath(self.direction)
            self.pathIndex = 0
            print("update - self.calculatePath => ", self.__bestPath, (not self.__bestPath is None) and len(self.getBestPathSafe()) < 2)
            if len(self.getBestPathSafe()) < 2:
                self.ended = True
            self.calculatePath = False

    def getBestRawNodeToMove(self):
        # print("Best path: ", self.__bestPath)
        # print("Index: ", self.pathIndex)
        if len(self.getBestPathSafe()):
            return self.__bestPath[self.pathIndex]
        else:
            return None

    def getBestPosToMove(self):
        bestRawNode = self.getBestRawNodeToMove()
        # print("BEST PATH: ", bestRawNode)
        if bestRawNode is None:
            return None
        node, quadrant = self.grid.rawToProcessedNode(bestRawNode)

        nodePos = self.getTilePos(node)

        vortexPos = self.getVortexPosInTile(quadrant)
        return [nodePos[0] + vortexPos[0], nodePos[1] + vortexPos[1]]
        # return nodePos

    def getBestPoses(self):
        bestPoses = []
        for bestRawNode in self.__bestPath:
            node, quadrant = self.grid.rawToProcessedNode(bestRawNode)

            nodePos = self.getTilePos(node)

            vortexPos = self.getVortexPosInTile(quadrant)
            # print("Vortex pos: ", vortexPos)
            # return
            bestPoses.append([nodePos[0] + vortexPos[0], nodePos[1] + vortexPos[1]])
        return bestPoses

    def getGrid(self):
        return self.grid.grid

    def showGrid(self):
        None
        # cv.imshow("Analyst grid",
        #    cv.resize(self.grid.getNumpyPrintableArray(), (400, 400), interpolation=cv.INTER_NEAREST))

# File: "CameraDetection.py"
# noinspection PyInterpreter




class Listener:
    def __init__(self, lowerHSV, upperHSV):
        self.lower = np.array(lowerHSV)
        self.upper = np.array(upperHSV)

    def getFiltered(self, img):
        hsv_image = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv_image, self.lower, self.upper)
        #imgResult = cv.bitwise_and(img, img, mask=mask)
        return mask

class VictimClassifier:
    def __init__(self):
        self.redListener = Listener(lowerHSV=(73, 157, 127), upperHSV=(179, 255, 255))
        self.yellowListener = Listener(lowerHSV=(0, 157, 82), upperHSV=(40, 255, 255))
        self.whiteListener = Listener(lowerHSV=(0, 0, 200), upperHSV=(0, 255, 255))
        self.blackListener = Listener(lowerHSV=(0, 0, 0), upperHSV=(0, 255, 10))
        self.victimLetterListener = Listener(lowerHSV=(0, 0, 0), upperHSV=(5, 255, 100))

    def isClose(self, height):
        print(f"Current height: {height}")
        return height > 45

    def isInCenter(self, pos):
        print(f"Current pos1: {pos[1]}")
        return 15 < pos[1] < 70

    def getCloseVictims(self, victimPoses, victimImages):
        finalVictims = []
        for pos, img in zip(victimPoses, victimImages):
            height = img.shape[0]
            if self.isClose(height) and self.isInCenter(pos):
                finalVictims.append(img)
        return finalVictims



    def getSumedFilters(self, images):
        finalImg = images[0]
        for index, image in enumerate(images):
            finalImg += image
            #cv.imshow(str(index), image)
        return finalImg


    def filterVictims(self, poses, images):
        finalPoses = []
        finalImages = []
        for pos, img in zip(poses, images):
            print(f"Current victim pos0: {pos[0]}")
            if 25 < pos[0] < 60:
                finalPoses.append(pos)
                finalImages.append(img)

        return finalPoses, finalImages

    def getVictimImagesAndPositions(self, image):
        binaryImages = [self.redListener.getFiltered(image),
                        self.yellowListener.getFiltered(image),
                        self.whiteListener.getFiltered(image),
                        self.blackListener.getFiltered(image)]

        binaryImage = self.getSumedFilters(binaryImages)
        # cv.imshow("binaryImage", binaryImage)

        # Encuentra los contornos, aunque se puede confundir con el contorno de la letra
        contours, _ = cv.findContours(binaryImage, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # Pra evitar la confusion dibuja rectangulos blancos donde estan los contornos en la imagen y despues vuelve a
        # sacar los contornos para obtener solo los del rectangulo, no los de las letras.
        for c0 in contours:
            x, y, w, h = cv.boundingRect(c0)
            cv.rectangle(binaryImage, (x, y), (x + w, y + h), (225, 255, 255), -1)
        # cv.imshow("thresh2", binaryImage)
        contours, _ = cv.findContours(binaryImage, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # saca las medidas y la posicion de los contornos y agrega a la lista de imagenes la parte esa de la imagen original
        # Tambien anade la posicion de cada recuadro en la imagen original
        finalPoses = []
        finalImages = []
        for c in contours:
            x, y, w, h = cv.boundingRect(c)
            finalImages.append(image[y:y + h, x:x + w])
            finalPoses.append((y, x))

        return self.filterVictims(finalPoses, finalImages)

    def cropWhite(self, binaryImg):
        white = 255
        #print(conts)
        maxX = 0
        maxY = 0
        minX = binaryImg.shape[0]
        minY = binaryImg.shape[1]
        for yIndex, row in enumerate(binaryImg):
            for xIndex, pixel in enumerate(row):
                if pixel == white:
                    maxX = max(maxX, xIndex)
                    maxY = max(maxY, yIndex)
                    minX = min(minX, xIndex)
                    minY = min(minY, yIndex)

        return binaryImg[minY:maxY, minX:maxX]

    def classifyHSU(self, img):
        white = 255

        img =  cv.resize(img, (100, 100), interpolation=cv.INTER_AREA)
        #conts, h = cv.findContours(thresh1, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        binary = self.victimLetterListener.getFiltered(img)

        letter1 = self.cropWhite(binary)
        letter1 = cv.resize(letter1, (100, 100), interpolation=cv.INTER_AREA)
        letter = letter1[:,10:90]
        letter = self.cropWhite(letter)
        letter = cv.resize(letter, (100, 100), interpolation=cv.INTER_AREA)
        # cv.imshow("letra", letter)
        # #cv.imshow("letra1", letter1)
        # cv.imshow("thresh", binary)
        letterColor = cv.cvtColor(letter, cv.COLOR_GRAY2BGR)
        areaWidth = 20
        areaHeight = 30
        areas = {
            "top": ((0, areaHeight),(50 - areaWidth // 2, 50 + areaWidth // 2)),
            "middle": ((50 - areaHeight // 2, 50 + areaHeight // 2), (50 - areaWidth // 2, 50 + areaWidth // 2)),
            "bottom": ((100 - areaHeight, 100), (50 - areaWidth // 2, 50 + areaWidth // 2 ))
            }
        images = {
            "top": letter[areas["top"][0][0]:areas["top"][0][1], areas["top"][1][0]:areas["top"][1][1]],
            "middle": letter[areas["middle"][0][0]:areas["middle"][0][1], areas["middle"][1][0]:areas["middle"][1][1]],
            "bottom": letter[areas["bottom"][0][0]:areas["bottom"][0][1], areas["bottom"][1][0]:areas["bottom"][1][1]]
            }
        cv.rectangle(letterColor,(areas["top"][1][0], areas["top"][0][0]), (areas["top"][1][1], areas["top"][0][1]), (0, 255, 0), 1)
        cv.rectangle(letterColor, (areas["middle"][1][0], areas["middle"][0][0]), (areas["middle"][1][1], areas["middle"][0][1]), (0, 0, 255), 1)
        cv.rectangle(letterColor,(areas["bottom"][1][0], areas["bottom"][0][0]), (areas["bottom"][1][1], areas["bottom"][0][1]), (225, 0, 255), 1)
        counts = {}
        for key in images.keys():
            count = 0
            for row in images[key]:
                for pixel in row:
                    if pixel == white:
                        count += 1
            counts[key] = count > 20
        letters = {
            "H":{'top': False, 'middle': True, 'bottom': False},
            "S":{'top': True, 'middle': True, 'bottom': True},
            "U":{'top': False, 'middle': False, 'bottom': True}
            }

        finalLetter = "S"
        for letterKey in letters.keys():
            if counts == letters[letterKey]:
                finalLetter = letterKey
                break

        #print(counts)
        #print(finalLetter)
        return finalLetter

    def isPoison(self, blackPoints, whitePoints):
        return blackPoints < 600 and whitePoints > 700 and whitePoints < 4000

    def isVictim(self, blackPoints, whitePoints):
        return whitePoints > 5000 and 2000 > blackPoints > 100

    def isCorrosive(self, blackPoints, whitePoints):
        return 700 < whitePoints < 2500 and 1000 < blackPoints < 2500

    def isFlammable(self, redPoints, whitePoints):
        return redPoints and whitePoints

    def isOrganicPeroxide(self, redPoints, yellowPoints):
        return redPoints and yellowPoints

    def classifyVictim(self, img):
        letter = "N"
        image = cv.resize(img, (100, 100), interpolation=cv.INTER_AREA)
        colorImgs = {
        "red" : self.redListener.getFiltered(image),
        "yellow" : self.yellowListener.getFiltered(image),
        "white" : self.whiteListener.getFiltered(image),
        "black" : self.blackListener.getFiltered(image)}

        colorPointCounts = {}
        for key, img in colorImgs.items():
            print("Shpae idisjfdj:", img.shape)
            sought = 255
            all_points = np.where(img == 255)
            all_points = all_points[0]
            count = len(all_points)

            colorPointCounts[key] = count

        print(colorPointCounts)
        if self.isPoison(colorPointCounts["black"], colorPointCounts["white"]):
            print("Poison!")
            letter = "P"

        if self.isVictim(colorPointCounts["black"], colorPointCounts["white"]):
            # cv.imshow("black filter:", colorImgs["black"])
            letter = self.classifyHSU(image)
            print("Victim:", letter)


        if self.isCorrosive(colorPointCounts["black"], colorPointCounts["white"]):
            print("Corrosive!")
            letter = "C"

        if self.isOrganicPeroxide(colorPointCounts["red"], colorPointCounts["yellow"]):
            print("organic peroxide!")
            letter = "O"

        if self.isFlammable(colorPointCounts["red"], colorPointCounts["white"]):
            print("Flammable!")
            letter = "F"

        return letter

# File: "RobotLayer.py"











# Captures images and processes them
class Camera:
    def __init__(self, camera, timeStep):
        self.camera = camera
        self.camera.enable(timeStep)
        self.height = self.camera.getHeight()
        self.width = self.camera.getWidth()

    # Gets an image from the raw camera data
    def getImg(self):
        imageData = self.camera.getImage()
        return np.array(np.frombuffer(imageData, np.uint8).reshape((self.height, self.width, 4)))

    def getImgBuffered(self):
        imageData = self.camera.getImage()
        return np.frombuffer(imageData, np.uint8).reshape((self.height, self.width, 4))


# Tracks global rotation
class Gyroscope:
    def __init__(self, gyro, index, timeStep):
        self.sensor = gyro
        self.sensor.enable(timeStep)
        self.oldTime = 0.0
        self.index = index
        self.rotation = 0
        self.lastRads = 0

    # Do on every timestep
    def update(self, time):
        #print("Gyro Vals: " + str(self.sensor.getValues()))
        timeElapsed = time - self.oldTime  # Time passed in time step
        radsInTimestep = (self.sensor.getValues())[self.index] * timeElapsed
        self.lastRads = radsInTimestep
        finalRot = self.rotation + radsInTimestep
        self.rotation = normalizeRads(finalRot)
        self.oldTime = time

    # Gets the actual angular Velocity
    def getDiff(self):
        if self.lastRads < 0:
            return self.lastRads * -1

        return self.lastRads

    # Returns the rotation on degrees
    def getDegrees(self):
        return radsToDegs(self.rotation)

    # Returns the rotation on radians
    def getRadians(self):
        return self.rotation

    # Sets the rotation in radians
    def setRadians(self, rads):
        self.rotation = rads

    # Sets the rotation in degrees
    def setDegrees(self, degs):
        self.rotation = degsToRads(degs)


# Tracks global position
class Gps:
    def __init__(self, gps, timeStep, coordsMultiplier=1):
        self.gps = gps
        self.gps.enable(timeStep)
        self.multiplier = coordsMultiplier
        self.__prevPosition = []
        self.position = self.getPosition()

    # updates gps, must run every timestep
    def update(self):
        self.__prevPosition = self.position
        self.position = self.getPosition()

    # Returns the global position
    def getPosition(self):
        vals = self.gps.getValues()
        return [vals[0] * self.multiplier, vals[2] * self.multiplier]

    # Returns the global rotation according to gps
    def getRotation(self):
        if self.__prevPosition != self.position:
            posDiff = ((self.position[0] - self.__prevPosition[0]), (self.position[1] - self.__prevPosition[1]))
            accuracy = getDistance(posDiff)
            #print("accuracy: " + str(accuracy))
            if accuracy > 0.001:
                degs = getDegsFromCoords(posDiff)
                return normalizeDegs(degs)
        return None


# Returns a point cloud of the detctions it makes
class Lidar():
    def __init__(self, device, timeStep):
        self.device = device
        self.device.enable(timeStep)
        self.x = 0
        self.y = 0
        self.z = 0
        self.rotation = 0
        self.fov = device.getFov()
        self.verticalFov = self.device.getVerticalFov()
        self.horizontalRes = self.device.getHorizontalResolution()
        self.verticalRes = self.device.getNumberOfLayers()
        self.hRadPerDetection = self.fov / self.horizontalRes
        self.vRadPerDetection = self.verticalFov / self.verticalRes
        self.detectRotOffset = 0 #math.pi * 0.75
        self.maxDetectionDistance = 0.06 * 10

    # Does a detection pass and returns a point cloud with the results
    def getPointCloud(self, layers=range(3)):
        #(degsToRads(359 - radsToDegs(self.rotation)))
        #rangeImage = self.device.getRangeImageArray()
        #print("Lidar vFov: ", self.verticalFov/ self.verticalRes)
        pointCloud = []

        for layer in layers:
            actualVDetectionRot = (layer * self.vRadPerDetection) + self.verticalFov / 2
            depthArray = self.device.getLayerRangeImage(layer)
            actualHDetectionRot = self.detectRotOffset + ((2 * math.pi) - self.rotation)
            for item in depthArray:
                if item <= self.maxDetectionDistance:
                    if item != float("inf") and item != float("inf") * -1 and item != 0:
                        x = item * math.cos(actualVDetectionRot)
                        x += 0.06 * 0.2
                        coords = getCoordsFromRads(actualHDetectionRot, x)
                        pointCloud.append([coords[0] - 0, (coords[1] * -1) - 0])
                actualHDetectionRot += self.hRadPerDetection
        return pointCloud

    # Sets the rotation of the sensors in radians
    def setRotationRadians(self, rads):
        self.rotation = rads

    # Sets the rotation of the sensors in degrees
    def setRotationDegrees(self, degs):
        self.rotation = degsToRads(degs)


# Controlls a wheel
class Wheel:
    def __init__(self, wheel, maxVelocity):
        self.maxVelocity = maxVelocity
        self.wheel = wheel
        self.velocity = 0
        self.wheel.setPosition(float("inf"))
        self.wheel.setVelocity(0)

    # Moves the wheel at a ratio of the maximum speed (between 0 and 1)
    def move(self, ratio):
        if ratio > 1:
            ratio = 1
        elif ratio < -1:
            ratio = -1
        self.velocity = ratio * self.maxVelocity
        self.wheel.setVelocity(self.velocity)

# Reads the colour sensor
class ColourSensor:
    def __init__(self, sensor, distancefromCenter, timeStep):
        self.distance = distancefromCenter
        self.sensor = sensor
        self.sensor.enable(timeStep)
        self.r = 0
        self.g = 0
        self.b = 0

    def getPosition(self, robotGlobalPosition, robotGlobalRotation):
        realPosition = getCoordsFromDegs(robotGlobalRotation, self.distance)
        return [robotGlobalPosition[0] + realPosition[0], robotGlobalPosition[1] + realPosition[1]]

    def __update(self):
        colour = self.sensor.getImage()
        print("Colourimg:", colour)
        self.r = self.sensor.imageGetRed(colour, 1, 0, 0)
        self.g = self.sensor.imageGetGreen(colour, 1, 0, 0)
        self.b = self.sensor.imageGetBlue(colour, 1, 0, 0)
        print("Colour:", self.r, self.g, self.b)

    def __isTrap(self):
        return (35 < self.r < 45 and 35 < self.g < 45)
    def __isSwamp(self):
        return (200 < self.r < 210 and 165 < self.g < 175 and 95 < self.b < 105)
    def __isCheckpoint(self):
        return (self.r > 232 and self.g > 232 and self.b > 232)
    def __isNormal(self):
        return self.r == 227 and self.g == 227
    def __isBlue(self):
        return (55 < self.r < 65 and 55 < self.g < 65 and 245 < self.b < 255)
    def __isPurple(self):
        return (135 < self.r < 145 and 55 < self.g < 65 and 215 < self.b < 225)
    def __isRed(self):
        return (245 < self.r < 255 and 55 < self.g < 65 and 55 < self.b < 65)

    # Returns the type of tyle detected from the colour data
    def getTileType(self):
        self.__update()
        tileType = "undefined"
        if self.__isNormal():
            tileType = "normal"
        elif self.__isTrap():
            tileType = "hole"
        elif self.__isSwamp():
            tileType = "swamp"
        elif self.__isCheckpoint():
            tileType = "checkpoint"
        elif self.__isBlue():
            tileType = "connection1-2"
        elif self.__isPurple():
            tileType = "connection2-3"
        elif self.__isRed():
            tileType = "connection1-3"

        #print("Color: " + tileType)
        #print("r: " + str(self.r) + "g: " + str(self.g) + "b: " +  str(self.b))
        return tileType


class Comunicator:
    def __init__(self, emmiter, receiver, timeStep):
        self.receiver = receiver
        self.emmiter = emmiter
        self.receiver.enable(timeStep)
        self.lackOfProgress = False
        self.doGetWordInfo = True
        self.gameScore = 0
        self.remainingTime = 0

    def sendVictim(self, position, victimtype):
        self.doGetWordInfo = False
        letter = bytes(victimtype, "utf-8")
        position = multiplyLists(position, [100, 100])
        position = [int(position[0]), int(position[1])]
        message = struct.pack("i i c", position[0], position[1], letter)
        self.emmiter.send(message)


    def sendLackOfProgress(self):
        self.doGetWordInfo = False
        message = struct.pack('c', 'L'.encode()) # message = 'L' to activate lack of progress
        self.emmiter.send(message)


    def sendEndOfPlay(self):
        self.doGetWordInfo = False
        exit_mes = bytes('E', "utf-8")
        self.emmiter.send(exit_mes)


        print("Ended!!!!!")

    def sendMap(self, npArray):
         ## Get shape
        print(npArray)
        s = npArray.shape
        ## Get shape as bytes
        s_bytes = struct.pack('2i',*s)
        ## Flattening the matrix and join with ','
        flatMap = ','.join(npArray.flatten())
        ## Encode
        sub_bytes = flatMap.encode('utf-8')
        ## Add togeather, shape + map
        a_bytes = s_bytes + sub_bytes
        ## Send map data
        self.emmiter.send(a_bytes)
        #STEP3 Send map evaluate request
        map_evaluate_request = struct.pack('c', b'M')
        self.emmiter.send(map_evaluate_request)
        self.doGetWordInfo = False

    def requestGameData(self):
        if self.doGetWordInfo:
            message = struct.pack('c', 'G'.encode()) # message = 'G' for game information
            self.emmiter.send(message) # send message

    def update(self):

        if self.doGetWordInfo:
            """
            self.requestGameData()
            if self.receiver.getQueueLength() > 0: # If receiver queue is not empty
                receivedData = self.receiver.getData()
                if len(receivedData) > 2:
                    tup = struct.unpack('c f i', receivedData) # Parse data into char, float, int
                    if tup[0].decode("utf-8") == 'G':
                        self.gameScore = tup[1]
                        self.remainingTime = tup[2]
                        self.receiver.nextPacket() # Discard the current data packet
            """

            #print("Remaining time:", self.remainingTime)
            self.lackOfProgress = False
            if self.receiver.getQueueLength() > 0: # If receiver queue is not empty
                receivedData = self.receiver.getData()
                print(receivedData)
                if len(receivedData) < 2:
                    tup = struct.unpack('c', receivedData) # Parse data into character
                    if tup[0].decode("utf-8") == 'L': # 'L' means lack of progress occurred
                        print("Detected Lack of Progress!")
                        self.lackOfProgress = True
                    self.receiver.nextPacket() # Discard the current data packetelse:
        else:
            self.doGetWordInfo = True

class DistanceSensor:
    def __init__(self, threshold, distanceFromCenter, angle, sensor, timeStep):
        self.sensor = sensor
        self.angle = angle
        self.distance = distanceFromCenter
        self.timeStep = timeStep
        self.threshold = threshold
        self.position = [0, 0]
        self.sensor.enable(self.timeStep)

    def isFar(self):
        distance = self.sensor.getValue()
        #print("Sensor distance:", distance)
        return distance > self.threshold

    def setPosition(self, robotPosition, robotRotation):
        sensorRotation = robotRotation + self.angle
        sensorPosition = getCoordsFromDegs(sensorRotation, self.distance)
        self.position = sumLists(sensorPosition, robotPosition)

# Abstraction layer for robot
class RobotLayer:
    def __init__(self, timeStep):
        self.maxWheelSpeed = 6.28
        self.timeStep = timeStep
        self.robot = Robot()
        self.prevRotation = 0
        self.rotation = 0
        self.globalPosition = [0, 0]
        self.prevGlobalPosition = [0, 0]
        self.positionOffsets = [0, 0]
        self.__useGyroForRotation = True
        self.time = 0
        self.rotateToDegsFirstTime = True
        self.delayFirstTime = True
        self.gyroscope = Gyroscope(self.robot.getDevice("gyro"), 1, self.timeStep)
        self.gps = Gps(self.robot.getDevice("gps"), self.timeStep)
        self.lidar = Lidar(self.robot.getDevice("lidar"), self.timeStep)
        self.leftWheel = Wheel(self.robot.getDevice("wheel1 motor"), self.maxWheelSpeed)
        self.rightWheel = Wheel(self.robot.getDevice("wheel2 motor"), self.maxWheelSpeed)
        self.colorSensor = ColourSensor(self.robot.getDevice("colour_sensor"), 0.037, 32)
        self.leftGroundSensor = DistanceSensor(0.04, 0.0523, 45, self.robot.getDevice("distance sensor2"), self.timeStep)
        self.rightGroundSensor = DistanceSensor(0.04, 0.0523, -45, self.robot.getDevice("distance sensor1"), self.timeStep)
        self.comunicator = Comunicator(self.robot.getDevice("emitter"), self.robot.getDevice("receiver"), self.timeStep)
        self.rightCamera = Camera(self.robot.getDevice("camera2"), self.timeStep)
        self.leftCamera = Camera(self.robot.getDevice("camera1"), self.timeStep)
        self.victimClasifier = VictimClassifier()

    def getVictims(self):
        poses = []
        imgs = []
        for camera in (self.rightCamera, self.leftCamera):
            img = camera.getImg()
            crop_center(img, 12)
            img = cv.resize(img, (128, 128), interpolation = cv.INTER_NEAREST)
            cposes, cimgs = self.victimClasifier.getVictimImagesAndPositions(img)
            poses += cposes
            imgs += cimgs
        print("Victim Poses: ",poses)
        for img in imgs:
            print("Victim shape:", img.shape)
        closeVictims = self.victimClasifier.getCloseVictims(poses, imgs)
        finalVictims = []
        for closeVictim in closeVictims:
            finalVictims.append(self.victimClasifier.classifyVictim(closeVictim))
        return finalVictims

    def reportVictims(self, letter):
        self.comunicator.sendVictim(self.globalPosition, letter)

    def sendArray(self, array):
        self.comunicator.sendMap(array)

    def sendEnd(self):
        print("End sended")
        self.comunicator.sendEndOfPlay()


    # Decides if the rotation detection is carried out by the gps or gyro
    @property
    def rotationDetectionType(self):
        if self.__useGyroForRotation:
            return "gyroscope"
        else:
            return "gps"

    @rotationDetectionType.setter
    def rotationDetectionType(self, rotationType):
        if rotationType == "gyroscope":
            self.__useGyroForRotation = True

        elif rotationType == "gps":
            self.__useGyroForRotation = False
        else:
            raise ValueError("Invalid rotation detection type inputted")

    def delaySec(self, delay):
        if self.delayFirstTime:
            self.delayStart = self.robot.getTime()
            self.delayFirstTime = False
        else:
            if self.time - self.delayStart >= delay:
                self.delayFirstTime = True
                return True
        return False

    # Moves the wheels at the specified ratio
    def moveWheels(self, leftRatio, rightRatio):
        self.leftWheel.move(leftRatio)
        self.rightWheel.move(rightRatio)

    def rotateToDegs(self, degs, orientation="closest", maxSpeed=0.5):
        accuracy = 2
        if self.rotateToDegsFirstTime:
            #print("STARTED ROTATION")
            self.rotateToDegsFirstTime = False
        self.seqRotateToDegsInitialRot = self.rotation
        self.seqRotateToDegsinitialDiff = round(self.seqRotateToDegsInitialRot - degs)
        diff = self.rotation - degs
        moveDiff = max(round(self.rotation), degs) - min(self.rotation, degs)
        if diff > 180 or diff < -180:
            moveDiff = 360 - moveDiff
        speedFract = min(mapVals(moveDiff, accuracy, 90, 0.2, 0.8), maxSpeed)
        if accuracy  * -1 < diff < accuracy or 360 - accuracy < diff < 360 + accuracy:
            self.rotateToDegsFirstTime = True
            return True
        else:
            if orientation == "closest":
                if 180 > self.seqRotateToDegsinitialDiff > 0 or self.seqRotateToDegsinitialDiff < -180:
                    direction = "right"
                else:
                    direction = "left"
            elif orientation == "farthest":
                if 180 > self.seqRotateToDegsinitialDiff > 0 or self.seqRotateToDegsinitialDiff < -180:
                    direction = "left"
                else:
                    direction = "right"
            else:
                direction = orientation

            if moveDiff > 10:
                if direction == "right":
                    self.moveWheels(speedFract * -1, speedFract)
                elif direction == "left":
                    self.moveWheels(speedFract, speedFract * -1)
            else:
                if direction == "right":
                    self.moveWheels(speedFract * -0.5, speedFract)
                elif direction == "left":
                    self.moveWheels(speedFract, speedFract * -0.5)
            #print("speed fract: " +  str(speedFract))
            #print("target angle: " +  str(degs))
            #print("moveDiff: " + str(moveDiff))
            #print("diff: " + str(diff))
            #print("orientation: " + str(orientation))
            #print("direction: " + str(direction))
            #print("initialDiff: " + str(self.seqRotateToDegsinitialDiff))

        #print("ROT IS FALSE")
        return False

    def rotateSmoothlyToDegs(self, degs, orientation="closest", maxSpeed=0.5):
        accuracy = 2
        seqRotateToDegsinitialDiff = round(self.rotation  - degs)
        diff = self.rotation - degs
        moveDiff = max(round(self.rotation), degs) - min(self.rotation, degs)
        if diff > 180 or diff < -180:
            moveDiff = 360 - moveDiff
        speedFract = min(mapVals(moveDiff, accuracy, 90, 0.2, 0.8), maxSpeed)
        if accuracy  * -1 < diff < accuracy or 360 - accuracy < diff < 360 + accuracy:
            self.rotateToDegsFirstTime = True
            return True
        else:
            if orientation == "closest":
                if 180 > seqRotateToDegsinitialDiff > 0 or seqRotateToDegsinitialDiff < -180:
                    direction = "right"
                else:
                    direction = "left"
            elif orientation == "farthest":
                if 180 > seqRotateToDegsinitialDiff > 0 or seqRotateToDegsinitialDiff < -180:
                    direction = "left"
                else:
                    direction = "right"
            else:
                direction = orientation
            if direction == "right":
                self.moveWheels(speedFract * -0.5, speedFract)
            elif direction == "left":
                self.moveWheels(speedFract, speedFract * -0.5)
            #print("speed fract: " +  str(speedFract))
            #print("target angle: " +  str(degs))
            #print("moveDiff: " + str(moveDiff))
            #print("diff: " + str(diff))
            #print("orientation: " + str(orientation))
            #print("direction: " + str(direction))
            #print("initialDiff: " + str(seqRotateToDegsinitialDiff))

        #print("ROT IS FALSE")
        return False

    def moveToCoords(self, targetPos):
        errorMargin = 0.01
        descelerationStart = 0.5 * 0.12
        diffX = targetPos[0] - self.globalPosition[0]
        diffY = targetPos[1] - self.globalPosition[1]
        #print("Target Pos: ", targetPos)
        #print("Used global Pos: ", self.globalPosition)
        #print("diff in pos: " + str(diffX) + " , " + str(diffY))
        dist = getDistance((diffX, diffY))
        #print("Dist: "+ str(dist))
        if errorMargin * -1 < dist < errorMargin:
            #self.robot.move(0,0)
            #print("FinisehedMove")
            return True
        else:

            ang = getDegsFromCoords((diffX, diffY))
            ang = normalizeDegs(ang)
            #print("traget ang: " + str(ang))
            ratio = min(mapVals(dist, 0, descelerationStart, 0.1, 1), 1)
            ratio = max(ratio, 0.8)
            if self.rotateToDegs(ang):
                self.moveWheels(ratio, ratio)
                #print("Moving")
        return False

    # Gets a point cloud with all the detections from lidar and distance sensorss
    def getDetectionPointCloud(self):

        rawPointCloud = self.lidar.getPointCloud(layers=(2,3))
        processedPointCloud = []
        for point in rawPointCloud:
            procPoint = [point[0] + self.globalPosition[0], point[1] + self.globalPosition[1]]
            #procPoint = [procPoint[0] + procPoint[0] * 0.1, procPoint[1] + procPoint[1] * 0.1]
            processedPointCloud.append(procPoint)
        return processedPointCloud

    def getColorDetection(self):
        pos = self.colorSensor.getPosition(self.globalPosition, self.rotation)
        detection = self.colorSensor.getTileType()
        return pos, detection

    def trapsAtSides(self):
        sides = []
        if self.leftGroundSensor.isFar():
            sides.append(self.leftGroundSensor.position)
        if self.rightGroundSensor.isFar():
            sides.append(self.rightGroundSensor.position)
        return sides

    # Returns True if the simulation is running
    def doLoop(self):
        return self.robot.step(self.timeStep) != -1

    def getWheelDirection(self):
        if self.rightWheel.velocity + self.leftWheel.velocity == 0:
            return 0
        return (self.rightWheel.velocity + self.leftWheel.velocity) / 2

    # Must run every TimeStep
    def update(self):
        # Updates the current time
        self.time = self.robot.getTime()
        # Updates the gps, gyroscope
        self.gps.update()
        self.gyroscope.update(self.time)

        # Gets global position
        self.prevGlobalPosition = self.globalPosition
        self.globalPosition = self.gps.getPosition()
        self.globalPosition[0] += self.positionOffsets[0]
        self.globalPosition[1] += self.positionOffsets[1]

        if self.gyroscope.getDiff() < 0.00001 and self.getWheelDirection() >= 0:
            self.rotationDetectionType = "gps"

        else:
            self.rotationDetectionType = "gyroscope"

        self.prevRotation = self.rotation

        # Gets global rotation
        if self.__useGyroForRotation:
            self.rotation = self.gyroscope.getDegrees()
            print("USING GYRO")
        else:
            print("USING GPS")
            val = self.gps.getRotation()
            if val is not None:
                self.rotation = val
            self.gyroscope.setDegrees(self.rotation)

        # Sets lidar rotation
        self.lidar.setRotationDegrees(self.rotation + 0)

        self.rightGroundSensor.setPosition(self.globalPosition, self.rotation)
        self.leftGroundSensor.setPosition(self.globalPosition, self.rotation)



        self.comunicator.update()

        #victims = self.camera.getVictims()
        #print("Victims: ", victims)


# File: "AbstractionLayer.py"










class PlottingArray:
    def __init__(self, size, offsets, scale, tileSize):
        self.scale = scale
        self.size = size
        self.offsets = offsets
        self.scale = scale
        self.tileSize = tileSize
        self.gridPlottingArray = np.zeros(self.size, np.uint8)

        for y in range(0, len(self.gridPlottingArray), int(self.tileSize * scale)):
            for x in range(len(self.gridPlottingArray[0])):
                self.gridPlottingArray[x][y] = 50
        for x in range(0, len(self.gridPlottingArray), int(self.tileSize * scale)):
            for y in range(len(self.gridPlottingArray[0])):
                self.gridPlottingArray[x][y] = 50

    def plotPoint(self, point, value):
        procPoint = [int(point[0] * self.scale), int(point[1] * self.scale * -1)]
        finalx = procPoint[0] + int(self.offsets[0] * self.tileSize)
        finaly = procPoint[1] + int(self.offsets[1] * self.tileSize)

        if self.size[0] * -1 < finalx < self.size[0] and self.size[0] * -1 < finaly < self.size[1]:
            self.gridPlottingArray[finalx][finaly] = value

    def getPoint(self, point):
        procPoint = [int(point[0] * self.scale), int(point[1] * self.scale * -1)]
        finalx = procPoint[0] + int(self.offsets[0] * self.tileSize)
        finaly = procPoint[1] + int(self.offsets[1] * self.tileSize)

        if self.size[0] * -1 < finalx < self.size[0] and self.size[0] * -1 < finaly < self.size[1]:
            return self.gridPlottingArray[finalx][finaly]

    def reset(self):
        self.gridPlottingArray = np.zeros(self.size, np.uint8)

        for y in range(0, len(self.gridPlottingArray), round(self.tileSize * self.scale)):
            for x in range(len(self.gridPlottingArray[0])):
                self.gridPlottingArray[x][y] = 50
        for x in range(0, len(self.gridPlottingArray), round(self.tileSize * self.scale)):
            for y in range(len(self.gridPlottingArray[0])):
                self.gridPlottingArray[x][y] = 50


class AbstractionLayer():

    def __init__(self):
        # Variables
        self.tileSize = 0.06
        self.timeStep = 32
        self.gridPlotter = PlottingArray((300, 300), [1500, 1500], 150, self.tileSize)
        self.doWallMapping = False
        self.actualTileType = "undefined"
        self.isTrap = False
        self.timeInRound = 8 * 60
        self.timeWithoutMoving = 0
        self.__timeWithoutMovingStart = 0

        # Components
        self.robot = RobotLayer(self.timeStep)
        self.seqMg = SequenceManager()
        self.analyst = Analyst(self.tileSize)

        # -- Functions --
        self.seqPrint = self.seqMg.makeSimpleSeqEvent(print)
        self.seqDelaySec = self.seqMg.makeComplexSeqEvent(self.robot.delaySec)
        self.seqMoveWheels = self.seqMg.makeSimpleSeqEvent(self.robot.moveWheels)
        self.seqRotateToDegs = self.seqMg.makeComplexSeqEvent(self.robot.rotateToDegs)
        self.seqMoveToCoords = self.seqMg.makeComplexSeqEvent(self.robot.moveToCoords)
        self.seqResetSequenceFlags = self.seqMg.makeSimpleSeqEvent(self.resetSequenceFlags)
        self.seqResetSequence = self.seqMg.makeSimpleSeqEvent(self.resetSequence)

    def resetSequence(self):
        self.seqMg.resetSequence()
        self.resetSequenceFlags()
        self.seqMg.linePointer = 0

    def resetSequenceFlags(self):
        self.robot.delayFirstTime = True

    def calibrate(self):
        self.seqMg.startSequence()
        self.seqDelaySec(0.5)
        if self.seqMg.simpleSeqEvent():
            actualTile = [self.position[0] // self.tileSize, self.position[1] // self.tileSize]
            self.robot.positionOffsets = [
                round((actualTile[0] * self.tileSize) - self.position[0]) + self.tileSize // 2,
                round((actualTile[1] * self.tileSize) - self.position[1]) + self.tileSize // 2]
            self.robot.positionOffsets = [self.robot.positionOffsets[0] % self.tileSize,
                                          self.robot.positionOffsets[1] % self.tileSize]

            print("positionOffsets: ", self.robot.positionOffsets)
        if self.seqMg.simpleSeqEvent(): self.analyst.registerStart()
        self.seqDelaySec(0.5)

        if self.seqMg.simpleSeqEvent(): self.robot.rotationDetectionType = "gps"
        self.seqMoveWheels(1, 1)
        self.seqDelaySec(0.2)
        if self.seqMg.simpleSeqEvent(): self.robot.rotationDetectionType = "gyroscope"
        self.seqDelaySec(0.2)
        self.seqMoveWheels(0, 0)
        self.seqMoveWheels(-1, -1)
        self.seqDelaySec(0.4)
        self.seqMoveWheels(0, 0)
        if self.seqMg.simpleSeqEvent(): self.doWallMapping = True
        return self.seqMg.seqResetSequence()

    @property
    def rotation(self):
        return self.robot.rotation

    @property
    def position(self):
        return self.robot.globalPosition

    @property
    def prevPosition(self):
        return self.robot.prevGlobalPosition

    def getBestPos(self):
        return self.analyst.getBestPosToMove()

    def doLoop(self):
        return self.robot.doLoop()

    def recalculatePath(self):
        self.analyst.calculatePath = True

    def isVictims(self):
        victims = self.robot.getVictims()
        if len(victims) and not self.analyst.isRegisteredVictim():
            return True
        return False

    def reportVictims(self):
        victims = self.robot.getVictims()
        if len(victims):
            self.robot.reportVictims(victims[0])
        self.analyst.registerVictim()

    def endGame(self):
        self.sendFinalArray()
        self.robot.sendEnd()

    def sendFinalArray(self):
        self.robot.sendArray(self.analyst.getArrayRepresentation())

    def isEnded(self):
        return self.analyst.ended

    @property
    def timeLeft(self):
        return self.timeInRound - self.robot.time

    def update(self):
        self.robot.update()

        print("Time:", self.robot.time)
        print("time without moving: ", self.timeWithoutMoving)
        print("time left:", self.timeLeft)
        diff = [self.position[0] - self.prevPosition[0], self.position[1] - self.prevPosition[1]]
        if self.robot.getWheelDirection() < 0.1:
            self.timeWithoutMoving = 0
        elif -0.0001 < getDistance(diff) < 0.0001:
            if self.timeWithoutMoving == 0:
                self.__timeWithoutMovingStart = self.robot.time
                self.timeWithoutMoving = 0.000000001
            else:
                self.timeWithoutMoving = self.robot.time - self.__timeWithoutMovingStart
        else:
            self.timeWithoutMoving = 0

        if self.doWallMapping:
            print("Doing wall mapping")

            if self.timeWithoutMoving > 1:
                self.analyst.stoppedMoving = True
            else:
                self.analyst.stoppedMoving = False

            pointCloud = self.robot.getDetectionPointCloud()

            """
            for point in pointCloud:

                if self.gridPlotter.getPoint(point) < 250:
                    self.gridPlotter.plotPoint(point, self.gridPlotter.getPoint(point) + 5)
            """
            # tileType = self.robot.get
            self.analyst.loadPointCloud(pointCloud)

        colorPos, self.actualTileType = self.robot.getColorDetection()
        print("Tile type: ", self.actualTileType)
        self.analyst.loadColorDetection(colorPos, self.actualTileType)
        trapsAtSides = self.robot.trapsAtSides()
        for trap in trapsAtSides:
            self.analyst.loadColorDetection(trap, "hole")
        self.isTrap = len(trapsAtSides) or self.actualTileType == "hole"
        self.analyst.update(self.position, self.rotation)

        self.gridPlotter.reset()
        for point in self.analyst.converter.totalPointCloud:
            if point[2] > 20:
                ppoint = [point[0] / 100, point[1] / 100]
                self.gridPlotter.plotPoint(ppoint, 100)

        bestPos = self.analyst.getStartRawNodePos()
        if bestPos is not None:
            self.gridPlotter.plotPoint(bestPos, 255)

        bestPos = self.analyst.getBestPosToMove()
        if bestPos is not None:
            self.gridPlotter.plotPoint(bestPos, 200)

            # self.gridPlotter.plotPoint(self.position, 150)

        bestPoses = self.analyst.getBestPoses()
        for bestPos in bestPoses:
            self.gridPlotter.plotPoint(bestPos, 255)

        self.analyst.showGrid()

        # cv.imshow("raw detections", cv.resize(self.gridPlotter.gridPlottingArray, (600, 600), interpolation=cv.INTER_NEAREST))
        # cv.waitKey(1)


# File: "FinalCode.py"









timeStep = 16 * 2
stMg = StateManager("init")
r = AbstractionLayer()

isOptimised = cv.useOptimized()

# While the simulation is running
while r.doLoop():
    e1 = cv.getTickCount()
    # Update the robot
    r.update()
    print("rotation: " + str(r.rotation))
    print("position: " + str(r.position))
    print("State:", stMg.state)


    if not stMg.checkState("init"):
        if r.isEnded():
            r.seqResetSequence()
            stMg.changeState("end")

        elif r.isVictims():
            r.seqResetSequence()
            stMg.changeState("victim")



    if stMg.checkState("init"):
        if r.calibrate():
            stMg.changeState("followBest")

    if stMg.checkState("stop"):
        r.seqMg.startSequence()
        r.seqMoveWheels(0, 0)

    if stMg.checkState("moveForward"):
        r.seqMg.startSequence()
        r.seqMoveWheels(0.5, -0.5)
        r.seqDelaySec(0.1)
        r.seqMoveWheels(-0.5, 0.5)
        r.seqDelaySec(0.1)
        r.seqResetSequence()


    if stMg.checkState("followBest"):
        r.seqMg.startSequence()
        bestPos = r.getBestPos()
        if bestPos is not None:
            r.seqMoveToCoords(bestPos)
        r.seqResetSequence()

        if r.isTrap:
            r.seqResetSequence()
            stMg.changeState("hole")


    if stMg.checkState("hole"):
        r.seqMg.startSequence()
        r.seqMoveWheels(-0.5, -0.5)
        r.seqDelaySec(0.5)
        r.seqMoveWheels(0, 0)
        if r.seqMg.simpleSeqEvent(): r.recalculatePath()
        r.seqResetSequence()
        stMg.changeState("followBest")

    if stMg.checkState("victim"):
        print("Victim mode!!")
        r.seqMg.startSequence()
        r.seqMoveWheels(0, 0)
        r.seqPrint("stopping")
        r.seqDelaySec(3.2)
        r.seqPrint("reporting")
        if r.seqMg.simpleSeqEvent(): r.reportVictims()
        r.seqPrint("Victim reported")
        r.seqResetSequence()
        stMg.changeState("followBest")

    if stMg.checkState("end"):
        r.seqMg.startSequence()
        if r.seqMg.simpleSeqEvent(): r.endGame()
        r.seqMoveWheels(0, 0)

    print("--------------------------------------------------------------------")

    e2 = cv.getTickCount()

    time = (e2 - e1)/ cv.getTickFrequency()
    print(f"Tick time is {time}")
    print(f"Is it optimised? {isOptimised}")

    print("--------------------------------------------------------------------")