import tkinter
from tkinter import filedialog as fd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.image as mtpltimg
import os
import math
import json
import numpy

class colors:
    def __init__(self):
        self.darkMode = ['#36393F', '#2F3136', 'white', '#292B2F']

class DataManager():
    def __init__(self, parent):
        filetypes = [('json files', '*.json')]
        self.fileName = fd.askopenfilename(title="Open TDS data file", filetypes=filetypes)
        self.parent = parent
        self.imgDir = None
        self.imageDictionary = {}
        self.c = colors()

        self.imagePlot = None

        if self.fileName == ():
            quit()
        else:
            self.currentImgId = self.fromJSON(self.fileName)['images'][0]['id']

        self.imageMaskArray = self.loadRLE()
    
    def hexToRGB(self, hexCode):
        return tuple(int(hexCode.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

    def fromJSON(self, fileName):
        with open(fileName, "r") as jsonObj:
            returnDict = json.load(jsonObj)
            return returnDict

    def deleteImgData(self):
        masterDict = self.fromJSON(self.fileName)

        # Loop checking for images with the right ID to be deleted and deleting them
        for i in masterDict['images']:
            if i['id'] == self.currentImgId:
                masterDict['images'].remove(i)

        # Loop to remove all segment data with matching imgID
        for i in reversed(masterDict['annotation']):
            if i['image_id'] == self.currentImgId:
                masterDict['annotation'].remove(i)

        # Save changes to the dataset
        with open(self.fileName, 'w') as outFile:
            json.dump(masterDict, outFile, indent=4)
            outFile.close()

        self.imageDictionary.clear()
        self.getImgList()

    def getImgList(self):
        masterDict = self.fromJSON(self.fileName)

        imagesDict = masterDict['images']
        anoDict = masterDict['annotation']

        for i in imagesDict:
            for k, v in enumerate(anoDict):
                if v['image_id'] == i['id']:
                    if i['id'] not in self.imageDictionary:
                        self.imageDictionary[i['id']] = k

    def loadImage(self):
        if self.imgDir == None:
            imagePlot = numpy.dstack(self.hexToRGB(self.c.darkMode[3]))
            self.imagePlot = imagePlot
        else:
            imgName = os.path.join(self.imgDir,os.path.relpath('./img-' + self.currentImgId + '.jpg'))
            imagePlot = mtpltimg.imread(imgName)
            self.imagePlot = imagePlot
                    
    def loadRLE(self):
        segmentColors = ['#71b8eb', '#b1ddfc', '#707070', '#8d56ba', "#fff5a8", "#d97796"]

        masterDict = self.fromJSON(self.fileName)

        subDict = [] # masterDict["annotation"]
        subDict.clear()

        for i in masterDict['annotation']:
            if i['image_id'] == self.currentImgId:
                subDict.append(i)

        self.getImgList()

        arraySize = subDict[0]["segmentation"]["size"]
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
                colorList = self.hexToRGB(segmentColors[int(categoryArray[x, y])])
                for c, color in enumerate(colorList):
                    array[y, (x + y) % 256, c] = color

        array = array.astype(dtype=numpy.uint8)
        return array

class ImageDisplay(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)
        self.parent = parent
        c = colors()

        self.graph = Figure(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.graph, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(sticky='NSEW')   

        self.graph.subplots_adjust(left = 0.01, right = 0.99,
                            bottom = 0.05, top = 0.99,
                            wspace = 0.01, hspace = 0.01)

        self.graph.set_facecolor(c.darkMode[3])

        self.updateImages()

    def updateImages(self):
        self.parent.data.loadImage()
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
        rightDisplay.imshow(self.parent.data.imagePlot)
        rightDisplay.tick_params(axis='both', # changes apply to the x-axis
                       which='both',          # both major and minor ticks are affected
                       bottom=False,          # ticks along the bottom edge are off
                       top=False,             # ticks along the top edge are off
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)

        self.canvas.draw()

class Buttons(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)
        self.parent = parent
        c = colors()
        self.config(bg=c.darkMode[3])

        prevButton = tkinter.Button(self, text="<", height=2, width=4, highlightthickness=0, fg=c.darkMode[2], bg=c.darkMode[1], command=lambda: self.cyclePrev())
        prevButton.grid(row=0, sticky='nsw', pady=(0,10), padx=(15, 0))

        nextButton = tkinter.Button(self, text=">", height=2, width=4, highlightthickness=0, fg=c.darkMode[2], bg=c.darkMode[1], command=lambda: self.cycleNext())
        nextButton.grid(row=0, sticky='nse', padx= (65, 20), pady=(0, 10))

        self.idLabel = tkinter.Label(self, text="Current Image ID: "+ self.parent.data.currentImgId, fg=c.darkMode[2], bg=c.darkMode[1])
        self.idLabel.grid(row=0, column=1, columnspan=2, pady=(0,10), padx=(0,300))

        delButton = tkinter.Button(self, text="DEL", highlightthickness=0, fg=c.darkMode[2], bg=c.darkMode[1], command=self.delButtonFunc)
        delButton.grid(row=0, column=1, sticky='nse', pady=(0,10), padx=(0,250))

        imgDirButton = tkinter.Button(self, text="Open Image Directory", highlightthickness=0, fg=c.darkMode[2], bg=c.darkMode[1], command=lambda: self.openImgDir())
        imgDirButton.grid(row=0, column=1, sticky='nse', pady=(0, 10), padx=(0, 100))

        openButton = tkinter.Button(self, text="Open Dataset", highlightthickness=0, fg=c.darkMode[2], bg=c.darkMode[1],command=lambda: self.openDataset())
        openButton.grid(row=0, column=1, sticky='nse', pady=(0,10), padx=(555,0))

        self.imgIDS = []
 
    def cyclePrev(self):
        self.imgIDS.clear()
        for k in self.parent.data.imageDictionary:
            self.imgIDS.append(k)

        index = 0

        for i, v in enumerate(self.imgIDS):
            if v == self.parent.data.currentImgId:
                index = i-1

        self.parent.data.currentImgId = self.imgIDS[index % len(self.imgIDS)]
        self.idLabel.config(text="Current Image ID: "+self.parent.data.currentImgId)
        self.parent.data.imageMaskArray = self.parent.data.loadRLE()
        self.parent.ImageDisplay.updateImages()

    def cycleNext(self):
        self.imgIDS.clear()
        for k in self.parent.data.imageDictionary:
            self.imgIDS.append(k)

        index = 0

        for i, v in enumerate(self.imgIDS):
            if v == self.parent.data.currentImgId:
                index = i+1

        self.parent.data.currentImgId = self.imgIDS[index % len(self.imgIDS)]
        self.idLabel.config(text="Current Image ID: "+self.parent.data.currentImgId)
        self.parent.data.imageMaskArray = self.parent.data.loadRLE()
        self.parent.ImageDisplay.updateImages()
        
    def openDataset(self):
        fileName = fd.askopenfilename(title='Open TDS File', filetypes=[("JSON Files", "*.json")])
        self.parent.data.fileName = fileName
        self.parent.ImageDisplay.updateImages()

    def openImgDir(self):
        imgDir = fd.askdirectory(title="Enter Directory Containing Segmented Images")
        self.parent.data.imgDir = imgDir
        self.parent.ImageDisplay.updateImages()

    def delButtonFunc(self):
        c = colors()
        confirmWindow = tkinter.Toplevel()
        confirmWindow.config(bg=c.darkMode[3])
        confirmWindow.resizable(False,False)
        
        confirmLabel = tkinter.Label(confirmWindow, text="Are you sure you want to delete the current image data?", highlightthickness=0, fg=c.darkMode[2], bg=c.darkMode[1])
        confirmLabel.grid(column=0, row=0, columnspan=2, pady=(10,10), padx=(10,10))

        confirmButton = tkinter.Button(confirmWindow, text="Yes", highlightthickness=0, fg=c.darkMode[2], bg=c.darkMode[1], command=lambda:[self.parent.data.deleteImgData(), confirmWindow.destroy(), self.cycleNext()])
        confirmButton.grid(column=0, row=1,pady=(10,20), padx=(50,0), sticky='nsw')

        returnButton = tkinter.Button(confirmWindow, text="No", highlightthickness=0, fg=c.darkMode[2], bg=c.darkMode[1] ,command=confirmWindow.destroy)
        returnButton.grid(column=1, row=1, pady=(10,20),padx=(0,50), sticky='nse')

class WindowClass(tkinter.Frame):
    def __init__(self, parent):            
        tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title('COCO Dataset Viewer')

        self.data = DataManager(self)

        self.ImageDisplay = ImageDisplay(self)
        self.ImageDisplay.grid(row = 0, column=0)

        self.Buttons = Buttons(self)
        self.Buttons.grid(row = 1, column=0, columnspan=2, sticky='NSEW')

def main():
    root = tkinter.Tk()

    root.geometry('800x445')

    window = WindowClass(root)
    window.pack(fill='both', expand=True)

    root.resizable(False, False)
    root.mainloop()

main()