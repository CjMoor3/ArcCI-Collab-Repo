import tkinter as tk
from tkinter import filedialog as fd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.image as mtpltimg
import os
import math
import json
import numpy as np
import webbrowser as wb

class colors:
    def __init__(self):
        self.darkMode = ['#36393F', '#2F3136', 'white', '#292B2F']
        self.segmentColors = ['#71b8eb', '#b1ddfc', '#707070', "#fff5a8", '#8d56ba', "#d97796", '#000000', "32FF00"]

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
        self.segCounts   = []
        self.statBool = False
        self.statString = ""

        self.currentSegmentID = None
        self.currentSegments = []
        self.currentCatID = None
        self.idArray = None
        self.currentImgId = None
        
        self.imagePlot = None

        if self.fileName == ():
            quit()
        else:
            try:
                self.currentImgId = self.fromJSON(self.fileName)['images'][0]['id']
            except TypeError:
                pass

        self.imageMaskArray = self.loadRLE()
    
    def hexToRGB(self, hexCode):
        return tuple(int(hexCode.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

    def fromJSON(self, fileName):
        try:    
            with open(fileName, "r") as jsonObj:
                returnDict = json.load(jsonObj)
                return returnDict
        except FileNotFoundError:
            return
    
    def changeCategory(self, catID):
        masterDict = self.fromJSON(self.fileName)
        
        for v in masterDict['annotation']:
            if v['id'] == self.currentSegmentID and v['image_id'] == self.currentImgId:
                v['category_id'] = catID
                
        with open(self.fileName, 'w') as outFile:
            json.dump(masterDict, outFile, indent=4)
            outFile.close()
            
    def onClick(self, event):
        if event.inaxes is not None:
            axesProps = event.inaxes.properties()
            
            x, y = 0, 0
            
            if axesProps['label'] == 'DatasetDisplay':
                x = int(event.xdata)
                y = int(event.ydata)
                
                self.parent.Data.currentSegmentID = int(self.parent.Data.idArray[y, x])
                
        self.parent.ImageDisplay.updateImages()
        
    def countCats(self, listParam):
        # Count Vars
        segBools = []
        segLabels = []
        segVals = []
        segCols = []

        counts = list(listParam.count(i) for i in range(6))
        bools = list(counts[i] > 0 for i in range(6))

        nameList = ["Water", "Thin Ice", "Shadow", "Snow", "Sub Ice", "Melt Pond"]
        
        for i, v in enumerate(bools):
            if v:
                segVals.append(counts[i])
                segCols.append(self.c.segmentColors[i])
                segLabels.append(nameList[i])
                    
        segCounts = list((counts[i] / self.currentSegCount) * 100 for i in range(6))
        
        self.segLabels = segLabels
        self.segVals   = segVals
        self.segCols   = segCols
        self.segCounts   = counts

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
            imagePlot = np.dstack(self.hexToRGB(self.c.darkMode[3]))
            self.imagePlot = imagePlot
        else:
            try:
                imgName = os.path.join(self.imgDir,os.path.relpath('img-' + self.currentImgId + '.jpg'))
                imagePlot = mtpltimg.imread(imgName)
            except FileNotFoundError as error:
                imgName = os.path.join(self.imgDir,os.path.relpath('img-' + self.currentImgId + '.tif'))
                imagePlot = mtpltimg.imread(imgName)
            self.imagePlot = imagePlot
                    
    def loadRLE(self):
        masterDict = self.fromJSON(self.fileName)

        subDict = [] # masterDict["annotation"]
        subDict.clear()

        try:
            subDict = [i for i in masterDict['annotation'] if i['image_id'] == self.currentImgId]
            
            self.currentSegments = []
            categoryCountList = []
                    

            self.getImgList()

            arraySize = subDict[0]["segmentation"]["size"]
            arraySize.append(3)
            
            if self.statBool == True:
                categoryCountList = [i['category_id'] for i in masterDict['annotation']]
                self.currentSegCount = len(masterDict['annotation'])
                self.statString = "Dataset"
            elif self.statBool == False:
                categoryCountList = [i['category_id'] for i in subDict]
                self.currentSegCount = len(subDict)
                self.statString = "Image"

            array = np.full(arraySize, 6)
            categoryArray = np.full(arraySize[0:2], 6).flatten()
            idNumArray = np.full(arraySize[0:2], 6).flatten()
            
            outlineSegment = None
            
            for i, count in enumerate(subDict):
                if count["id"] == self.currentSegmentID:
                    outlineSegment = count
                
                self.currentSegments.append(count['id'])
                
                countList = count["segmentation"]["counts"]
                
                boolean = False
                arrayIndex = 0
                for indivCount in countList:
                    if boolean:
                        categoryArray[arrayIndex:arrayIndex+indivCount] = count["category_id"]
                        idNumArray[arrayIndex:arrayIndex+indivCount] = count['id']
                          
                    arrayIndex += indivCount
                    boolean = not boolean
                    
            if outlineSegment is not None:
                boolean = False
                arrayIndex = 0
                for indivCount in outlineSegment["segmentation"]["counts"]:
                    if boolean:
                        for i in range(arrayIndex, arrayIndex+indivCount):
                            try:
                                if idNumArray[i-arraySize[0]] != outlineSegment["id"]:
                                    categoryArray[i] = 7
                                if idNumArray[i+arraySize[0]] != outlineSegment["id"]:
                                    categoryArray[i] = 7
                            except IndexError as error:
                                pass
                        categoryArray[arrayIndex] = 7
                        if arrayIndex + indivCount < 65536:
                            categoryArray[arrayIndex + indivCount] = 7
                        
                    arrayIndex += indivCount
                    boolean = not boolean
                    
            categoryArray = np.reshape(categoryArray, (arraySize[0:2]))
                    
            self.idArray = np.reshape(idNumArray, arraySize[0:2])
            self.countCats(categoryCountList)
            
            colorConverts = [self.hexToRGB(color) for color in self.c.segmentColors]
            for y in range(arraySize[0]):
                for x in range(arraySize[1]):
                    colorList = colorConverts[int(categoryArray[x, y])]
                    array[x, y] = colorList

            array = array.astype(dtype=np.uint8)
            masterDict.clear()
            subDict.clear()
            return array
        except TypeError:
            return np.dstack(self.hexToRGB(self.c.darkMode[3]))
        
    
class ButtonsLeft(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        c = colors()
        
        self.config(bg=c.darkMode[3])
        
        navLabel = tk.Label(self, text='Nav <- ->', fg=c.darkMode[2], bg=c.darkMode[1],)
        navLabel.grid(row=0, pady=(0,390))
        
        prevButton = tk.Button(self, text = '<--', height = 2, width=8, highlightthickness=0,fg=c.darkMode[2], bg=c.darkMode[1], command=lambda: self.cycleDataPrev())
        prevButton.grid(row=0, pady=(0,330), padx=(0, 0))
        
        nextButton = tk.Button(self, text='-->', height = 2, width = 8, highlightthickness=0,fg=c.darkMode[2], bg=c.darkMode[1], command=lambda: self.cycleDataNext())
        nextButton.grid(row=0, pady=(0, 260), padx=(0, 0))
        
        openDatasetButton = tk.Button(self, text='Open\nDataset', height=4, width=8, highlightthickness=0,fg=c.darkMode[2], bg=c.darkMode[1], command=lambda: self.openDataset())
        openDatasetButton.grid(row=0, pady=(0, 55))
        
        meltPondLabel = tk.Label(self, text='Melt\nPond', font=(None, 12), fg=c.segmentColors[5], bg=c.darkMode[1])
        meltPondLabel.grid(row=0, pady=(105, 0))
        
        subIceLabel = tk.Label(self, text='Sub\nIce', font=(None, 12), fg=c.segmentColors[4], bg=c.darkMode[1])
        subIceLabel.grid(row=0, pady=(190, 0))
        
        snowLabel = tk.Label(self, text='Snow', font=(None, 12), fg=c.segmentColors[3], bg=c.darkMode[1])
        snowLabel.grid(row=0, pady=(280, 0))
        
        shadowLabel = tk.Label(self, text='Shadow', font=(None, 12),fg=c.segmentColors[2], bg=c.darkMode[1])
        shadowLabel.grid(row=0, pady=(360, 0))
        
        thinIceLabel = tk.Label(self, text='Thin\nIce', font=(None, 12),fg=c.segmentColors[1], bg=c.darkMode[1])
        thinIceLabel.grid(row=0, pady=(450,0))
        
        waterLabel = tk.Label(self, text='Water', font=(None, 12),fg=c.segmentColors[0], bg=c.darkMode[1])
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

        self.parent.Data.currentImgId = self.imgIDS[index % len(self.imgIDS)]
        self.parent.ButtonsCenter.imageIdLabel.config(text="Current Image ID: "+self.parent.Data.currentImgId)
        self.parent.Data.imageMaskArray = self.parent.Data.loadRLE()
        self.parent.ImageDisplay.updateImages()
  
    def openDataset(self):
        fileName = fd.askopenfilename(title='Open TDS File', filetypes=[("JSON Files", "*.json")])
        self.parent.Data.currentImgId = self.parent.Data.fromJSON(fileName)['images'][0]['id']
        self.parent.Data.fileName = fileName
        self.parent.ImageDisplay.updateImages()
           
class ButtonsCenter(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.c = colors()
        self.imgIDS = []
        self.getImgIDS()
        
        self.config(bg=self.c.darkMode[3])
        
        graphLabel = tk.Label(self, text='Tally of Current Segments', fg=self.c.darkMode[2], bg=self.c.darkMode[1])
        graphLabel.grid(row=0, column=0, padx=(0, 80))
        
        self.imageIdLabel = tk.Label(self, text='Current Image ID',fg=self.c.darkMode[2], bg=self.c.darkMode[1])
        self.imageIdLabel.grid(row=1, column=0, pady=(5,35))
        
        self.segCountLabel = tk.Label(self, text='Current Total Segments: '+str(self.parent.Data.currentSegCount),fg=self.c.darkMode[2], bg=self.c.darkMode[1])
        self.segCountLabel.grid(row=0, column=1)
        
        delButton = tk.Button(self, text='DELETE', height=2, width=8, highlightthickness=0, command=self.delButtonFunc, fg=self.c.darkMode[2], bg=self.c.darkMode[1])
        delButton.grid(row=1, column=1, pady=(20,0), padx=(80,0))
        
        self.statsLabel = tk.Label(self, text='Current Statistics:\n'+str(self.parent.Data.statString),fg=self.c.darkMode[2], bg=self.c.darkMode[1])
        self.statsLabel.grid(row=0, column=2, rowspan=2, padx=(25, 0))
        
        self.imgVar = tk.StringVar(self)
        self.imgVar.set(self.imgIDS[0])
        
        imgIdDropdown = tk.OptionMenu(self, self.imgVar, *self.imgIDS, command=self.selectImg)
        imgIdDropdown.config(fg=self.c.darkMode[2], bg=self.c.darkMode[1])
        imgIdDropdown.grid(row=1, column=0, pady=(20,0))
        
    def getImgIDS(self):
        self.imgIDS.clear()
        self.imgIDS = [k for k in self.parent.Data.imageDictionary]
        
    def selectImg(self, choice):
        choice = self.imgVar.get()
        self.parent.Data.currentImgId = choice
        self.parent.Data.imageMaskArray = self.parent.Data.loadRLE()
        self.parent.ImageDisplay.updateImages()
        
    def delButtonFunc(self):
        confirmWindow = tk.Toplevel()
        confirmWindow.config(bg=self.c.darkMode[3])
        confirmWindow.resizable(False,False)

        
        confirmLabel = tk.Label(confirmWindow, text="Are you sure you want to delete the current image data?", highlightthickness=0, fg=self.c.darkMode[2], bg=self.c.darkMode[1])
        confirmLabel.grid(column=0, row=0, columnspan=2, pady=(10,10), padx=(10,10))

        confirmButton = tk.Button(confirmWindow, text="Yes", highlightthickness=0, fg=self.c.darkMode[2], bg=self.c.darkMode[1], command=lambda:[self.parent.Data.deleteImgData(), confirmWindow.destroy(), self.parent.ButtonsLeft.cycleDataNext()])
        confirmButton.grid(column=0, row=1,pady=(10,20), padx=(50,0), sticky='nsw')

        returnButton = tk.Button(confirmWindow, text="No", highlightthickness=0, fg=self.c.darkMode[2], bg=self.c.darkMode[1] ,command=confirmWindow.destroy)
        returnButton.grid(column=1, row=1, pady=(10,20),padx=(0,50), sticky='nse')
            
class ButtonsRight(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.c = colors()
        
        self.config(bg=self.c.darkMode[3])
        
        imgDirButton = tk.Button(self, text='Open Img\nDirectory', height=4, width=8, highlightthickness=0, command=lambda: self.openImgDir(), fg=self.c.darkMode[2], bg=self.c.darkMode[1])
        imgDirButton.grid(row=0, pady=(510, 0))
        
        helpButton = tk.Button(self, text='Help!', width=8, height=4, highlightthickness=0, command=self.getHelp, fg=self.c.darkMode[2], bg=self.c.darkMode[1])
        helpButton.grid(row=0, pady=(0, 400))
        
        nextButton = tk.Button(self, text='->', width=3, height=2,  highlightthickness=0, fg=self.c.darkMode[2], bg=self.c.darkMode[1], command=lambda: self.nextSegment())
        nextButton.grid(row=0, pady=(0, 160), padx=(30, 0))
        
        prevButton = tk.Button(self, text='<-', width=3, height=2,  highlightthickness=0, fg=self.c.darkMode[2], bg=self.c.darkMode[1], command=lambda: self.prevSegment())
        prevButton.grid(row=0, pady=(0, 160), padx=(0, 30))
        
        waterButton = tk.Button(self, width=2, text='0', highlightthickness=0, fg=self.c.segmentColors[0], bg=self.c.darkMode[1], command=lambda: self.changeCat(0))
        waterButton.grid(row=0, pady=(40,0), padx=(0, 30))
        
        thinIceButton = tk.Button(self, width=2, text='1', highlightthickness=0, fg=self.c.segmentColors[1], bg=self.c.darkMode[1], command=lambda: self.changeCat(1))
        thinIceButton.grid(row=0, pady=(40,0), padx=(30, 0))
        
        shadowButton = tk.Button(self, width=2, text='2', highlightthickness=0, fg=self.c.segmentColors[2], bg=self.c.darkMode[1], command=lambda: self.changeCat(2))
        shadowButton.grid(row=0, pady=(90,0), padx=(0, 30))
        
        snowButton = tk.Button(self, width=2, text='3', highlightthickness=0, fg=self.c.segmentColors[3], bg=self.c.darkMode[1], command=lambda: self.changeCat(3))
        snowButton.grid(row=0, pady=(90, 0), padx=(30, 0)) 
        
        subIceButton = tk.Button(self, width=2, text='4', highlightthickness=0, fg=self.c.segmentColors[4], bg=self.c.darkMode[1], command=lambda: self.changeCat(4))
        subIceButton.grid(row=0, pady=(140,0), padx=(0, 30))
        
        meltPondButton = tk.Button(self, width=2, text='5', highlightthickness=0, fg=self.c.segmentColors[5], bg=self.c.darkMode[1], command=lambda: self.changeCat(5))
        meltPondButton.grid(row=0, pady=(140, 0), padx=(30, 0))
        
        switchStatsButton = tk.Button(self, width=6, text='Switch\nStats', highlightthickness=0, fg=self.c.darkMode[2], bg= self.c.darkMode[1], command=lambda: self.switchStats())
        switchStatsButton.grid(row=0, pady=(300, 0), padx=(15, 15))
        
        self.currentSegIDLabel = tk.Label(self, text='Current\nSeg ID:\n'+str(self.parent.Data.currentSegmentID),highlightthickness=0, fg=self.c.darkMode[2], bg=self.c.darkMode[1])
        self.currentSegIDLabel.grid(row=0, pady=(0, 265))
        
        self.currentCatIDLabel = tk.Label(self, text='Current\nCat ID:\n'+str(self.parent.Data.currentCatID),highlightthickness=0, fg=self.c.darkMode[2], bg=self.c.darkMode[1])
        self.currentCatIDLabel.grid(row=0, pady=(0, 50))
        
    def openImgDir(self):
        imgDir = fd.askdirectory(title='Enter Directory Containing Segmented Images')
        if imgDir != "":
            self.parent.Data.imgDir = imgDir
            self.parent.ImageDisplay.updateImages()
        
    def getHelp(self):
        wb.open('https://github.com/CjMoor3/ArcCI-Collab-Repo/wiki/ViewCOCO')
        
    def nextSegment(self):
        index = 0
        
        if self.parent.Data.currentSegmentID == None:
            self.parent.Data.currentSegmentID = self.parent.Data.currentSegments[0]
            self.categoryID = self.parent.Data.currentCatID
        else:
            for i, v in enumerate(self.parent.Data.currentSegments):
                if v == self.parent.Data.currentSegmentID:
                    index = i+1
                    
            self.parent.Data.currentSegmentID = self.parent.Data.currentSegments[index]
            
        self.parent.ImageDisplay.updateImages()
        
    def prevSegment(self):
        index = 0
        
        if self.parent.Data.currentSegmentID == None:
            self.parent.Data.currentSegmentID = self.parent.Data.currentSegments[-1]
            self.categoryID = self.parent.Data.currentCatID
        else:
            for i, v in enumerate(self.parent.Data.currentSegments):
                if v == self.parent.Data.currentSegmentID:
                    index = i-1
                    
            self.parent.Data.currentSegmentID = self.parent.Data.currentSegments[index]
            
        self.parent.ImageDisplay.updateImages()
        
    def changeCat(self, catID):
        self.parent.Data.changeCategory(catID)
        self.parent.ImageDisplay.updateImages()
        
    def switchStats(self):
        self.parent.Data.statBool = not self.parent.Data.statBool
        self.parent.ImageDisplay.updateImages()
        
          
class ImageDisplay(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.c = colors()
        
        self.graph = Figure(figsize=(6,6))
        self.canvas = FigureCanvasTkAgg(self.graph, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(sticky='NSEW', padx=((0,0)))
        
        self.graph.subplots_adjust(left = 0.01, right = 0.99,
                            bottom = 0.05, top = 0.99,
                            wspace = 0.05, hspace = 0.05)
        
        self.graph.set_facecolor(self.c.darkMode[3])
        
        self.topLeftDisplay = self.graph.add_subplot(2,2,1, label='DatasetDisplay')
        self.topRightDisplay = self.graph.add_subplot(2,2,4, label='PieChart')
        self.botLeftDisplay = self.graph.add_subplot(2,2,3, label="BarChart")
        self.botRightDisplay = self.graph.add_subplot(2,2,2, label='ImageDisplay')
        
        self.updateImages()
         
    def updateImages(self):
        self.parent.Data.imageMaskArray = self.parent.Data.loadRLE()
        self.parent.Data.loadImage()
        
        self.topLeftDisplay.clear()
        self.topLeftDisplay.imshow(self.parent.Data.imageMaskArray)
        self.topLeftDisplay.tick_params(axis='both',  # changes apply to the x-axis
                       which='both',             # both major and minor ticks are affected
                       bottom=False,             # ticks along the bottom edge are off
                       top=False,                # ticks along the top edge are off
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)
        
        
        self.topRightDisplay.clear()
        self.topRightDisplay.pie(self.parent.Data.segVals, labels=self.parent.Data.segLabels, colors=self.parent.Data.segCols, autopct="%1.1f%%", startangle=45, radius=0.7, textprops={'color':'grey'})
        self.topRightDisplay.tick_params(axis='both', # changes apply to the x-axis
                       which='both',                  # both major and minor ticks are affected
                       bottom=False,                  # ticks along the bottom edge are off
                       top=False,                     # ticks along the top edge are off
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)
        
        self.botLeftDisplay.clear()
        self.botLeftDisplay.set_facecolor(self.c.darkMode[3])
        try:
            self.botLeftDisplay.barh(self.parent.Data.segLabelsConst, self.parent.Data.segCounts)
        except ValueError:
            pass
        self.botLeftDisplay.set_xlim([0, sum(self.parent.Data.segCounts)])
        self.botLeftDisplay.tick_params(axis='both', # changes apply to the x-axis
                       which='both',            # both major and minor ticks are affected
                       bottom=True,
                       right=False,
                       labelleft=True,
                       labelbottom=True,
                       colors='white')
        
        self.botRightDisplay.clear()
        self.botRightDisplay.imshow(self.parent.Data.imagePlot)
        self.botRightDisplay.tick_params(axis='both', # changes apply to the x-axis
                       which='both',             # both major and minor ticks are affected
                       bottom=False,             # ticks along the bottom edge are off
                       top=False,                # ticks along the top edge are off
                       left=False,
                       right=False,
                       labelleft=False,
                       labelbottom=False)
        
        try:
            self.parent.ButtonsRight.currentSegIDLabel.config(text='Current\nSeg ID:\n'+str(self.parent.Data.currentSegmentID))
            self.parent.ButtonsRight.currentCatIDLabel.config(text='Current\nCat ID:\n'+str(self.parent.Data.currentCatID))
            self.parent.ButtonsCenter.statsLabel.config(text='Current Statistics\n'+str(self.parent.Data.statString))
            self.parent.ButtonsCenter.segCountLabel.config(text='Current Total Segments: '+str(self.parent.Data.currentSegCount))
        except AttributeError:
            pass
        self.graph.canvas.mpl_connect('button_press_event', self.parent.Data.onClick)
        self.canvas.draw()
        
             
class WindowClass(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title('ViewCOCO')
        
        self.Data = DataManager(self)
        
        self.ImageDisplay = ImageDisplay(self)
        self.ImageDisplay.grid(row = 0, column=1, sticky='N', padx=(0, 0))
        
        self.ButtonsLeft = ButtonsLeft(self)
        self.ButtonsLeft.grid(row = 0, column = 0, rowspan=3, sticky='NSW')
        self.ButtonsCenter = ButtonsCenter(self)
        self.ButtonsCenter.grid(row = 1, column = 1, sticky='WE')
        self.ButtonsRight = ButtonsRight(self)
        self.ButtonsRight.grid(row = 0, column = 2, rowspan = 3, sticky='NSE')
            
if __name__ == '__main__':
    root = tk.Tk()
    
    root.geometry('735x680')
    
    window = WindowClass(root)
    window.pack(fill='both', expand=True)
    
    root.resizable(False, False)
    root.mainloop()
