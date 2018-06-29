# -*- coding: utf-8 -*-

import pandas as pd
import warnings
from sklearn.model_selection import train_test_split
#from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import pickle

class Predictor:
    
    def __init__(self):
        warnings.filterwarnings("ignore")

    def loadData(self):
        try:
            dataset = pd.read_csv(r"house_data.csv", encoding = "latin1")
            dataset = dataset.drop_duplicates(subset = ['PropertyID'])
            dataset = dataset.dropna(axis = 0)
            return dataset
        except FileNotFoundError:
            print("Dataset Not Found. Please Re-run scraper")
            return 0
        
    def splitData(self, dataset):
        X_df = dataset.iloc[:, 1:7]
        Y_df = dataset.iloc[:, 7:8]
        X_df = pd.get_dummies(X_df,columns=['Locality','Type_of_Sale','Furnishing_Status'])
        X = X_df.values
        Y = Y_df.values
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 0)
        return X_train, Y_train, X_test, Y_test
    
    def trainData(self, X_train, Y_train, X_test, Y_test):
        
        regressor = RandomForestRegressor(n_estimators = 20, random_state = 0, max_features = 'sqrt',
                                  min_samples_leaf =  1, min_samples_split = 4, bootstrap = True, 
                                  warm_start = True, oob_score = True)
        
        """
        regressor = DecisionTreeRegressor(min_samples_split = 4, random_state = 0, max_features = 'sqrt',
                                  presort = True, splitter = 'random', min_samples_leaf = 1)
        """
        regressor.fit(X_train, Y_train)
        #y_pred = self.regressor.predict(X_test)
        print('R^2 Score: %.2f' % regressor.score(X_test, Y_test))
        #filename = 'regressor_model.pkl'
        pickle.dump(regressor, open('regressor_model.pkl', 'wb'))
        del regressor
        return 1
    
    def getPredictedPrice(self, inp):
        inp_df = pd.DataFrame(data = inp)
        input_data = inp_df.values
        price = 0
        try:
            regressor = pickle.load(open('regressor_model.pkl', 'rb'))
            price = regressor.predict(input_data)
        except FileNotFoundError:
            return 0
        #price = regressor.predict(input_data)
        #print(type(price))
        #print(type(price[0]))
        if(price[0]%10 < 5):
           low=price[0]-(price[0]%10)
           high=low+10
           ans=str(low)+' - '+str(high)
           #print(ans)
           #print(type(ans))
        elif(price[0]%10 > 5):
            low=price[0]-((price[0]%10)-5)
            high=low+10
            ans=str(low)+' - '+str(high)
            #print(ans)
            #print(type(ans))
        elif(price[0]%10==5):
            low=price[0]
            high=low+10
            ans=str(low)+' - '+str(high)
            #print(ans)
            #print(type(ans))
        return ans
    
    def managePredictor(self):
        dataset = self.loadData()
        X_train, Y_train, X_test, Y_test = self.splitData(dataset)
        if(self.trainData(X_train, Y_train, X_test, Y_test)):
            print("Model successfully fitted and trained.")
        else:
            print("Training Unsuccessful. Please re-run predictor.")
    
if __name__=='__main__':
    predictor = Predictor()
    predictor.managePredictor()
    """
    #sample input format
    inp = {'BHKs':[2],'FloorArea':[720],'Bathrooms':[1],'Locality_Ballygunge':[0],
           'Locality_Chetla':[0],'Locality_Dhakuria':[1],'Locality_Gariahat':[0],
           'Locality_Jadavpur':[0],'Locality_New Town':[0],'Locality_Rajarhat':[0],
           'Type of Sale_New':[1],'Type of Sale_Resale':[0],'Furnishing Status_Furnished':[0],
           'Furnishing Status_Semi-Furnished':[0],'Furnishing Status_Unfurnished':[1]}
    price = predictor.getPredictedPrice(inp)
    #prediction = price[0].astype(str)
    #print(type(prediction[0].astype(str)))
    print("Predicted Price (in Lacs):" + price)
    """