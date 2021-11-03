import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.image as mtpltimg
import os
import math
import json
import numpy
from tkinter import filedialog as fd

def hexToRGB(hexCode):
    return tuple(int(hexCode.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

class DataManager():
    def __init__(self):
        self.fileName = ""
        while self.fileName == "":
            filetypes = [('json files', '*.json')]
            self.fileName = fd.askopenfilename(title="Open TDS data file", filetypes=filetypes)
        self.imageDictionary = {}
        self.currentImgId = self.fromJSON(self.fileName)['images'][0]['id']

        self.imageMaskArray = self.manageData()

    def fromJSON(self, fileName):
        with open(fileName, "r") as jsonObj:
            returnDict = json.load(jsonObj)
            return returnDict

    def getImgList(self):
        masterDict = self.fromJSON(self.fileName)

        imagesDict = masterDict['images']
        anoDict = masterDict['annotation']

        for i in imagesDict:
            for k, v in enumerate(anoDict):
                if v['image_id'] == i['id']:
                    if i['id'] not in self.imageDictionary:
                        self.imageDictionary[i['id']] = k

        print(self.imageDictionary)
        print(self.currentImgId)

    def loadImage(self):
        imgName = os.path.relpath('./cropImages/img-' + self.currentImgId + '.jpg')
        imagePlot = mtpltimg.imread(imgName)
        return imagePlot
                    
    def manageData(self):
        segmentColors = ['#71b8eb', '#b1ddfc', '#707070', '#8d56ba', "#fff5a8", "#d97796"]
        imageIDs = []

        masterDict = self.fromJSON(self.fileName)

        subDict = [] #masterDict["annotation"]

        for i in masterDict['annotation']:
            if i['image_id'] == self.currentImgId:
                subDict.append(i)

        self.getImgList()

        arraySize = subDict[self.imageDictionary[self.currentImgId]]["segmentation"]["size"]
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
                        
                        
        for y in range(booleanSize[0]):
            for x in range(booleanSize[1]):
                colorList = hexToRGB(segmentColors[int(categoryArray[x, y])])
                for c, color in enumerate(colorList):
                    array[y, (x + y) % 256, c] = color

        array = array.astype(dtype=numpy.uint8)
        return array

class ImageDisplay(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)
        self.parent = parent

        self.graph = Figure(figsize=(5,4))
        canvas = FigureCanvasTkAgg(self.graph, self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0)   

        self.updateImages()

    def updateImages(self):
        leftDisplay = self.graph.add_subplot(1,2,1)
        leftDisplay.imshow(self.parent.data.imageMaskArray)
        leftDisplay.tick_params(axis='both',  # changes apply to the x-axis
                       which='both',          # both major and minor ticks are affected
                       bottom=False,          # ticks along the bottom edge are off
                       top=False,             # ticks along the top edge are off
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)

        rightDisplay = self.graph.add_subplot(1,2,2)
        rightDisplay.imshow(self.parent.data.loadImage())
        rightDisplay.tick_params(axis='both', # changes apply to the x-axis
                       which='both',          # both major and minor ticks are affected
                       bottom=False,          # ticks along the bottom edge are off
                       top=False,             # ticks along the top edge are off
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)



class Buttons(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)
        self.parent = parent
        prevButton = tkinter.Button(self, text="<")
        prevButton.grid(row=1,column=0, sticky='NSW', padx=210)

        nextButton = tkinter.Button(self, text=">", command=lambda: self.cycleNext())
        nextButton.grid(row=1,column=0, sticky='NSE', padx= 210)

    def cycleNext(self):
        imgIDS = []
        for k in self.parent.data.imageDictionary:
            imgIDS.append(k)
        print(imgIDS)

        for i, v in enumerate(imgIDS):
            if v == self.parent.data.currentImgId:
                index = i+1

        self.parent.currentImgId = imgIDS[index]
        self.parent.ImageDisplay.updateImages()
        self.parent.data.imageMaskArray = self.parent.data.manageData()
        print(self.parent.currentImgId)
            


class WindowClass(tkinter.Frame):
    def __init__(self, parent):            
        tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title('Embedding Matplotlib in Tk')

        self.data = DataManager()

        self.ImageDisplay = ImageDisplay(self)
        self.ImageDisplay.grid(row = 0, column=0)

        self.Buttons = Buttons(self)
        self.Buttons.grid(row = 1, column=0)

def main():
    root = tkinter.Tk()

    root.geometry('800x600')

    window = WindowClass(root)
    window.pack(fill='both', expand=True)

    root.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.
main()