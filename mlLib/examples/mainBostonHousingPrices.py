#!/usr/bin/env python2
# -*- coding: utf-8 -*-


from project import mlProject, loadPredictProject
import pandas as pd
import numpy as np

from getData import getData
import exploreData as ed
from exploreData import exploreData
from cleanData import cleanData, cleaningRules
from prepData import prepData
from trainModels import trainModels



"""
Created on Wed May 16 13:44:03 2018

@author: scottsmith
"""



project = mlProject('Predict Bostom Home Values', 'Udacity Project1')

project.setTrainingPreferences (crossValidationSplits=4, parallelJobs=-1, modelType='regression', modelList=['lasso', 'ridge', 'enet', 'rf', 'gb', 'decisiontree'] ) 

project.importFile('House Values', type='csv', description='Predict Bostom Housing Prices', fileName='BostonHousingPrices.csv',  hasHeaders = True)


project.setTarget('MEDV')



project.exploreData() 
print project.explore['House Values']
print project.explore['House Values'].allStatsSummary()
   

#project.explore['House Values'].plotExploreHeatMap()


project.runCleaningRules()



project.cleanAndExploreProject()

project.prepProjectByName('House Values')
project.trainProjectByName('House Values')

#project.exportBestModel('BostonPricing.plk')
#project.exportNamedModel('gb','gbRealEstateModel.plk')
#project.exportNamedModel('lasso','lassoRealEstateModel.plk')
#project.exportNamedModel('ridge','ridgeRealEstateModel.plk')
#project.exportNamedModel('enet','enetRealEstateModel.plk')
#project.exportNamedModel('rf','rfRealEstateModel.plk')

project.exportBestModel('bostonHousingBestModel.plk')
print 
print 'the best is ', project.bestModelName
print
print project.bestModel


client_data = pd.DataFrame({'RM': [5, 4, 8],
                           'LSTAT': [17, 32, 3],
                           'PTRATIO': [15, 22,12]},
                           columns=['RM','LSTAT','PTRATIO'])

predict = loadPredictProject('bostonHousingBestModel.plk')
predict.importPredictFromDF(client_data)
predict.prepPredict()


# Produce a matrix for client data
#client_data = [[5, 17, 15], # Client 1
#               [4, 32, 22], # Client 2
#               [8, 3, 12]]  # Client 3

# Show predictions
for i, price in enumerate(predict.runPredict()):
    print("Predicted selling price for Client {}'s home: ${:,.2f}".format(i+1, price))


