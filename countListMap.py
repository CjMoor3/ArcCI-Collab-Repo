#########################
# countListMap.py       #
# Author: Dylan Berndt  #
# 27/10/2021            #
#########################

import matplotlib.pyplot as plt
import numpy
import json
import tkinter as tk
import os
import math

classColors = ['#71b8eb', '#b1ddfc', '#707070', '#8d56ba', "#fff5a8", "#d97796"]

def hexToRGB(hexCode):
    return tuple(int(hexCode.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

def fromJSON(fileName):
    with open(fileName, "r") as jsonObj:
        returnDict = json.load(jsonObj)
        return returnDict


def manageData():
    global classColors

    fileName = os.path.relpath("./TDSCOCO/COCOTDS.json")

    masterDict = fromJSON(fileName)

    subDict = masterDict["annotation"]

    #arraySize = subDict[0]["segmentation"]["size"]
    arraySize = [200, 200]
    arraySize.append(3)

    array = numpy.zeros(arraySize)
    categoryArray = numpy.zeros(arraySize[0:2])

    for i, count in enumerate(subDict):
        #booleanSize = count["segmentation"]["size"][0:2]
        booleanSize = [200, 200]
        booleanMask = numpy.zeros(booleanSize)

        countList = count["segmentation"]["counts"]
        boolean = False
        arrayIndex = 0
        for indivCount in countList:
            for b in range(indivCount):
                xIndex = arrayIndex % booleanSize[0]
                yIndex = math.floor(arrayIndex / booleanSize[0])
                booleanMask[xIndex, yIndex] = boolean

                arrayIndex += 1

            boolean = not boolean

        for y in range(booleanSize[1]):
            for x in range(booleanSize[0]):
                if booleanMask[x, y]:
                    categoryArray[x, y] = count["category_id"]

    for x in range(booleanSize[1]):
        for y in range(booleanSize[0]):
            colorList = hexToRGB(classColors[int(categoryArray[x, y])])
            for c, color in enumerate(colorList):
                array[y, x, c] = color

    array = array.astype(dtype=numpy.uint8)
    return array

plt.imsave("yep.png", manageData())