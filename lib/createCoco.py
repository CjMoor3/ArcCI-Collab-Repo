import json
import h5py

##############################################################
## createCoco.py                                            ##
## Converts input data into COCO formatted JSON objects     ##
## Author: Gavin Moore                                      ##
## 10/1/2021                                                ##
##############################################################

class createCOCO:
    def getAnnotation(self, anoId=None, anoImg=None, anoCatId=None, anoSeg=None, area=None, segList=None, isCrowd=None):
        retAnnotation = {'id': anoId, 'image_id': anoImg, 'category_id': anoCatId, 'segmentation': anoSeg,
                         'area': area,'bbox': [segList], 'iscrowd': isCrowd}
        return retAnnotation

    def getCategories(self, catId=None, catName=None, category=None):
        retCategories = {'id': [catId], 'name': catName, 'supercategory': category}
        return retCategories
    
    def toCOCO(self, fileName,
               anoId=None, anoImg=None, anoCatId=None, anoSeg=None, area=None, segList=None, isCrowd=None,          ## Parameters for getAnnotation()
               catId=None, catName=None, category=None                                                              ## Parameters for getCategories()
               ):
        masterDict = {'annotation': self.getAnnotation(anoId, anoImg, anoCatId, anoSeg, area, segList, isCrowd),
                      'categories': self.getCategories(catId, catName, category)}
        with open(fileName, 'w') as jsonObj:
            json.dump(masterDict, jsonObj, indent=4)

    def fromCOCO(self, filePath):
        with open(filePath, 'r') as fileContent:
            localDict = json.load(fileContent)
        return localDict

    def appendCOCO(self, filePath, 
                anoId=None, anoImg=None, anoCatId=None, anoSeg=None, area=None, segList=None, isCrowd=None,
                catId=None, catName=None, category=None):
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