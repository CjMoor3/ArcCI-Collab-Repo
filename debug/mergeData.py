import os
import json
import argparse
from datetime import date

def fromJSON(fileName) -> dict:
    with open(fileName, 'r') as file:
        returnDict =  json.load(file)
        return returnDict
    
def toJSON(fileName, masterDict):
    with open(fileName, 'w') as file:
        json.dump(masterDict, file, indent=3)
        file.close()
        
def mergeData(dictList):
    imagesDict = [dict['images'] for dict in dictList]
    annoDict = [dict['annotation'] for dict in dictList]
    
    fileIDs = []
    outImagesDict = []
    for v in imagesDict:
        for x in v:
            if x['id'] not in fileIDs:
                fileIDs.append(x['id'])
                outImagesDict.append(x)
            else:
                pass
    
    imgSegs = []
    for lst in annoDict:
        imgIds = []
        for x in lst:
            if x['image_id'] in fileIDs:
                imgIds.append(x['image_id'])
                imgSegs.append(x)
        
        fileIDs = [y for y in fileIDs if y not in imgIds]
                
    annoDict = imgSegs
    today = date.today()
    outFileName = "ArcCi-TDS-" + str(today.strftime("%Y-%m-%d")) + '.json'
    catDict = [
        {
            "id": 0,
            "name": "Water",
            "supercategory": "geo"
        },
        {
            "id": 1,
            "name": "Thin Ice",
            "supercategory": "geo"
        },
        {
            "id": 2,
            "name": "Shadow",
            "supercategory": "geo"
        },
        {
            "id": 3,
            "name": "Shadow",
            "supercategory": "geo"
        },
        {
            "id": 4,
            "name": "Ice/Snow",
            "supercategory": "geo"
        },
        {
            "id": 5,
            "name": "Melt Pond",
            "supercategory": "geo"
        }
    ]
            
    masterDict = {'images': outImagesDict,'annotation': annoDict,'categories': catDict}
             
    toJSON(outFileName, masterDict)
    
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('-d', '--dir', type=str, nargs='+')
    args = p.parse_args()
    for dir in args.dir:
        masterDict = [fromJSON(str(dir)+str(file)) for file in os.listdir(dir)]
    mergeData(masterDict)