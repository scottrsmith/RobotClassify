#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 12:54:33 2018

@author: scottsmith
"""

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
import trainModels as tm




project = mlProject('Find Donors', 'Find Donots')

project.setTrainingPreferences (crossValidationSplits=10, parallelJobs=-1, modelType=tm.TRAIN_CLUSTERING, dropDuplicates=False , clusterDimensionThreshold=20) 

project.importFile('Donors', type='csv', description='Donors model', fileName='census.csv',  hasHeaders = True)
#project.openProject('Predict Home Values2', type='GoogleSheet', description='Real Estate Project 2', location='1QC2v9jPJFTLYxjm-wkIuO1FpYhR-x6ic-utw0CBskU8',  hasHeaders = False, range='A1:Z1884')


project.setTarget('income', boolean=True, trueValue='>50K')

project.exploreData()      

print project.explore['Donors']
print project.explore['Donors'].allStatsSummary()
project.explore['Donors'].plotExploreHeatMap()

#project.explore.plotHistogramsAll(10)
#project.explore['Donors'].plotCategoryColumn('Country')


print project.dataFile['Donors'].dataFrame.shape

#project.runCleaningRules()
#project.addManualRuleForDefault(ed.EXPLORE_REMOVE_ITEMS_EQUAL, 'CustomerID', None)
#project.addManualRuleForDefault(ed.EXPLORE_CONVERT_DATATYPE, 'CustomerID', 'int64')
#project.addManualRuleForDefault(ed.EXPLORE_NEW_VARIABLE, 'Sales', 'Quantity * UnitPrice')


#print project.dataFile.dataFrame.shape



# Create a customer analytical base table
#project.addManualRuleForDefault(ed.EXPLORE_GROUPBY_ROLLUP, ['CustomerID', 'InvoiceNo'], { 'total_transactions' : 'nunique' })
#project.addManualRuleForDefault(ed.EXPLORE_GROUPBY_ROLLUP, ['CustomerID', 'StockCode'], { 'total_products' : 'count', 
#                                                     'total_unique_products' : 'nunique' })
#project.addManualRuleForDefault(ed.EXPLORE_GROUPBY_ROLLUP, ['CustomerID','Sales'], { 'total_sales' : 'sum', 
#                                                  'avg_product_value' : 'mean' })
#
#project.addManualRuleForDefault(ed.EXPLORE_INTERMEDIARY_GROUPBY_ROLLUP, [['CustomerID','InvoiceNo'],'Sales'], { 'cart_value' : 'sum' } )
#
#project.addManualRuleForDefault(ed.EXPLORE_ROLLUP_INTERMEDIARY_GROUPBY_ROLLUP, ['CustomerID','cart_value'], { 'avg_cart_value' : 'mean',
#                                                                                                    'min_cart_value' : 'min',
#                                                                                                    'max_cart_value' : 'max'})



#project.addManualRuleForDefault(ed.EXPLORE_JOIN_ROLLUPS,'customer_df',None)
#
#
#project.addManualRuleForDefault(ed.EXPLORE_PCA_DIMENSIONALITY_REDUTION,['StockCode','CustomerID'], 'pca_item_data')
#
#project.addManualRuleForDefault(ed.EXPLORE_THRESHOLD_DIMENSIONALITY_REDUTION,['StockCode','CustomerID'], 'threshold_item_data')
#
#project.addManualRuleForDefault(ed.EXPLORE_JOIN_TABLES,['customer_df','threshold_item_data'],'threshold_df')
#project.addManualRuleForDefault(ed.EXPLORE_JOIN_TABLES,['customer_df','pca_item_data'],'pca_df')
#
#project.addManualRuleForDefault(ed.EXPLORE_SET_BATCH_TABLES,['customer_df', 'threshold_df', 'pca_df'], None)
#
#
#
#
#project.cleanAndExploreProject()
#


#
#
#

#
#

#project.prepProjectByBatch()
#project.trainProjectByBatch()



#project.prepProjectByName('customer_df')
#project.trainProjectByName('customer_df')
#
#project.exportBestModel('customer_df.plk', tableName='customer_df')
#project.exportBestModel('threshold_df.plk', tableName='threshold_df')
#project.exportBestModel('pca_df.plk', tableName='pca_df')
#project.exportFile('customer_df', 'customer_df_preped.csv')
#
#
#
#
#print 
#print 'The best is ', project.bestModelName
#print
#print project.bestModel
#
#
# Pick the winner
#predict = loadPredictProject('customer_df.plk',)
#predict.importPredictFileFromProject(project,'customer_df')
#predict.prepPredict()
#ans = predict.runPredict()
#predict.addToPredictFile('cluster',ans)
#predict.exportPredictFile('customer_df_clustered.csv')
#print ans
#
#predict = loadPredictProject('threshold_df.plk',)
#predict.importPredictFileFromProject(project,'threshold_df')
#predict.prepPredict()
#ans = predict.runPredict()
#predict.addToPredictFile('cluster',ans)
#predict.exportPredictFile('threshold_df_clustered.csv')
#print ans
#

#predict = loadPredictProject('pca_df.plk',)
#predict.importPredictFileFromProject(project,'pca_df')
#predict.prepPredict()
#ans = predict.runPredict()
#predict.addToPredictFile('cluster',ans)
#predict.exportPredictFile('pca_df_clustered.csv')
#print ans
#
#
