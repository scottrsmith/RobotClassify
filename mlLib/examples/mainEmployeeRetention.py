#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 12:54:33 2018

@author: scottsmith
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from mlLib.project import mlProject, loadPredictProject


from mlLib.getData import getData
import mlLib.exploreData as ed
from mlLib.exploreData import exploreData
from mlLib.cleanData import cleanData, cleaningRules
from mlLib.prepData import prepData
import mlLib.trainModels as tm




project = mlProject('Employee Retention', 'EDS Project 3')

project.setTrainingPreferences (crossValidationSplits=10, parallelJobs=-1, modelType=tm.TRAIN_CLASSIFICATION, modelList=['l1', 'l2', 'rfc', 'gbc'] ) 

project.importFile('Employee List', type='csv', description='Employee Retention', fileName='employee_data.csv',  hasHeaders = True)
#project.openProject('Predict Home Values2', type='GoogleSheet', description='Real Estate Project 2', location='1QC2v9jPJFTLYxjm-wkIuO1FpYhR-x6ic-utw0CBskU8',  hasHeaders = False, range='A1:Z1884')


project.setTarget('status', boolean=True, trueValue='Left')

project.exploreData()      

#print project.explore['Employee List']
#print project.explore['Employee List'].allStatsSummary()
#project.explore['Employee List'].plotHistogramsAll(10)
#project.explore['Employee List'].plotCategoryColumn('department')
#project.explore['Employee List'].plotCategoryColumn('salary')
#project.explore['Employee List'].plotCategoryColumn('status')
#project.explore['Employee List'].plotNumericColumn('')
#project.explore['Employee List'].plotSegmentation('satisfaction','status')
#project.explore['Employee List'].plotSegmentation('last_evaluation','status')
##project.explore['Employee List'].plotSegmentation('satisfaction','last_evaluation','status')
#project.explore['Employee List'].plotCorrelations()



project.runCleaningRules()

# Add manual Rules
project.addManualRuleForDefault(ed.EXPLORE_REMOVE_ITEMS_EQUAL, 'department', 'temp')
project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'department', [['information_technology'], 'IT'])
project.addManualRuleForDefault(ed.EXPLORE_NUMERIC_MARK_MISSING, 'last_evaluation', None)



#project.explore.dataSummary(10)


#project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'exterior_walls', [ ['Rock, Stone'], 'Masonry'])
#project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'exterior_walls', [ ['Concrete','Block'], 'Concrete Block'])
#project.addManualRuleForDefault(ed.EXPLORE_REMOVE_ITEMS_ABOVE, 'lot_size', 1220551)

# Status



### Feature Engineer


project.addManualRuleForDefault(ed.EXPLORE_NEW_INDICATOR_VARIABLE,  'underperformer', '( ( last_evaluation < 0.6 ) & ( last_evaluation_missing == 0 ) ) ')
project.addManualRuleForDefault(ed.EXPLORE_NEW_INDICATOR_VARIABLE,  'unhappy',        '( satisfaction < 0.2 )')
project.addManualRuleForDefault(ed.EXPLORE_NEW_INDICATOR_VARIABLE,  'overachiever',   '( ( last_evaluation > 0.8 ) & ( satisfaction > 0.7 ) ) ')


#
project.cleanAndExploreProject()
#

#project.addManualRuleForDefault(ed.EXPLORE_REBUCKET, 'roof', [['Gravel/Rock', 'Roll Composition', 'Slate', 'Built-up', 'Asbestos', 'Metal'], 'Other'])
#project.addManualRuleForDefault(ed.EXPLORE_NEW_INDICATOR_VARIABLE, 'during_recession', '( tx_year >= 2010 ) & ( tx_year <= 2013 )')
# Create a school score feature that num_schools * median_school
#df['school_score'] = df['num_schools'] * df['median_school']
#project.addManualRuleForDefault(ed.EXPLORE_NEW_VARIABLE, 'school_score', 'num_schools * median_school')
#
## Create a property age feature
#project.addManualRuleForDefault(ed.EXPLORE_NEW_VARIABLE, 'property_age', 'tx_year - year_built')
#project.addManualRuleForDefault(ed.EXPLORE_REMOVE_ITEMS_BELOW, 'property_age',-1)
#
## Drop 'tx_year' and 'year_built' from the dataset
##df = df.drop(['tx_year','year_built'], axis=1)
#
#project.addManualRuleForDefault(ed.EXPLORE_DROP_COLUMN,'tx_year', None)
#project.addManualRuleForDefault(ed.EXPLORE_DROP_COLUMN,'year_built', None)




project.prepProjectByName('Employee List')



project.trainProjectByName('Employee List')

project.exportBestModel('employeeBestModel.plk')
#project.exportNamedModel('l1','l1EmployeeModel.plk')
#project.exportNamedModel('l2','l2EmployeeModel.plk')
#project.exportNamedModel('rcf','rcfEmployeeModel.plk')
#project.exportNamedModel('gbc','gbcEmployeeModel.plk')



print 
print 'The best is ', project.bestModelName
print
print project.bestModel


# Pick the winner
predict = loadPredictProject('employeeBestModel.plk')
predict.importPredictFile('Employee Raw data', type='csv', description='Raw Data', fileName='unseen_raw_data.csv',  hasHeaders = True)
predict.prepPredict()
ans = predict.runPredict()
print ans

