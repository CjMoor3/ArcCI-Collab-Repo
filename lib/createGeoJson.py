#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import geojson
from geojson import Feature, Point, FeatureCollection
import base64
import codecs


# In[2]:


class geoJsonConverter:
    def __init__(self):
        #self.encodingImage = None
        #self.rasterList = None
        self.imageData = {}
        self.newFileNameIndex = 1 # name index for creating new text files - populated in imgToJson()
        #!TODO: Create boiler plate geojson object
        self.trainingData = None
    
    # def setEncodingImage(self): #!TODO: Pass raster metadata for a single config method creating GeoJSON objs
    # The encoding image is passed to the class after it is initiated
        #self.encodingImage = encodingImage
        #self.rasterList = rasterList
        
    #def configFeatureCollection(self):
        #self.encodin

    #takes h5py training data format from gui and moves it to GeoJSON object
    def plugTrainingData(self, featureMatrix, labelVector, segmentList, newFileName):
        
        #Append the trainingData members to the GeoJSON Object
        features = []
        features.append(Feature(properties={"featureMatrix": featureMatrix}))
        features.append(Feature(properties={"labelVector": labelVector}))
        features.append(Feature(properties={"segmentList": segmentList}))

        #Consolidate features into feature collection for writing to a GeoJSON object
        featureCollection = FeatureCollection(features)

        #Create GeoJSON file
        with open(newFileName, 'w') as newGeoJSONobject:
            geojson.dump(featureCollection, newGeoJSONobject)

            newGeoJSONobject.close()
    
    
    #This method searializes our numpy arrays into JSON objects
    def imgToJson(self , encodingImage):
        encodeList = encodingImage.tolist()
        #print(encodeList)
        JSONobj = json.dumps(encodeList)

        # This loop ensures that we create a new GeoJSON object each time we press the button

####DYLAN LOOK HERE-cjm *&^%&*^$^%$^%$(&^%)&*)%_)*&%^)(&*^%(*&%)*&$%&^$&^%&*%*(&%&*^
                #\/ 00

        #fix plz
        # CAUTION: PLEASE BACKUP SAVED OBJECTS AFTER EACH SESSION - THE FILE INDEX WILL RESET,
        # AND FILES CAN BE OVERWRITTEN FROM THIS CODE - (working on a more user-friendly solution)
        while True: # infinite loop
            indexToCat = str(self.newFileNameIndex) # Convert our current file index to string to allow concatenation
            newFileName = 'S:\\OSSP-master\\CJ\\GeoJSONobjects\\GeoJSONobject' + indexToCat + '.txt' # concatenate target directory with file index
            self.newFileNameIndex += 1 #increment the file index to allow us to create a new file in each iteration
            continue # break infinite loop

        newGeoJSONobject = open(newFileName, 'w')
        newGeoJSONobject.write(JSONobj) #write new JSON obj

        # 2 functs -> 1) read/write (creating fresh objects) 2) conversion form numpy->JSON->GeoJSON
        
        
        #file_path = "/path.json" ## your path variable
        #returnObj = json.dump(encodeList, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4) 
        #print(JSONobj)   
        
#!TODO: CONSOLIDATE

    







