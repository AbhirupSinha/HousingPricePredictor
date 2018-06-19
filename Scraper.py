# -*- coding: utf-8 -*-

import urllib3
import certifi
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import pandas as pd
import configparser
import numpy as np
from Property import Property
#import time

#start_time = time.time()
class Scraper:
    
    def __init__(self):
        self.lastSamplePoint = 0
        self.places = []
        self.bedroom = []

    def getConfig(self):
        configParser = configparser.ConfigParser(allow_no_value = True)
        keys = []
        configFilePath = 'config.ini'
        configParser.read(configFilePath)
        if(len(configParser.read(configFilePath)) > 0):
            details = configParser.sections()[0]
            for key in configParser[details]:
                keys.append(key)
            self.places += configParser[details][keys[0]].split(',')
            self.bedroom += configParser[details][keys[1]].split(',')
            return 1
        else:
            print("Configuration File not found!!")
            return 0

    def scrapeData(self,properties,dataset):
        if(self.getConfig()):
            http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
            for i in self.places:
                for j in self.bedroom:
                    URL = 'https://www.magicbricks.com/property-for-sale/residential-real-estate?bedroom='+j+'&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment&Locality='+i+'&cityName=Kolkata'
                    page = http.request('GET', URL)
                    soup = BeautifulSoup(page.data, 'lxml')																				# parse the html using BeautifulSoup and store in variable `soup`    
                    price_box = soup.find_all('span', attrs={'class': 'm-srp-card__price'})												# Take out all <span> of prices and get its values        
                    BHK_box = soup.find_all('span', attrs={'class': 'm-srp-card__title__bhk'})											# Take out all <span> of BHK details and get its values        
                    floorSize_box = [floor['content'] for floor in soup.find_all('meta',attrs={'itemprop':'floorSize'})]	 			# Take out all <meta> of property floorarea and get its values       
                    propertyID_box = [ID['data-objid'] for ID in soup.find_all('span', attrs={'class':'domcache js-domcache-srpgtm'})]	# Take out all <span> of property IDs and get its values        
                    location_box = [location['content'] for location in soup.find_all('meta', attrs={'itemprop':'addressLocality'})]	# Take out all <meta> of property locations and get its values
                    URL_box = [link['href'] for link in soup.find_all('a', attrs={'class': 'm-srp-card__title'})]           			# Take out all <a> tags and get property URLs
                    image_box = [link['data-src'] for link in soup.find_all('img', attrs={'class':'m-photo__img lazy'})]
                    posted_box = soup.find_all('span', attrs={'itemprop':'dateCreated'})
                    try:
                        for k in range(0,len(propertyID_box)):
                            properties.PropertyID = propertyID_box[k]
                            properties.BHK = BHK_box[0].text.split('BHK')[0].strip()
                            if("Call" in price_box[k].text.strip()):
                                properties.Price = np.nan
                            else:
                                properties.Price = price_box[k].text.split(" ")[0].strip()
                                if(price_box[k].text.split(" ")[1].strip()=="Cr"):
                                    properties.Price = float(properties.Price) * 100
                            location = location_box[k]
                            if(len(location.split(","))>=2):
                                properties.Locality = location.split(",")[1].strip()
                            else:
                                properties.Locality = location.strip()
                            if properties.Locality not in self.places:
                                properties.Locality = np.nan
                            properties.Bathrooms = soup.find('input', attrs={'id':'bathroom'+propertyID_box[k]})['value']
                            properties.TypeofSale = soup.find('input', attrs={'id':'transactionType'+propertyID_box[k]})['value'].strip().split(" ")[0]
                            properties.FurnishingStatus = soup.find('input', attrs={'id':'furnshingStatus'+propertyID_box[k]})['value'].strip()
                            properties.FloorArea = floorSize_box[k].split("FTK")[0].strip()
                            properties.PropertyURL = URL_box[k]
                            properties.PostedOn = posted_box[k].text.strip()
                            properties.ImageURL = image_box[k]
                            if int(properties.PropertyID) not in dataset.PropertyID.values:
                                dataset = dataset.append(pd.DataFrame(data = {'PropertyID':[properties.PropertyID], 'BHKs':[properties.BHK], 'FloorArea':[properties.FloorArea], 
                                      'Bathrooms':[properties.Bathrooms], 'Type_of_Sale':[properties.TypeofSale], 'Furnishing_Status':[properties.FurnishingStatus], 'Locality':[properties.Locality], 
                                      'Price_in_Lacs':[properties.Price], 'Property_URL':[properties.PropertyURL], 'Image_URL':[properties.ImageURL], 'Posted_On':[properties.PostedOn],
                                      'Last_Modified_On':[datetime.now()]}, columns = ['PropertyID','BHKs','FloorArea','Bathrooms','Type_of_Sale','Furnishing_Status','Locality','Price_in_Lacs','Property_URL',
                                      'Image_URL','Posted_On','Last_Modified_On']), ignore_index = True)
                            else:
                                pass
                    except IndexError:
                        pass
                    
            return dataset

    def processData(self,dataset):
        dataset = dataset.drop_duplicates(subset = ['PropertyID'])
        dataset = dataset.dropna(axis = 0)
        dataset = dataset.reset_index(drop = True)
        return dataset
    
    def loadData(self):
        try:
            dataset = pd.read_csv(r"house_data.csv", encoding = "latin1")
            self.lastSamplePoint = len(dataset) - 1
        except FileNotFoundError:
            print("Dataset does not exist. Creating dataset....")
            dataset = pd.DataFrame(columns = ['PropertyID','BHKs','FloorArea','Bathrooms','Type_of_Sale','Furnishing_Status','Locality','Price_in_Lacs','Property_URL','Image_URL','Posted_On','Last_Modified_On'])
            with open('house_data.csv', 'a', encoding = 'utf-8', newline = '') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(("PropertyID", "BHKs", "FloorArea", "Bathrooms", "Type_of_Sale", "Furnishing_Status", "Locality", "Price_in_Lacs", "Property_URL", "Image_URL","Posted_On", "Last_Modified_On"))
        return dataset
    
    def writeData(self,dataset):
        df = dataset.iloc[self.lastSamplePoint:len(dataset),:]
        try:
            with open('house_data.csv', 'a', encoding = 'utf-8', newline = '') as csv_file:
                df.to_csv(csv_file, header=False, index = False)
            return 1
        except:
            return 0
        
    def returnPropertyURLS(self, BHK, locality, FurnishingStatus, TypeofSale):
        #import pandas as pd
        dataset = pd.read_csv(r"house_data.csv", encoding = "latin1")
        #print(dataset)
        PropertyURL_list = []
        ImageURL_list = []
        Area_list = []
        #Price_list = []
        BHK_list = []
        #print(type(BHK))
        #print(type(locality))
        for i in range(0, len(dataset)):
            if((str(dataset.BHKs[i]) == BHK) and (dataset.Type_of_Sale[i] == TypeofSale) and 
               (dataset.Furnishing_Status[i] == FurnishingStatus) and (dataset.Locality[i] == locality)):
                PropertyURL_list.append(dataset.Property_URL[i])
                #print(dataset.Property_URL[i])
                #print(PropertyURL_list)
                ImageURL_list.append(dataset.Image_URL[i])  
                Area_list.append(dataset.FloorArea[i])
                #Price_list.append(dataset.Price_in_Lacs[i])
                BHK_list.append(dataset.BHKs[i])
        #print(len(PropertyURL_list))
        #print(len(ImageURL_list))
        #print(len(Area_list))
        #print(len(Price_list))
        #print(len(BHK_list))
                
        return PropertyURL_list, ImageURL_list, Area_list, BHK_list
    
if __name__=='__main__':
    scraper = Scraper()
    properties = Property()
    dataset = scraper.loadData()
    dataset = scraper.scrapeData(properties,dataset)
    dataset = scraper.processData(dataset)
    if(scraper.writeData(dataset)):
        print("Dataset Successfully Updated")
    else:
        print("Dataset updation failed. Please re-run scraper")
"""    
if(get_places()):
    dataset = load_data()
    dataset = process_data(dataset)
    if(write_data(dataset)):
        print("Dataset Successfully Updated")
    else:
        print("Dataset updation failed. Please re-run scraper")
        
#print("Total Execution Time in seconds: %.3f" % (time.time() - start_time))
"""