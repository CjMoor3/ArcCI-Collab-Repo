import json
from typing import Any
import h5py
import os

##############################################################
## createCoco.py                                            ##
## Converts input data into COCO formatted JSON objects     ##
## Author: Gavin Moore                                      ##
## 10/1/2021                                                ##
##############################################################

class createCOCO:
    def checkDict(self, value1, value2, dict):
        if not any(d['id'] == value1 and d['image_id'] == value2 for d in dict):
                return True   
        else:
            return False

    def toCOCO(self, fileName,
               imgName=None, anoImg=None, area=None, segList=None,        
               category=None, trainingData=None):
        if os.path.exists(fileName) == False:
            masterDict = {'annotation': [],
                         'categories':
                                        [
                                        {
                                        'id': 0,
                                        'name': 'Water',
                                        'supercategory': 'geo'
                                        },
                                        {
                                        'id': 1,
                                        'name': 'Thin Ice',
                                        'supercategory': 'geo'
                                        },
                                        {
                                        'id': 2,
                                        'name': 'Shadow',
                                        'supercategory': 'geo'
                                        },
                                        {
                                        'id': 3,
                                        'name': 'Shadow',
                                        'supercategory': 'geo'
                                        },
                                        {
                                        'id': 4,
                                        'name': 'Ice/Snow',
                                        'supercategory': 'geo'
                                        },
                                        {
                                        'id': 5,
                                        'name': 'Melt Pond',
                                        'supercategory': 'geo'
                                        }
                                        ]
                            }
            with open(fileName, 'w') as jsonObj:
                json.dump(masterDict, jsonObj, indent=4)

        elif os.path.exists(fileName) == True:
                masterDict = self.fromCOCO(fileName)
                for i in trainingData:
                    counts = i[0]
                    segID = i[1]
                    cat = i[2]
                    segIdStatus = self.checkDict(i[1], imgName, masterDict['annotation'])
                    if cat != None and segIdStatus: # and self.checkDict(segID, masterDict['annotation']):
                        masterDict['annotation'].append({
                            'id': segID,
                            'image_id': imgName,
                            'category_id': cat,
                            'segmentation': {
                                            'size': (256, 256),
                                            'counts': counts
                                        },
                            'area': area,
                            'bbox': segList,
                            'iscrowd': 1
                        })
                with open(fileName, 'w') as jsonObj:
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










    def appendCOCO(self, filePath):
        masterDict = self.fromCOCO(filePath)

        transferDict = masterDict["annotation"]

        

