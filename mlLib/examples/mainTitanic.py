#!/usr/bin/env python2
# -*- coding: utf-8 -*-


from project import mlProject
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


'''



enet
--------
('R^2:', 0.4052451373117357)
('MAE:', 86298.63725312549)
('enet', 0.3428746286638919)

lasso
--------
('R^2:', 0.40888624716724375)
('MAE:', 85035.54246538795)
('lasso', 0.3086275085937654)

ridge
--------
('R^2:', 0.4093396476329719)
('MAE:', 84978.03564808935)
('ridge', 0.3166111585985651)

gb
--------
('R^2:', 0.5410951822821564)
('MAE:', 70601.60664940192)
('gb', 0.4869720585739858)

rf
--------
('R^2:', 0.5722509742910005)
('MAE:', 67962.75780160858)
('rf', 0.4815967347888209)
'''

project = mlProject('Titanic Survival', 'Udacity')

project.setTrainingPreferences (crossValidationSplits=10, parallelJobs=-1, modelType='regression', modelList=['lasso', 'ridge', 'enet', 'rf', 'gb'] ) 

#project.openProject('Predict Home Values2', type='csv', description='Real Estate Project 2', fileName='original_real_estate_data.csv',  hasHeaders = True)
project.importFile('Survival Data', type='csv', description='Survival Data', fileName='titanic_data.csv',  hasHeaders = True,)


project.setTarget('Survived')



project.exploreData() 
   


print project.explore['Survival Data']
print project.explore['Survival Data'].allStatsSummary()
project.explore['Survival Data'].plotExploreHeatMap()

project.explore['Survival Data'].plotHistogramsAll(10)

project.explore['Survival Data'].plotCorrelations()


#project.runCleaningRules()


# Add manual Rules

#project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'roof', [['asphalt,shake-shingle','shake-shingle'], 'Shake Shingle'])
#project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'exterior_walls', [ ['Rock, Stone'], 'Masonry'])
#project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'exterior_walls', [ ['Concrete','Block'], 'Concrete Block'])
#project.addManualRuleForDefault(ed.EXPLORE_REMOVE_ITEMS_ABOVE, 'lot_size', 1220551)

# Status





#********************************************************
#
#  
#  values are sparse classes and prompt to combine
#
#********************************************************
#project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'exterior_walls', [['Wood Siding','Wood Shingle'], 'Wood'])
#project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'exterior_walls', [['Concrete Block', 'Stucco', 'Masonry', 'Asbestos shingle'], 'Other'])
#project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'roof', [['Composition', 'Wood Shake/ Shingles'], 'Composition Shingle'])
#project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'roof', [['Gravel/Rock', 'Roll Composition', 'Slate', 'Built-up', 'Asbestos', 'Metal'], 'Other'])

#********************************************************
## Feature Engineer - needs to be user driven
#********************************************************
    

#
#  indicator variable 
#    

# Create indicator variable for properties with 2 beds and 2 baths
#df['two_and_two'] = ((df['beds']==2) & (df['baths']==2)).astype(int)
#project.addManualRuleForDefault(ed.EXPLORE_NEW_INDICATOR_VARIABLE, 'two_and_two', '( beds == 2 ) & ( baths == 2 )')


# Create indicator feature for transactions between 2010 and 2013, - resession
#df['during_recession'] = df['tx_year'].between(2010,2013).astype(int)

#project.addManualRuleForDefault(ed.EXPLORE_NEW_INDICATOR_VARIABLE, 'during_recession', '( tx_year >= 2010 ) & ( tx_year <= 2013 )')
       
#
#  new variables - needs to be user driven
#

# Create a school score feature that num_schools * median_school
#df['school_score'] = df['num_schools'] * df['median_school']
#project.addManualRuleForDefault(ed.EXPLORE_NEW_VARIABLE, 'school_score', 'num_schools * median_school')

# Create a property age feature
#project.addManualRuleForDefault(ed.EXPLORE_NEW_VARIABLE, 'property_age', 'tx_year - year_built')
#project.addManualRuleForDefault(ed.EXPLORE_REMOVE_ITEMS_BELOW, 'property_age',-1)

# Drop 'tx_year' and 'year_built' from the dataset
#df = df.drop(['tx_year','year_built'], axis=1)

#project.addManualRuleForDefault(ed.EXPLORE_DROP_COLUMN,'tx_year', None)
#project.addManualRuleForDefault(ed.EXPLORE_DROP_COLUMN,'year_built', None)




#project.cleanAndExploreProject()
#
#project.prepProjectByName('Property Data')
#project.trainProjectByName('Property Data')
#
#project.exportBestModel('realEstateBestModel.plk')
#project.exportNamedModel('gb','gbRealEstateModel.plk')
#project.exportNamedModel('lasso','lassoRealEstateModel.plk')
#project.exportNamedModel('ridge','ridgeRealEstateModel.plk')
#project.exportNamedModel('enet','enetRealEstateModel.plk')
#project.exportNamedModel('rf','rfRealEstateModel.plk')


#print 
#print 'the best is ', project.bestModelName
#print
#print project.bestModel




#



# Pick the winner
