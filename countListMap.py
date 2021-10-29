#########################
# countListMap.py       #
# Author: Dylan Berndt  #
# 27/10/2021            #
#########################

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg#, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import numpy
import json
import tkinter as tk
import os
import math

listIndex = 0

def hexToRGB(hexCode):
    return tuple(int(hexCode.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

def fromJSON(fileName):
    with open(fileName, "r") as jsonObj:
        returnDict = json.load(jsonObj)
        return returnDict

def manageData():
    global listIndex
    segmentColors = ['#71b8eb', '#b1ddfc', '#707070', '#8d56ba', "#fff5a8", "#d97796"]
    imageIDs = []

    fileName = os.path.relpath("./TDSCOCO/COCOTDS.json")

    masterDict = fromJSON(fileName)

    subDict = masterDict["annotation"]

    for i, k in enumerate(subDict):
        if not any(d == k["image_id"] for d in imageIDs):
            imageIDs.append(k['image_id'])
            listIndex = i

    arraySize = subDict[listIndex]["segmentation"]["size"]
    arraySize.append(3)

    array = numpy.zeros(arraySize)
    categoryArray = numpy.zeros(arraySize[0:2])

    for i, count in enumerate(subDict):
        booleanSize = count["segmentation"]["size"][0:2]
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
            colorList = hexToRGB(segmentColors[int(categoryArray[x, y])])
            for c, color in enumerate(colorList):
                array[y, x, c] = color

    array = array.astype(dtype=numpy.uint8)
    return array

plt.imshow(manageData())
plt.show()