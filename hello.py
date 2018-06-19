# -*- coding: utf-8 -*-


from flask import Flask, render_template, request, redirect, url_for
import os
import configparser
from Searcher import Searcher

app = Flask(__name__)
port = int(os.getenv('PORT', 5050))

places = []
bedroom = []

PropertyURL_list = [] 
ImageURL_list = []
Area_list = [] 
Price_list = [] 
BHK_list = []
configParser = configparser.ConfigParser(allow_no_value = True)
keys = []
configFilePath = 'config.ini'
configParser.read(configFilePath)
if(len(configParser.read(configFilePath)) > 0):
    details = configParser.sections()[0]
    for key in configParser[details]:
        keys.append(key)
    places += configParser[details][keys[0]].split(',')
    bedroom += configParser[details][keys[1]].split(',')

@app.route('/')
def home():
    global places, bedroom
    return render_template('home.html', locality = places, bhk = bedroom)

@app.route('/results', methods = ['GET','POST'])
def results():
    BHK = request.form.get('bhk')
    bathroom = request.form['bathrooms']
    area = request.form['floor_area']
    Locality = request.form.get('locality')
    FurnishingStatus = request.form.get('furnishing_status')
    TypeofSale = request.form.get('type_of_sale')
    searcher = Searcher()
    searcher.putBathrooms(bathroom)
    searcher.putBHK(BHK)
    searcher.putFloorArea(area)
    searcher.putFurnishingStatus(FurnishingStatus)
    searcher.putLocality(Locality)
    searcher.putTypeofSale(TypeofSale)
    #print(FurnishingStatus)
    #print(Locality)
    #print(TypeofSale)
    #TypeofSale = TypeofSale.split(" ")[0]
    price = searcher.searchProperties(BHK, area, bathroom, Locality, FurnishingStatus, TypeofSale)
    global PropertyURL_list, ImageURL_list, Area_list, Price_list, BHK_list
    PropertyURL_list, ImageURL_list, Area_list, BHK_list = searcher.viewProperties(BHK, Locality, FurnishingStatus, TypeofSale)
    #print(PropertyURL_list[0:3])
    #print(ImageURL_list[0:3])
    #print(Area_list[0:3])
    #print(Price_list[0:3])
    #print(BHK_list[0:3])
    #print(zip(PropertyURL_list[0:3], ImageURL_list[0:3], Area_list[0:3], BHK_list[0:3], Price_list[0:3]))
    return render_template('results.html', locality = Locality, type_of_sale = TypeofSale, bhk = BHK, bathrooms = bathroom, 
                           furnishing_status = FurnishingStatus, floor_area = area, prediction = price,
                           PropertyURL_ImageURL_Area_BHK_Price = zip(PropertyURL_list[0:3], ImageURL_list[0:3], BHK_list[0:3], Area_list[0:3]))
@app.route('/more')
def more():
    global PropertyURL_list, ImageURL_list, Area_list, Price_list, BHK_list
    return render_template('more.html', PropertyURL_ImageURL_Area_BHK_Price = zip(PropertyURL_list, ImageURL_list, BHK_list, Area_list))
"""
def getDetails():
    BHK = request.form.get('bhk')
    bathroom = request.form['bathrooms']
    area = request.form['floor_area']
    Locality = request.form.get('locality')
    FurnishingStatus = request.form.get('furnishing_status')
    TypeofSale = request.form.get('type_of_sale')
    results(BHK, bathroom, area, Locality, FurnishingStatus, TypeofSale)
"""
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)