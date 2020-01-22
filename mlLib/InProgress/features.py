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



def evaluateFeatureImportance(fileName):
    import numpy as np
    import matplotlib.pyplot as plt


        
    X = pd.read_csv(fileName, header=True, low_memory=False)
    # Create separate object for input features
    y = X[project.targetVariable[name]]

   
    # Create separate object for target variable
    X.drop(self.project.targetVariable[name], axis = 1, inplace=True)
    

    # Build a forest and compute the feature importances
    forest = ExtraTreesClassifier(n_estimators=250,
                                  random_state=0)

    forest.fit(X, y)
    importances = forest.feature_importances_
    std = np.std([tree.feature_importances_ for tree in forest.estimators_],
                 axis=0)
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    print("Feature ranking:")

    for f in range(X.shape[1]):
        print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))

    # Plot the feature importances of the forest
    plt.figure()
    plt.title("Feature importances")
    plt.bar(range(X.shape[1]), importances[indices],
           color="r", yerr=std[indices], align="center")
    plt.xticks(range(X.shape[1]), indices)
    plt.xlim([-1, X.shape[1]])
    plt.show()



class Counters(object):
    def __init__ (self):
        self.featureList = None
        #print (len(self.maxes))
 
# Run 1
        self.counter =   [7,0,0,0,3,1,1,1,0,0,0] # Reverse if the max digets   # 00011130006
        self.maxes =   [7,5,3,4,3,2,1,1,3,0,0] # Reverse if the max digets
        self.done = [2,2,2,2,1,0,1,0,0,0,0] # Reverse order of a number (Start) -00001012222
        
        
    def init (self, featureList, counters, maxes, done):
        self.featureList = featureList
        self.counter =   [7,0,0,0,3,1,1,1,0,0,0] # Reverse if the max digets   # 00011130006
        self.maxes =   [7,5,3,4,3,2,1,1,3,0,0] # Reverse if the max digets
        self.done = [2,2,2,2,1,0,1,0,0,0,0] # Reverse order of a number (Start) -00001012222
            
            
    def get(self,name):
        
        cLen = len(self.counter)
        for getName in self.featureList:
            cLen -= 1
            if getName == name:
                return(self.counter[cLen])
                
        
        
        for i in range(cLen,0,-1):
            if name==self.featureList[i]:
                return(self.counter[i])
        return -1


    def update(self):
        working = True
        digit = 0
        while working:
            digitValue = self.counter[digit]
            maxValue = self.maxes[digit]
            if digitValue < maxValue:
                digitValue += 1
                self.counter[digit] = digitValue
              
                working = False
            elif digitValue==maxValue:    
                self.counter[digit] = 0
                digit += 1   
            if digit==len(self.maxes)-1:
                return True
            elif self.done is not None:
                if self.counter==self.done:
                    return True
                
                
        return False

    def display(self):
        show = ''
        counter = self.counter.copy()
        while len(counter)>0:
            show += str(counter.pop())
        return show


def checkAuto(engineerClass, counters, name, inOption, auto):
    option = inOption
    if auto:
        option = counters.get(name)
    return option
    


def runFieldEngineering(project, counters, fieldListNames, runCount):
    fieldEngineering = [PassengerId(),
                    Ticket(),
                    Parch(),
                    SibSp(),
                    Pclass(),
                    Sex(),
                    Fare(),
                    Cabin(),
                    Embarked(),
                    Age(),
                    Name()]
    runDetails=[runCount,'Run Defaults']
    numFeatures = 0
    features = ''
    for name, engineer in zip(fieldListNames,fieldEngineering):
        option, desc = engineer.run(counters, project, name, auto=True)
        if option > 0:
            numFeatures += 1
        runDetails.append(desc)
        features+=str(option)
    return features, numFeatures, runDetails
  

#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################
class runProject(object):

    def __init__ (self, counters, runCount, featureClasses, runDesc):
        pass
        
    

    def exe(counters, runCount, fieldListNames, runDesc):
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




def runTest ():
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
    

