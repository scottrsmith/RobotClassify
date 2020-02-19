#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 16 13:44:03 2018

@author: scottsmith
"""

from project import mlProject
import pandas as pd
import numpy as np
from getData import getData
import exploreData as ed
from exploreData import exploreData
from cleanData import cleanData, cleaningRules
from prepData import prepData
from trainModels import trainModels

# Create the project and set the training preferences
project = mlProject('Predict Home Values', 'EDS Real Estate Project 2')
project.setTrainingPreferences(crossValidationSplits=10,
                               parallelJobs=-1,
                               modelType='regression',
                               modelList=['lasso', 'ridge', 'enet', 'rf', 'gb'])

# Import the file and set the training target to predict
project.importFile('Property Data',
                   type='GoogleSheet',
                   description='Real Estate Project 2',
                   location='1QC2v9jPJFTLYxjm-wkIuO1FpYhR-x6ic-utw0CBskU8',
                   hasHeaders=False, range='A1:Z1884')
project.setTarget('tx_price')

# Explore the data and print out the heatmap that
# will illustrate the recommended feature engineering
# plot other statistical data
project.exploreData()
project.explore['Property Data'].plotExploreHeatMap()
project.explore[TRAININGFILENAME].plotFeatureImportance()
project.explore[TRAININGFILENAME].plotColumnImportance()
project.explore[TRAININGFILENAME].plotHistogramsAll(10)
project.explore[TRAININGFILENAME].plotCorrelations()

# Init the setup of the cleaning rules
project.runCleaningRules()


# Add manual cleaning Rules. These rules perform the feature engineering
project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'roof', [
                                ['asphalt,shake-shingle','shake-shingle'],
                                 'Shake Shingle'])
project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'exterior_walls', [
                                ['Rock, Stone'], 'Masonry'])
project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'exterior_walls', [
                                ['Concrete', 'Block'], 'Concrete Block'])
project.addManualRuleForDefault(
    ed.EXPLORE_REMOVE_ITEMS_ABOVE, 'lot_size', 1220551)

# values are sparse classes and prompt to combine
project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'exterior_walls', [
                                ['Wood Siding', 'Wood Shingle'], 'Wood'])
project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'exterior_walls', [
                                ['Concrete Block', 'Stucco', 'Masonry',
                                 'Asbestos shingle'], 'Other'])
project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'roof', [
                                ['Composition', 'Wood Shake/ Shingles'],
                                 'Composition Shingle'])
project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'roof', [
                                ['Gravel/Rock', 'Roll Composition', 'Slate',
                                'Built-up', 'Asbestos', 'Metal'], 'Other'])

# indicator variables
# Create indicator variable for properties with 2 beds and 2 baths
project.addManualRuleForDefault(ed.EXPLORE_NEW_INDICATOR_VARIABLE,
                                'two_and_two',
                                '( beds == 2 ) & ( baths == 2 )')

# Create indicator feature for transactions between 2010 and 2013, - resession
project.addManualRuleForDefault(ed.EXPLORE_NEW_INDICATOR_VARIABLE,
                                'during_recession',
                                '( tx_year >= 2010 ) & ( tx_year <= 2013 )')

# Create a school score feature that num_schools * median_school
project.addManualRuleForDefault(ed.EXPLORE_NEW_VARIABLE,
                               'school_score',
                               'num_schools * median_school')

# Create a property age feature
project.addManualRuleForDefault(ed.EXPLORE_NEW_VARIABLE,
                                'property_age', 'tx_year - year_built')
project.addManualRuleForDefault(ed.EXPLORE_REMOVE_ITEMS_BELOW,
                                'property_age', -1)

# Drop 'tx_year' and 'year_built' from the dataset
project.addManualRuleForDefault(ed.EXPLORE_DROP_COLUMN, 'tx_year', None)
project.addManualRuleForDefault(ed.EXPLORE_DROP_COLUMN, 'year_built', None)

# Now run these rules to reformat the data
project.cleanAndExploreProject()

# Prep the data for training
project.prepProjectByName('Property Data')

# Train the model
project.trainProjectByName('Property Data')

# Save the best model and one named model
project.exportBestModel('realEstateBestModel.plk')
project.exportNamedModel('gb', 'gbRealEstateModel.plk')

# Now run the predections
predict = project.createPredictFromBestModel('Property Data')
predict.importPredictFromDF(project.PullTrainingData(),
                            readyForPredict=True)
keyName, keyData = project.getKey()

# Prep the predict file
predict.prepPredict()
answer = predict.runPredict()

# Prepare the predict file for Kaggle upload
# This means taking the predicted answer and adding
# to the file for later export
predict.addToPredictFile(keyName, keyData)
if useProba:
    pass
else:
    answer = [int(x) for x in answer]
predict.addToPredictFile(targetVariable, answer)

# Prep the file for export, onlu keeping
# columns needed
predict.keepFromPredictFile(predictSetOut)
predict.exportPredictFile(resultsFile)
