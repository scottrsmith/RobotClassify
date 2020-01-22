#
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    ML Lib Producivity Class Library
    Copyright (C) 2019  Scott R Smith

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import print_function 
from __future__ import division


import numpy as np
import matplotlib.pyplot as plt
import itertools
from pathlib import Path
import pandas as pd


from .getData import getData
from .exploreData import exploreData
from .cleanData import cleanData, cleaningRules
from .prepData import prepData, prepPredictData
import mlLib.trainModels as tm
import mlLib.utility as utility



#utility.openLogs(logFile='runOutputLogFile.txt', errorFile='runErrorLogFile.txt', append=False)
#utility.openTraceLog(logFile='trace.txt', toTerminal=False, append=False)
utility.openLogs(logFile=None, errorFile=None)


    

class PassengerId(object):

    def __init__ (self):
        pass

    def run (self, counters, project, name, optionIn=0, auto=False):
        option = checkAuto(self, counters, name, optionIn, auto)
           
        if option==0:
            desc='Delete'
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['PassengerId'])

        return option,  desc
 

class Ticket(object):
    

    def __init__ (self):
        pass

    def run (self, counters, project, name, optionIn=0, auto=False):
        
        option = checkAuto(self, counters, name, optionIn, auto)
        if option==0:
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['Ticket'])
            desc='Delete'
        return option,  desc
 

class Parch(object):

    def __init__ (self):
        pass

    def run (self, counters, project, name, optionIn=0, auto=False):
        
        option = checkAuto(self, counters, name, optionIn, auto)

        if option==0:
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['Parch'])
            desc='Delete'
    
        if option==1:
            desc='Default'
            pass
    
        if option==2:
            desc='FamilyKeepSource'
            project.addManualRuleForDefault(ed.CLEANDATA_NEW_INDICATOR_VARIABLE, 'family', ' Parch + SibSp + 1')

        if option==3:
            desc='FamilyDelSource'
            project.addManualRuleForDefault(ed.CLEANDATA_NEW_INDICATOR_VARIABLE, 'family', ' Parch + SibSp + 1')
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['SibSp'])
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['Parch'])
        return option,  desc
 

class SibSp(object):

    def __init__ (self):
        pass

    def run (self, counters, project, name, optionIn=0, auto=False):
        
        option = checkAuto(self, counters, name, optionIn, auto)
        if option==0:
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['SibSp'])
            desc='Delete'
        if option==1:
            desc='Default'
            pass
        return option,  desc
 
class Pclass(object):

    def __init__ (self):
        pass

    def run (self, counters, project, name, optionIn=0, auto=False):
        
        option = checkAuto(self, counters, name, optionIn, auto)
        if option==0:
            desc='Delete'
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['Pclass'])
        if option==1:
            desc='Default'
            pass
        return option,  desc
 
class Sex(object):

    def __init__ (self):
        pass

    def run (self, counters, project, name, optionIn=0, auto=False):
        
        option = checkAuto(self, counters, name, optionIn, auto)
        if option==0:
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['Sex'])
            desc='Delete'
        if option==1:
            desc='Default'
            pass
        if option==2:
            desc='Rebucket2Int'
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET, 'Sex', [['male'], 1])
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET, 'Sex', [['female'], 0])
            project.addManualRuleForDefault(ed.CLEANDATA_CONVERT_DATATYPE, 'Sex', 'int64')
        return option,  desc
 
class Fare(object):

    def __init__ (self):
        pass

    def run (self, counters, project, name, optionIn=0, auto=False):
        
        option = checkAuto(self, counters, name, optionIn, auto)

        if option==0:
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['Fare'])
            desc='Delete'

        if option==1:
            project.addManualRuleForDefault(ed.CLEANDATA_ZERO_FILL, 'Fare')
            desc='Default'

        if option==2:
            desc='RebucketShortRange'
            project.addManualRuleForDefault(ed.CLEANDATA_ZERO_FILL, 'Fare')
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_RANGE, 'Fare',  [ (None,  'less',   7.91,  0),
                                                                               (7.91,  'between',14.454,1),
                                                                               (14.454,'between',31,    2),
                                                                               (None,  'more',   31.2,  3) ])
            project.addManualRuleForDefault(ed.CLEANDATA_CONVERT_DATATYPE, 'Fare', 'int64')
        if option==3:
            desc='MarkMissing'
            project.addManualRuleForDefault(ed.CLEANDATA_NUMERIC_MARK_MISSING, 'Fare', None)

        return option,  desc


class Cabin(object):


    def __init__ (self):
        pass

    def run (self, counters, project, name, optionIn=0, auto=False):
        
        option = checkAuto(self, counters, name, optionIn, auto)

        if option==0:
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['Cabin'])
            desc='Delete'

        if option==1:
            desc='Default'
            pass

        if option==2:
            desc='Has_CabinDropCabin'
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_TO_BINARY, 'Cabin', 'Has_Cabin')
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['Cabin']) #, 'Parch', 
        if option==3:
            desc='RebucketToFirstLetterInteger'
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_INCLUDE, 'Cabin',  [ (None, '0'),
                   ('A','1'),('B','2'),('C','3'),('D','4'),('E','5'),('F','6'),('G','7'),('T','0') ])
            project.addManualRuleForDefault(ed.CLEANDATA_CONVERT_DATATYPE, 'Cabin', 'int64')
        if option==4:
            desc='RebucketToFirstLetter'
            rebucket = [ (None, 'U'), ('A',''),('B',''),('C',''),('D',''),('E',''),('F',''),('G',''),('T','') ]
            categories = ['U', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'T']
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_INCLUDE, 'Cabin', rebucket)
            project.addManualRuleForDefault(ed.CLEANDATA_SET_CATEGORY_DATATYPE, 'Cabin',categories)

        return option,  desc

class Embarked(object):

    def __init__ (self):
        pass

    def run (self, counters, project, name, optionIn=0, auto=False):
        
        option = checkAuto(self, counters, name, optionIn, auto)
        if option==0:
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['Embarked'])
            desc='Delete'
        if option==1:
            project.addManualRuleForDefault(ed.CLEANDATA_MARK_MISSING, 'Embarked', 'S')
            desc='Default'
        if option==2:
            desc='RebucketToNumber'
            project.addManualRuleForDefault(ed.CLEANDATA_MARK_MISSING, 'Embarked', 'S')
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET, 'Embarked', [['S'],0])
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET, 'Embarked', [['Q'],1])
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET, 'Embarked', [['C'],2])
            project.addManualRuleForDefault(ed.CLEANDATA_CONVERT_DATATYPE, 'Embarked', 'int64')
        
        if option==3:
            desc='RebucketWithUnknown'
            project.addManualRuleForDefault(ed.CLEANDATA_MARK_MISSING, 'Embarked', 'U')
            project.addManualRuleForDefault(ed.CLEANDATA_SET_CATEGORY_DATATYPE, 'Embarked',['U','S','Q','C'])

        return option,  desc

class Age(object):

    def __init__ (self):
        pass

    def run (self, counters, project, name, optionIn=0, auto=False):
        
        option = checkAuto(self, counters, name, optionIn, auto)
            
        if option==0:
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['Age'])
            desc='Delete'

        if option==1:
            project.addManualRuleForDefault(ed.CLEANDATA_ZERO_FILL, 'Age')
            desc='Default'
            
        if option==2:
            desc='MarkMissing'
            project.addManualRuleForDefault(ed.CLEANDATA_NUMERIC_MARK_MISSING, 'Age', None)

        if option==3:
            desc='ShortRange'

            project.addManualRuleForDefault(ed.CLEANDATA_ZERO_FILL, 'Age')
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_RANGE, 'Age',   [ (None,  'less',   16, 0),
                                                                                   (16,    'between',32, 1),
                                                                                   (32,    'between',48, 2),
                                                                                   (48,    'between',64, 3),
                                                                                   (None,  'more',   64, 4) ])
            project.addManualRuleForDefault(ed.CLEANDATA_CONVERT_DATATYPE, 'Age', 'int64')
        
        if option==4:
            desc='MeanAges'
            project.addManualRuleForDefault(ed.CLEANDATA_NEW_FEATURE, 'tempName', 'Name', forPredict=False)
            rebucket = [
                   ('Mr.','Mr'),('Mrs.','Mrs'),('Miss.','Miss'),('Master.','Master'),('Rev.','Officer'),('Dr.','Officer'),
                   ('Ms.','Mrs'),('Major.','Officer'),('Lady.','Royalty'),('Sir.','Royalty'),('Col.','Officer'),
                   ('Mlle.','Miss'), ('Countess.','Royalty'),('Jonkheer.','Royalty'),('Don.','Royalty'),('Mme.','Mrs'),
                   ('Capt.','Officer'),('Dona.','Royalty')]
                   
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_INCLUDE, 'tempName',  rebucket, forPredict=True)
            
            project.addManualRuleForDefault(ed.CLEANDATA_GROUPBY_ROLLUP, ['tempName', 'Age'], { 'GroupName' : 'mean' }, forPredict=False)
            project.addManualRuleForDefault(ed.CLEANDATA_JOIN_ROLLUPS,'Mean Ages', None, forPredict=False)
        
            # update [training_table with 'table2'] for [trainingTable.ColNameToUpdate, 
            #                                    with table2.ColNameToUpdateWith] 
            #                                    where [trainingTable.colValue equals table2.colKey]
            project.addManualRuleForDefault(ed.CLEANDATA_UPDATE_FROM_TABLE2,'Mean Ages',
                                         [['Age','Mean Ages'],['tempName','GroupName']], forPredict=True)
        
            project.addManualRuleForDefault(ed.CLEANDATA_CONVERT_DATATYPE, 'Age', 'int64')
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['tempName'], forPredict=True)

            
        if option==5:
            desc='LongRange'
            project.addManualRuleForDefault(ed.CLEANDATA_ZERO_FILL, 'Age')
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_RANGE, 'Age',[ (None,  'less',   3, 0),
                                                                                    (8,    'between',12, 1),
                                                                                    (12,    'between',18, 2),
                                                                                    (18,    'between',25, 3),
                                                                                    (25,    'between',35, 4),
                                                                                    (35,    'between',50, 5),
                                                                                    (55,    'between',65, 6),
                                                                                    (65,    'between',70, 7),
                                                                                    (None,  'more',   70, 8) ])
            project.addManualRuleForDefault(ed.CLEANDATA_CONVERT_DATATYPE, 'Age', 'int64')
         
        return option, desc

class Name(object):

    def __init__ (self):
        pass
    
    def getName():
        return 'Name'
        
    def getFeaturesToTest()
        return (8)

    def run (self, counters, project, name, optionIn=0, auto=False):
        
        option = checkAuto(self, counters, name, optionIn, auto)
        if option==0:
            project.addManualRuleForDefault(ed.CLEANDATA_DROP_COLUMN,['Name'])
            desc='Delete'
        if option==1:
            # Mr.	Mrs.	Miss.	Master.	Rev.	Dr.	Ms.	Major.	Lady.	Sir.	Col.	
            # Mlle.	Countess.	Jonkheer.	Don.	Mme.	Capt.	Dona.
            desc='Default'
            pass
        if option==2:
            desc='rebucket2intShort'
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_INCLUDE, 'Name',  [ (None, '0'),
                   ('Mr.','1'),('Mrs.','2'),('Miss.','3'),('Master.','4'),('Rev.','5'),('Dr.','6'),
                   ('Ms.','3'),('Major.','7'),('Lady.','8'),('Sir.','8'),('Col.','8'),('Mlle.','8'),
                   ('Countess.','8'),('Jonkheer.','9'),('Don.','9'),('Mme.','9'),('Capt.','7'),('Dona.','9')])
            project.addManualRuleForDefault(ed.CLEANDATA_CONVERT_DATATYPE, 'Name', 'int64')
        if option==3:
            desc='rebucket2DescLong'
            rebucket =  [ 
                   ('Mr.',''),('Mrs.',''),('Miss.',''),('Master.',''),('Rev.',''),('Dr.',''),
                   ('Ms.',''),('Major.',''),('Lady.',''),('Sir.',''),('Col.',''),('Mlle.',''),
                   ('Countess.',''),('Jonkheer.',''),('Don.',''),('Mme.',''),('Capt.',''),('Dona.','')]
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_INCLUDE, 'Name', rebucket)

            categories = [w for w, x in tuple(rebucket)]
            project.addManualRuleForDefault(ed.CLEANDATA_SET_CATEGORY_DATATYPE, 'Name',categories)
        
        if option==4:
            desc='rebucket2intLong'
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_INCLUDE, 'Name',  [ (None, '0'),
                   ('Mr.','1'),('Mrs.','2'),('Miss.','3'),('Master.','4'),('Rev.','5'),('Dr.','5'),
                   ('Ms.','7'),('Major.','8'),('Lady.','9'),('Sir.','10'),('Col.','11'),('Mlle.','12'),
                   ('Countess.','13'),('Jonkheer.','14'),('Don.','15'),('Mme.','16'),('Capt.','17'),('Dona.','18')])
            project.addManualRuleForDefault(ed.CLEANDATA_CONVERT_DATATYPE, 'Name', 'int64')

        if option==5:
            desc='rebucket2intShort2'
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_INCLUDE, 'Name',  [ (None, '0'),
                   ('Mr.','1'),('Mrs.','2'),('Miss.','3'),('Master.','4'),('Rev.','5'),('Dr.','6'),
                   ('Ms.','7'),('Major.','8'),('Lady.','9'),('Sir.','10'),('Col.','8'),('Mlle.','11'),
                   ('Countess.','9'),('Jonkheer.','10'),('Don.','10'),('Mme.','9'),('Capt.','8'),('Dona.','9')])
            project.addManualRuleForDefault(ed.CLEANDATA_CONVERT_DATATYPE, 'Name', 'int64')

        if option==6:
            desc='rebucket2DescShort'
            rebucket = [
                   ('Mr.','Mr'),('Mrs.','Mrs'),('Miss.','Miss'),('Master.','Master'),('Rev.','Officer'),('Dr.','Officer'),
                   ('Ms.','Mrs'),('Major.','Officer'),('Lady.','Royalty'),('Sir.','Royalty'),('Col.','Officer'),('Mlle.','Miss'),
                   ('Countess.','Royalty'),('Jonkheer.','Royalty'),('Don.','Royalty'),('Mme.','Mrs'),('Capt.','Officer'),('Dona.','Royalty')]
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_INCLUDE, 'Name',  rebucket)
 
            categories = [x for w, x in tuple(rebucket)]
            project.addManualRuleForDefault(ed.CLEANDATA_SET_CATEGORY_DATATYPE, 'Name',list(set(categories)))

        if option==7:
            desc='rebucket2IntShort3'
            project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_INCLUDE, 'Name',  [ (None, '0'),
                   ('Mr.','1'),('Mrs.','2'),('Miss.','3'),('Master.','4'),('Rev.','5'),('Dr.','5'),
                   ('Ms.','2'),('Major.','5'),('Lady.','6'),('Sir.','6'),('Col.','5'),('Mlle.','3'),
                   ('Countess.','6'),('Jonkheer.','6'),('Don.','6'),('Mme.','3'),('Capt.','5'),('Dona.','6')])
            project.addManualRuleForDefault(ed.CLEANDATA_CONVERT_DATATYPE, 'Name', 'int64')
        
        return option,  desc
       


 

#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
fieldEngineering = [('PassengerId',PassengerId()),
                    ('Ticket',Ticket()),
                    ('Parch',Parch()),
                    ('SibSp',SibSp()),
                    ('Pclass',Pclass()),
                    ('Sex',Sex()),
                    ('Fare',Fare()),
                    ('Cabin',Cabin()),
                    ('Embarked',Embarked()),
                    ('Age',Age()),
                    ('Name',Name())]
      



#    def exe(counters, runCount, fieldListNames, runDesc):
project = mlProject('Titanic Survival', 'Udacity')

modelList1=['bagging', 'l1', 'l2', 'decisiontree', 'kneighbors',  'adaboost', 'gaussiannb']
modelList2=['bagging+l1', 'bagging+l2', 'bagging+decisiontree', 'bagging+kneighbors', 'bagging+gaussiannb']
modelList3=['adaboost+l1', 'adaboost+l2', 'adaboost+decisiontree', 'adaboost+gaussiannb']
modelList4=['rfc', 'etc']
modelList5=['adaboost+l1', 'sgd']


vote = project.makeVote(['bagging+kneighbors', 'bagging', 'l2', 'adaboost+decisiontree'])
vote = vote.pop()
modelAll = modelList1 + modelList2 + modelList3 + modelList4 + [vote]
RUN = tm.RUNDEFAULT
#RUN = tm.RUNSHORT
#RUN = tm.RUNLONG
#modelAll = ['kneighbors']


#LogFile ='' # Use None
resultsFile = 'BatchFeaturesLogs.csv'

project.setTrainingPreferences (crossValidationSplits=10, parallelJobs=-1, modelType=tm.TRAIN_CLASSIFICATION, 
                                modelList=modelAll, useStandardScaler=False, gridSearchScoring='accuracy',
                                testSize=0.25, logTrainingResultsFilename=resultsFile,
                                runHyperparameters=RUN, runEstimatorHyperparameters=RUN)

project.importFile('Survival Data', type='csv', description='Survival Data', fileName='titanic_train.csv',  hasHeaders = True)
project.setTarget('Survived')
project.setGoals( {'Accuracy': (0.82,'>'), 'F1': (0.846,'>'),'AUROC': (0.85,'>')})
project.setConfusionMatrixLabels([(0,'Not'), (1, 'Survived') ])


LogReporting = False
project.setOngoingReporting(LogReporting,'Survival Data')


project.exploreData()
project.initCleaningRules()


features, numFeatures,runDetails = runFieldEngineering(project, counters, fieldListNames, runCount)
if numFeatures==5:
    pass
else:   
    return True
utility.runLog ('\nfeatures,numFeatures={}\n'.format(features,numFeatures))
#utility.CSVLog(runDetails)



runNumber = str(runCount)



#print (project.preppedTablesDF['Survival Data'])


project.logTrainingResultsRunDescription(description='{}-{}-{}-{}'.format(runDesc,RUN,runNumber,features))
project.cleanAndExploreProject()

#project.prepProjectByName('Survival Data', outFile='ReadyToTrain.csv')
project.prepProjectByName('Survival Data')
project.trainProjectByName('Survival Data')

utility.runLog('The best is '.format(project.bestModelName))
utility.runLog(project.bestModel)

project.displayAllScores('Survival Data', short=True )
#project.reportResultsOnTrainedModel('Survival Data',project.bestModelName)
del project
return False





#############################################
############################################

fieldListNames=['PassengerId', 'Ticket', 'Parch', 'SibSp',  'Pclass', 'Sex',  'Fare', 'Cabin', 'Embarked', 'Age', 'Name']
counters = Counters()
counters.init(fieldListNames)

#utility.openCSVLog('FieldEngineering.csv',True, ['RunNumber','Description']+fieldListNames)
runCount = 17318
working = True
desc = 'TestFeatures'
while working:
    runProject(counters, runCount,fieldListNames, desc)
    runCount += 1
    isDone = counters.update()
    if isDone:
        working = False

utility.closeLogs()
    

