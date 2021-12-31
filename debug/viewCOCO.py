import tkinter as tk
from tkinter import Label, filedialog as fd
from tkinter import font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.image as mtpltimg
import os
import math
import json
import numpy
import webbrowser

class colors:
    def __init__(self):
        self.darkMode = ['#36393F', '#2F3136', 'white', '#292B2F']
        self.segmentColors = ['#71b8eb', '#b1ddfc', '#707070', '#8d56ba', "#fff5a8", "#d97796"]

class DataManager():
    def __init__(self, parent):
        filetypes = [('json files', '*.json')]
        self.fileName = fd.askopenfilename(title="Open TDS data file", filetypes=filetypes)
        self.parent = parent
        self.imgDir = None
        self.imageDictionary = {}
        self.c = colors()
        
        # Statistic vars used to display stats about the current dataset
        self.currentSegCount = 0
        self.segVals   = []
        self.segLabelsConst = ['Water', 'Thin Ice', 'Shadow', 'Sub Ice', 'Snow', 'Melt Pond']
        self.segLabels = []     
        self.segCols   = []
        self.segPcts   = []

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

    def countCats(self, listParam):
        # Count Vars
        waterCount = thinCount = shadowCount = subCount = snowCount = meltCount = 0
        waterBool = thinBool = shadowBool = subBool = snowBool = meltBool = False
        segBools = []
        segLabels = []
        segVals = []
        segCols = []
                    
        for i in listParam:
            if i == 0:
                waterCount += 1
                waterBool = True
            if i == 1:
                thinCount += 1
                thinBool = True
            if i == 2:
                shadowCount += 1
                shadowBool = True
            if i == 3:
                subCount += 1
                subBool = True
            if i == 4:
                snowCount += 1
                snowBool = True
            if i == 5:
                meltCount += 1
                meltBool = True
        
        segBools = [waterBool, thinBool, shadowBool, subBool, snowBool, meltBool]
        
        for i, v in enumerate(segBools):
            if v == True:
                if i == 0:
                    segLabels.append('Water')
                    segVals.append(waterCount)
                    segCols.append('#71b8eb')
                if i ==  1:
                    segLabels.append('Thin Ice')
                    segVals.append(thinCount)
                    segCols.append('#b1ddfc')
                if i == 2:
                    segLabels.append('Shadow')
                    segVals.append(shadowCount)
                    segCols.append('#707070')
                if i == 3:
                    segLabels.append('Sub Ice')
                    segVals.append(subCount)
                    segCols.append('#8d56ba')
                if i == 4:
                    segLabels.append('Snow')
                    segVals.append(snowCount)
                    segCols.append("#fff5a8")
                if i == 5:
                    segLabels.append('Melt Pond') 
                    segVals.append(meltCount)
                    segCols.append("#d97796")
                    
        waterPct  = (waterCount /self.currentSegCount) * 100
        thinPct   = (thinCount  /self.currentSegCount) * 100
        shadowPct = (shadowCount/self.currentSegCount) * 100
        subPct    = (subCount   /self.currentSegCount) * 100
        snowPct   = (snowCount  /self.currentSegCount) * 100
        meltPct   = (meltCount  /self.currentSegCount) * 100
        segPcts = [waterPct, thinPct, shadowPct, subPct, snowPct, meltPct]
        
        self.segLabels = segLabels
        self.segVals  = segVals
        self.segCols = segCols
        self.segPcts = segPcts

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
        masterDict = self.fromJSON(self.fileName)

        subDict = [] # masterDict["annotation"]
        subDict.clear()

        for i in masterDict['annotation']:
            if i['image_id'] == self.currentImgId:
                subDict.append(i)
                
        categoryCountList = []
                
        self.currentSegCount = len(subDict)

        self.getImgList()

        arraySize = subDict[0]["segmentation"]["size"]
        arraySize.append(3)

        array = numpy.zeros(arraySize)
        categoryArray = numpy.zeros(arraySize[0:2])

        for i, count in enumerate(subDict):
            booleanSize = count["segmentation"]["size"][0:2]
            
            categoryCountList.append(count['category_id'])

            countList = count["segmentation"]["counts"]
            boolean = False
            arrayIndex = 0
            for indivCount in countList:
                for b in range(indivCount):
                    xIndex = arrayIndex % booleanSize[0]
                    yIndex = math.floor(arrayIndex / booleanSize[0])
                    if boolean:
                        categoryArray[xIndex, yIndex] = count["category_id"]

                    arrayIndex += 1

                boolean = not boolean
                
        self.countCats(categoryCountList)
                       
        for y in range(booleanSize[0]):
            for x in range(booleanSize[1]):
                colorList = self.hexToRGB(self.c.segmentColors[int(categoryArray[x, y])])
                array[y, x] = colorList

        array = array.astype(dtype=numpy.uint8)
        return array
    
class ButtonsLeft(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        self.config(bg='#292B2F')
        
        navLabel = tk.Label(self, text='Nav <- ->')
        navLabel.grid(row=0, pady=(0,390))
        
        prevButton = tk.Button(self, text = '<--', height = 2, width=8, highlightthickness=0, command=lambda: self.cycleDataPrev())
        prevButton.grid(row=0, pady=(0,330), padx=(0, 0))
        
        nextButton = tk.Button(self, text='-->', height = 2, width = 8, highlightthickness=0, command=lambda: self.cycleDataNext())
        nextButton.grid(row=0, pady=(0, 260), padx=(0, 0))
        
        openDatasetButton = tk.Button(self, text='Open\nDataset', height=4, width=8, highlightthickness=0, command=lambda: self.openDataset())
        openDatasetButton.grid(row=0, pady=(0, 55))
        
        meltPondLabel = tk.Label(self, text='Melt\nPond', font=(None, 12))
        meltPondLabel.grid(row=0, pady=(105, 0))
        
        snowLabel = tk.Label(self, text='Snow', font=(None, 12))
        snowLabel.grid(row=0, pady=(190, 0))
        
        subIceLabel = tk.Label(self, text='Sub\nIce', font=(None, 12))
        subIceLabel.grid(row=0, pady=(280, 0))
        
        shadowLabel = tk.Label(self, text='Shadow', font=(None, 12))
        shadowLabel.grid(row=0, pady=(360, 0))
        
        thinIceLabel = tk.Label(self, text='Thin\nIce', font=(None, 12))
        thinIceLabel.grid(row=0, pady=(450,0))
        
        waterLabel = tk.Label(self, text='Water', font=(None, 12))
        waterLabel.grid(row=0, pady=(525,0))
        
        self.imgIDS = []
        
    def cycleDataPrev(self):
        self.imgIDS.clear()
        for k in self.parent.Data.imageDictionary:
            self.imgIDS.append(k)
            
        index = 0
        
        for i, v in enumerate(self.imgIDS):
            if v == self.parent.Data.currentImgId:
                index = i-1
                
        self.parent.ImageDisplay.topRightDisplay.clear()
        self.parent.Data.currentImgId = self.imgIDS[index%len(self.imgIDS)]
        self.parent.ButtonsCenter.imageIdLabel.config(text='Current Image ID: '+self.parent.Data.currentImgId)
        self.parent.Data.imageMaskArray = self.parent.Data.loadRLE()
        self.parent.ImageDisplay.updateImages()
        
    def cycleDataNext(self):
        self.imgIDS.clear()
        for k in self.parent.Data.imageDictionary:
            self.imgIDS.append(k)

        index = 0

        for i, v in enumerate(self.imgIDS):
            if v == self.parent.Data.currentImgId:
                index = i+1

        self.parent.ImageDisplay.topRightDisplay.clear()
        self.parent.Data.currentImgId = self.imgIDS[index % len(self.imgIDS)]
        self.parent.ButtonsCenter.imageIdLabel.config(text="Current Image ID: "+self.parent.Data.currentImgId)
        self.parent.Data.imageMaskArray = self.parent.Data.loadRLE()
        self.parent.ImageDisplay.updateImages()
  
    def openDataset(self):
        fileName = fd.askopenfilename(title='Open TDS File', filetypes=[("JSON Files", "*.json")])
        self.parent.Data.fileName = fileName
        self.parent.ImageDisplay.updateImages()
           
class ButtonsCenter(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.c = colors()
        
        self.config(bg='#292B2F')
        
        graphLabel = tk.Label(self, text='Percentage of Current Segments')
        graphLabel.grid(row=0, column=0, padx=(0, 80))
        
        self.imageIdLabel = tk.Label(self, text='Current Image ID: '+self.parent.Data.currentImgId)
        self.imageIdLabel.grid(row=1, column=0, pady=(20,20))
        
        self.segCountLabel = tk.Label(self, text='Current Total Segments: '+str(self.parent.Data.currentSegCount))
        self.segCountLabel.grid(row=0, column=1)
        
        delButton = tk.Button(self, text='DELETE', height=2, width=8, highlightthickness=0, command=self.delButtonFunc)
        delButton.grid(row=1, column=1, pady=(20,0), padx=(80,0))
        
    def delButtonFunc(self):
        confirmWindow = tk.Toplevel()
        confirmWindow.config(bg=self.c.darkMode[3])
        confirmWindow.resizable(False,False)
        
        confirmLabel = tk.Label(confirmWindow, text="Are you sure you want to delete the current image data?", highlightthickness=0, fg=self.c.darkMode[2], bg=self.c.darkMode[1])
        confirmLabel.grid(column=0, row=0, columnspan=2, pady=(10,10), padx=(10,10))

        confirmButton = tk.Button(confirmWindow, text="Yes", highlightthickness=0, fg=self.c.darkMode[2], bg=self.c.darkMode[1], command=lambda:[self.parent.Data.deleteImgData(), confirmWindow.destroy(), self.cycleNext()])
        confirmButton.grid(column=0, row=1,pady=(10,20), padx=(50,0), sticky='nsw')

        returnButton = tk.Button(confirmWindow, text="No", highlightthickness=0, fg=self.c.darkMode[2], bg=self.c.darkMode[1] ,command=confirmWindow.destroy)
        returnButton.grid(column=1, row=1, pady=(10,20),padx=(0,50), sticky='nse')
            
class ButtonsRight(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        self.config(bg='#292B2F')
        
        imgDirButton = tk.Button(self, text='Open Img\nDirectory', height=4, width=8, highlightthickness=0, command=lambda: self.openImgDir())
        imgDirButton.grid(row=0, pady=(510, 0))
        
        helpButton = tk.Button(self, text='Help!', width=8, height=4, highlightthickness=0, command=self.getHelp)
        helpButton.grid(row=0, pady=(0, 0))
        
    def openImgDir(self):
        imgDir = fd.askopenfilename(title='Enter Directory Containing Segmented Images')
        self.parent.Data.imgDir = imgDir
        self.parent.ImageDisplay.updateImages()
        
    def getHelp(self):
        webbrowser.open('https://github.com/CjMoor3/ArcCI-Collab-Repo/wiki')
          
class ImageDisplay(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.c = colors()
        
        self.graph = Figure(figsize=(6,6))
        self.graph.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.graph, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(sticky='NSEW', padx=((0,0)))
        
        self.graph.subplots_adjust(left = 0.01, right = 0.99,
                            bottom = 0.05, top = 0.99,
                            wspace = 0.05, hspace = 0.05)
        
        self.graph.set_facecolor(self.c.darkMode[3])
        
        self.updateImages()
         
    def updateImages(self):
        self.parent.Data.loadImage()
        topLeftDisplay = self.graph.add_subplot(2,2,1)
        topLeftDisplay.imshow(self.parent.Data.imageMaskArray)
        topLeftDisplay.tick_params(axis='both',  # changes apply to the x-axis
                       which='both',             # both major and minor ticks are affected
                       bottom=False,             # ticks along the bottom edge are off
                       top=False,                # ticks along the top edge are off
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)
        
        self.topRightDisplay = self.graph.add_subplot(2,2,2)
        self.topRightDisplay.pie(self.parent.Data.segVals, labels=self.parent.Data.segLabels, colors=self.parent.Data.segCols, autopct="%1.1f%%", startangle=45, radius=0.7, textprops={'color':'grey'})
        self.topRightDisplay.tick_params(axis='both', # changes apply to the x-axis
                       which='both',                  # both major and minor ticks are affected
                       bottom=False,                  # ticks along the bottom edge are off
                       top=False,                     # ticks along the top edge are off
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)
        
        botLeftDisplay = self.graph.add_subplot(2,2,3)
        botLeftDisplay.set_facecolor(self.c.darkMode[3])
        botLeftDisplay.set_autoscalex_on(False)
        botLeftDisplay.barh(self.parent.Data.segLabelsConst, self.parent.Data.segPcts, color=self.c.segmentColors)
        botLeftDisplay.set_xlim([0, 100])
        botLeftDisplay.tick_params(axis='both', # changes apply to the x-axis
                       which='both',            # both major and minor ticks are affected
                       bottom=True,
                       right=False,
                       labelleft=True,
                       labelbottom=True,
                       colors='white')
        
        botRightDisplay = self.graph.add_subplot(2,2,4)
        botRightDisplay.imshow(self.parent.Data.imagePlot)
        botRightDisplay.tick_params(axis='both', # changes apply to the x-axis
                       which='both',             # both major and minor ticks are affected
                       bottom=False,             # ticks along the bottom edge are off
                       top=False,                # ticks along the top edge are off
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)
       
        self.canvas.draw()
             
class WindowClass(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title('VIEWCOCO 2.0')
        
        self.Data = DataManager(self)
        
        self.ImageDisplay = ImageDisplay(self)
        self.ImageDisplay.grid(row = 0, column=1, sticky='N', padx=(0, 0))
        
        self.ButtonsLeft = ButtonsLeft(self)
        self.ButtonsLeft.grid(row = 0, column = 0, rowspan=3, sticky='NSW')
        self.ButtonsCenter = ButtonsCenter(self)
        self.ButtonsCenter.grid(row = 1, column = 1, sticky='WE')
        self.ButtonsRight = ButtonsRight(self)
        self.ButtonsRight.grid(row = 0, column = 2, rowspan = 3, sticky='NSE')
            
def main():
    root = tk.Tk()
    
    root.geometry('765x675')
    
    window = WindowClass(root)
    window.pack(fill='both', expand=True)
    
    root.resizable(False, False)
    root.mainloop()
    
main()