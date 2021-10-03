import json
import h5py

##############################################################
## createCoco.py                                            ##
## Converts input data into COCO formatted JSON objects     ##
## Author: Gavin Moore                                      ##
## 10/1/2021                                                ##
##############################################################

class createCOCO:
    def getInfo(self, year=None, version=None, desc=None, contrib=None, url=None, dateCrea=None):
        retInfo = {'year': year, 'version': version, 'description': desc,
                   'contributor': contrib, 'url': url, 'date_created': dateCrea}
        return retInfo
    
    def getImage(self, imgId=None, width=None, height=None, imgFileName=None, imgLic=None, flckrUrl=None, dateCap=None):
        retImage = {'id': imgId, "width": width, "height": height, "file_name": imgFileName,
                    "license": imgLic, "flickr_url": flckrUrl, "date_captured": dateCap}
        return retImage

    def getLicense(self, licId=None, licName=None, licUrl=None):
        retLicense = {'id': licId, 'name': licName, 'url': licUrl}
        return retLicense

    def getAnnotation(self, anoId=None, anoImg=None, anoCatId=None, anoSeg=None, area=None, segList=None, isCrowd=None):
        retAnnotation = {'id': anoId, 'image_id': anoImg, 'category_id': anoCatId, 'segmentation': anoSeg,
                         'area': area,'bbox': [segList], 'iscrowd': isCrowd}
        return retAnnotation

    def getCategories(self, catId=None, catName=None, category=None):
        retCategories = {'id': [catId], 'name': catName, 'supercategory': category}
        return retCategories
    
    def toCOCO(self, fileName,
               year=None, version=None, desc=None, contrib=None, url=None, dateCrea=None,                           ## Parameters for getInfo()
               imgId=None, width=None, height=None, imgFileName=None, imgLic=None, flckrUrl=None, dateCap=None,     ## Parameters for getImage()
               licId=None, licName=None, licUrl=None,                                                               ## Parameters for getLicense()
               anoId=None, anoImg=None, anoCatId=None, anoSeg=None, area=None, segList=None, isCrowd=None,          ## Parameters for getAnnotation()
               catId=None, catName=None, category=None                                                              ## Parameters for getCategories()
               ):
        masterDict = {'info': self.getInfo(year, version, desc, contrib, url, dateCrea),
                      'image': self.getImage(imgId, width, height, imgFileName, imgLic, flckrUrl, dateCap),
                      'license': self.getLicense(licId, licName, licUrl),
                      'annotation': self.getAnnotation(anoId, anoImg, anoCatId, anoSeg, area, segList, isCrowd),
                      'categories': self.getCategories(catId, catName, category)}
        with open(fileName, 'w') as jsonObj:
            json.dump(masterDict, jsonObj, indent=4)

    def fromCOCO(self, filePath):
        with open(filePath, 'r') as fileContent:
            localDict = json.load(fileContent)
        return localDict

    def toH5(self, inputFilePath, outputFilePath):
        localDictionary = json.load(inputFilePath)
        h5File = h5py.File(outputFilePath)
        for i, b in localDictionary:
            h5File.create_dataset(i, data=b)
        h5File.close()