# -*- coding: utf-8 -*-


import configparser
from Predictor import Predictor
from Scraper import Scraper

class Searcher:
    
    def __init__(self):
        self.__BHK = 0
        self.__FloorArea = 0
        self.__Bathrooms = 0
        self.__Locality = ""
        self.__FurnishingStatus = ""
        self.__TypeofSale = ""
        
    def putBHK(self, BHK):
        self.__BHK = BHK
        
    def putFloorArea(self, FloorArea):
        self.__FloorArea = FloorArea
        
    def putBathrooms(self, Bathrooms):
        self.__Bathrooms = Bathrooms
        
    def putLocality(self, Locality):
        self.__Locality = Locality
        
    def putFurnishingStatus(self, FurnishingStatus):
        self.__FurnishingStatus = FurnishingStatus
        
    def putTypeofSale(self, TypeofSale):
        self.__TypeofSale = TypeofSale
        
    def searchProperties(self, BHK, FloorArea, Bathrooms, Locality, FurnishingStatus, TypeofSale):
        configParser = configparser.ConfigParser(allow_no_value = True)
        keys = []
        places = []
        configFilePath = 'config.ini'
        configParser.read(configFilePath)
        if(len(configParser.read(configFilePath)) > 0):
            details = configParser.sections()[0]
            for key in configParser[details]:
                keys.append(key)
            places += configParser[details][keys[0]].split(',')
        places_key=[]
        for place in places:
            places_key +=['Locality_'+place]
        inp={}
        inp = {'BHKs':[BHK],'FloorArea':[FloorArea],'Bathrooms':[Bathrooms]}
        for place in places_key:
            inp[place]= [0]
        inp.update({'Type_of_Sale_New':[0],'Type_of_Sale_Resale':[0],'Furnishing_Status_Furnished':[0],
                    'Furnishing_Status_Semi-Furnished':[0],'Furnishing_Status_Unfurnished':[0]})
        inp['Locality_'+Locality] = [1] 
        inp['Furnishing_Status_'+FurnishingStatus] = [1]
        inp['Type_of_Sale_'+TypeofSale] = [1] 
        #print(inp)
        predictor = Predictor()
        #print(type(predictor.regressor))
        #print(predictor.price)
        #return 0
        price = predictor.getPredictedPrice(inp)
        if price:
            return price
        else:
            predictor.managePredictor()
            return predictor.getPredictedPrice(inp)
            
    
    def viewProperties(self, BHK, Locality, FurnishingStatus, TypeofSale):
        scraper = Scraper()
        PropertyURL_list, ImageURL_list, Area_list, BHK_list = scraper.returnPropertyURLS(BHK, Locality, FurnishingStatus, TypeofSale)
        return PropertyURL_list, ImageURL_list, Area_list, BHK_list
    
"""   
if __name__=='__main__':
    searcher = Searcher()"""