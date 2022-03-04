import json
import os

##############################################################
## createCoco.py                                            ##
## Converts input data into COCO formatted JSON objects     ##
## Author: Gavin Moore                                      ##
## 10/1/2021                                                ##
##############################################################

class createCOCO:
    def checkAnnotation(self, value1, value2, dict):
        if not any(d['id'] == value1 and d['image_id'] == value2 for d in dict):
                return True
        else:
            return False

    def checkImage(self, value, dict):
        if not any(d['id'] == value for d in dict):
            return True
        else:
            return False

    def toJSON(self, fileName, outDict):
        with open(fileName, 'w') as outFile:
            json.dump(outDict, outFile, indent=4)
            outFile.close()

    def toCOCO(self, fileName,
               imgName=None, imgId=None, segList=None,        
               trainingData=None, imgHeight=None, imgWidth=None):
        if os.path.exists(fileName) == False:
            masterDict = {'images': [],
                         'annotation': [],
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
                                        'name': 'Ice/Snow',
                                        'supercategory': 'geo'
                                        },
                                        {
                                        'id': 4,
                                        'name': 'Sub Ice',
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
                jsonObj.close()

        masterDict = self.fromCOCO(fileName)
        imageCheck = self.checkImage(imgId, masterDict['images'])
        if imageCheck:
            masterDict['images'].append({
                'file_name': imgName,
                'height': imgHeight,
                'width': imgWidth,
                'id': imgId
            })
        for i in trainingData:
            counts = i[0]
            segID = i[1]
            cat = i[2]
            area = i[3]
            segIdStatus = self.checkAnnotation(segID, imgId, masterDict['annotation'])
            if cat != None and segIdStatus: # and self.checkDict(segID, masterDict['annotation']):
                masterDict['annotation'].append({
                    'id': segID,
                    'image_id': imgId,
                    'category_id': cat,
                    'segmentation': {
                                    'size': (imgWidth, imgHeight),
                                    'counts': counts
                                },
                    'area': area,
                    'bbox': segList,
                    'iscrowd': 1
                })
        with open(fileName, 'w') as jsonObj:
            json.dump(masterDict, jsonObj, indent=4)
            jsonObj.close()

    def fromCOCO(self, filePath):
        with open(filePath, 'r') as fileContent:
            localDict = json.load(fileContent)
        return localDict