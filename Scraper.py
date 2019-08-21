# -*- coding: utf-8 -*-

import re
import requests
import warnings
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import pandas as pd
import configparser
import numpy as np
import time
from Property import Property

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
            URL = "https://www.magicbricks.com/property-for-sale/residential-real-estate"
            for area in self.places:
                for bed in self.bedroom:
                    for pageno in range(1,51):
                        parameters = dict(bedroom = bed, proptype = 'Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment', cityName = area, page = pageno)
                        page = requests.get(url = URL, params = parameters)
                        with open('scrapinglog.txt','a') as log_file:
                            log = str(page.status_code)+','+area+','+str(bed)+','+str(pageno)+','+str(datetime.now())+'\n'
                            log_file.write(log)
                            #if page.status_code == 404:
                            #    continue
                            #print(page.status_code)
                        soup = BeautifulSoup(page.text, 'lxml')	# parse the html using BeautifulSoup and store in variable `soup`
                        propertyID_box = [ID['data-objid'] for ID in soup.find_all('span', attrs={'class':'domcache js-domcache-srpgtm'})]	# Take out all <span> of property IDs and get its value    
                        for ID in propertyID_box:
                            if ID not in dataset['PropertyID']:
                                properties.PropertyID = int(ID)
                                #propertyid_box.append(ID)
                                properties.Area = area
                                #area_box.append(area)
                                url = soup.find('div', attrs={'id':'resultBlockWrapper'+ID})['onclick'].split(',')[1].strip()
                                url = re.sub(r"[']",'',url)
                                properties.PropertyURL = url
                                #url_box.append(url)
                                price = soup.find_all('span', attrs={'id': 'domcache_srp_'+ID})[1]['data-price']
                                try:
                                    properties.Price = int(price)
                                    #price_box.append(int(price))	
                                except ValueError:
                                    #print('Price Issue:'+url)
                                    properties.Price = np.nan
                                    #price_box.append(np.nan)
                                location = soup.find_all('span', attrs={'id': 'domcache_srp_'+ID})[0]['data-objlmtdname']
                                properties.Locality = location
                                #location_box.append(location)
                                typeofsale = soup.find_all('span', attrs={'id': 'domcache_srp_'+ID})[1]['data-transactiontype']
                                properties.TypeofSale = typeofsale.split(' ')[0]
                                #typeofsale_box.append(typeofsale.split(' ')[0])
                                propertytype = soup.find_all('span', attrs={'id': 'domcache_srp_'+ID})[0]['data-objproptypeid']
                                properties.PropertyType = propertytype
                                #propertytype_box.append(propertytype)
                                furnishing = soup.find_all('span', attrs={'id': 'domcache_srp_'+ID})[1]['data-furnshingstatus']
                                properties.FurnishingStatus = furnishing
                                #furnishing_box.append(furnishing)
                                society = soup.find('input', attrs={'id': 'projectSocietyName'+ID})['value']
                                properties.Society = society
                                #society_box.append(society)
                                floor = soup.find_all('span', attrs={'id': 'domcache_srp_'+ID})[1]['data-floorno']
                                try:
                                    properties.FloorNo = int(floor)
                                    #floor_box.append(int(floor))
                                except ValueError:
                                    #print('Floor Issue:'+url)
                                    properties.FloorNo = 0
                                    #floor_box.append(0)
                                bedrooms = soup.find_all('span', attrs={'id': 'domcache_srp_'+ID})[1]['data-bedroom']
                                properties.BHK = int(bedrooms)
                                #bedroom_box.append(int(bedrooms))
                                bathrooms = soup.find_all('span', attrs={'id': 'domcache_srp_'+ID})[1]['data-bathroom']
                                try:
                                    properties.Bathrooms = bathrooms
                                    #bathroom_box.append(int(bathrooms))  
                                except ValueError:
                                    properties.Bathrooms = round(int(bedrooms)/2)
                                    #bathroom_box.append(round(int(bedrooms)/2)) #assumption- per 2 rooms 1 bathroom is present                        
                                    #print('Bathroom Issue:'+url)
                                proppage = requests.get(url)
                                pagesoup = BeautifulSoup(proppage.text, 'lxml')  
                                imgurl = pagesoup.find('img', attrs={'id': 'bigImageId'})['data-src']
                                properties.ImageURL = imgurl
                                #imgurl_box.append(imgurl)
                                try:
                                    carpetarea = pagesoup.find('div', attrs={'id': 'carpetArea'}).text
                                    carpetarea = re.sub(r"[,]",'',carpetarea)
                                    properties.CarpetArea = int(carpetarea)
                                    #carpetarea_box.append(int(carpetarea))                  
                                    try:
                                        superarea = pagesoup.find('div', attrs={'id': 'coveredArea'}).text
                                        superarea = re.sub(r"[,]",'',superarea)
                                        properties.CoveredArea = int(superarea)
                                        #superarea_box.append(int(superarea))
                                    except AttributeError:
                                        #print('Super Area Issue:'+url)
                                        properties.CoveredArea = properties.CarpetArea
                                        #superarea_box.append(int(carpetarea))
                                except  AttributeError:
                                    try:
                                        superarea = pagesoup.find('div', attrs={'id': 'coveredArea'}).text
                                        superarea = re.sub(r"[,]",'',superarea)
                                        properties.CarpetArea = int(superarea)
                                        properties.CoveredArea = int(superarea)
                                        #print('carpet Area Issue:'+url)
                                        #carpetarea_box.append(int(superarea))
                                    except AttributeError:
                                        continue
                                try:
                                    properties.Price_per_sqft_carpetarea = round(properties.Price / properties.CarpetArea)
                                except ValueError:
                                    properties.Price_per_sqft_carpetarea = np.nan
                                try:
                                    properties.Price_per_sqft_coveredarea = round(properties.Price / properties.CoveredArea)
                                except ValueError:
                                    properties.Price_per_sqft_coveredarea = np.nan
                                properties.City = 'Kolkata'
                                dataset = dataset.append(pd.Series([properties.PropertyID, properties.PropertyType, 
                                                                    properties.BHK, properties.CarpetArea, properties.CoveredArea, 
                                                                    properties.Bathrooms, properties.FloorNo, properties.TypeofSale, 
                                                                    properties.FurnishingStatus, properties.Society, properties.Locality, 
                                                                    properties.Area, properties.City, properties.Price, 
                                                                    properties.Price_per_sqft_coveredarea, properties.Price_per_sqft_carpetarea, 
                                                                    properties.PropertyURL,  properties.ImageURL], 
                                                                    index = dataset.columns),ignore_index = True)
                        time.sleep(1)
        log_file.close()
        return dataset

    def processData(self,dataset):
        dataset = dataset.drop_duplicates(subset = ['PropertyID'])
        #dataset = dataset.dropna(axis = 0)
        dataset = dataset.reset_index(drop = True)
        return dataset
    
    def loadData(self):
        try:
            dataset = pd.read_csv(r"house_data.csv", encoding = "latin1")
            self.lastSamplePoint = len(dataset) - 1
        except FileNotFoundError:
            print("Dataset does not exist. Creating dataset....")
            dataset = pd.DataFrame(columns = ['PropertyID','PropertyType','BHK','CarpetArea','SuperArea','Bathrooms','Floor_No','Type_of_Sale','Furnishing_Status','Society','Locality','Area','City','Price','Price_per_sqft_Superarea','Price_per_sqft_Carpetarea','Property_URL','Image_URL'])
            with open('house_data.csv', 'a', encoding = 'utf-8', newline = '') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(("PropertyID", "Property Type", "BHK", "CarpetArea", "SuperArea", "Bathrooms", "Floor_No", "Type_of_Sale", "Furnishing_Status", "Society", "Locality", "Area", "City", "Price", "Price_per_sqft_Superarea", "Price_per_sqft_Carpetarea", "Property_URL", "Image_URL"))
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