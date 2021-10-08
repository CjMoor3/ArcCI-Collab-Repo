import json
import h5py

##############################################################
## createCoco.py                                            ##
## Converts input data into COCO formatted JSON objects     ##
## Author: Gavin Moore                                      ##
## 10/1/2021                                                ##
##############################################################

class createCOCO:
    def toCOCO(self, fileName,
               imgName=None, anoImg=None, area=None, segList=None,        
               category=None, trainingData=None):
        #trainingData[1] #counts
        #print(fileName)
        b = 0
        for i in trainingData:
            b += 1
            filePath = fileName + "." + str(b) + '.json'
            counts = i[0]
            segID = i[1]
            cat = i[2]
            if cat == 0:
                name = 'Water'
            elif cat == 1:
                name = 'Thin Ice'
            elif cat == 2:
                name = 'Shadow'
            elif cat == 3:
                name = 'Sub Ice'
            elif cat == 4:
                name = 'Ice/Snow'
            elif cat == 5:
                name = 'Melt Pond'
            else:
                name = 'No category'
            masterDict = {'annotation':
                                        {
                                        'id': segID,    ## Segment ID
                                        'image_id': imgName, ## Image Name
                                        'category_id': cat,
                                        'segmentation': {
                                                        'size': (256, 256),
                                                        'counts': counts
                                                        },
                                        'area': area,
                                        'bbox': segList,
                                        'isCrowd': 1
                                        },
                          'categories':
                                        {
                                        'id': cat,
                                        'name': name,
                                        'supercategory': None
                                        }}
            with open(filePath, 'w') as jsonObj:
                json.dump(masterDict, jsonObj, indent=4)

    def fromCOCO(self, filePath):
        with open(filePath, 'r') as fileContent:
            localDict = json.load(fileContent)
        return localDict

    def appendCOCO(self, filePath, 
                anoId=None, anoImg=None, anoCatId=None, anoSeg=None, area=None, segList=None, isCrowd=None,
                catId=None, catName=None, category=None, trainingData = None):
        jsonObj = open(filePath, 'r')
        bufferDict = json.load(jsonObj)
        jsonObj.close()
        bufferDict['annotation'] = self.getAnnotation(anoId, anoImg, anoCatId, anoSeg, area, segList, isCrowd)
        bufferDict['categories'] = self.getCategories(catId, catName, category)
        with open(filePath, 'w+') as jsonObj:
            json.dump(bufferDict, jsonObj, indent=4)
            jsonObj.close()

    def toH5(self, inputFilePath, outputFilePath):
        localDictionary = json.load(inputFilePath)
        h5File = h5py.File(outputFilePath)
        for i, b in localDictionary:
            h5File.create_dataset(i, data=b)
        h5File.close()
