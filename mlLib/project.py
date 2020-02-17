#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#    ML Lib Producivity Class Library
#    Copyright (C) 2019  Scott R Smith
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ============================================================================#

"""
**Introduction**
----------------
The projects module is is a high-level library to process ML jobs at the
project level. All interactions can happen with this API

- Manage Projects
- Load Data
- Explore Data
- Auto-execute ML jobs
- Create cleaning rules
- Train the data, finding the best model
- Deploy model, to process ML transactions


"""

from __future__ import print_function
from __future__ import division
from sklearn.exceptions import NotFittedError
import pickle as pk
import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.utils.testing import ignore_warnings
from sklearn.exceptions import DataConversionWarning, ConvergenceWarning
from sklearn.metrics import SCORERS
import mlLib.mlUtility as mlUtility
import mlLib.trainModels as tm
from .prepData import prepData, prepPredictData
from .cleanData import cleanData, cleaningRules
from .exploreData import exploreData
from .getData import getData
import pickle
import pandas as pd
from pathlib import Path
import itertools
import matplotlib.pyplot as plt
import numpy as np


import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


basedir = os.path.abspath(os.path.dirname(__file__))

# ----------------------------------------------------------------------------#
# Helper Functions
#    dump: print out the contents of an object
# ----------------------------------------------------------------------------#


def dumpObj(obj, name='None'):
    print('\n\nDump of object...{}'.format(name))
    for attr in dir(obj):
        print("    obj.%s = %r" % (attr, getattr(obj, attr)))


def dumpData(obj, name='None'):
    print('\n\nDump of data...{}'.format(name))
    for attr in obj:
        print("    data.%s = %r" % (attr, obj[attr]))


# ----------------------------------------------------------------------------#
# ----------------------------------------------------------------------------#
def autoFlaskEvaluateClassifier(projectName=None,
                                trainingFile=None,
                                testingFile=None,
                                trainingFileDF=None,
                                testingFileDF=None,
                                targetVariable=None,
                                key=None,
                                predictSetOut=[None],
                                trainingFileOut=None,
                                logFileOut=None,
                                transcriptFile=None,
                                predictFileOut=None,
                                resultsFile=None,
                                modelList=None,
                                confusionMatrixLabels=[],
                                scoring='f1',
                                useProba=False,
                                bottomImportancePrecentToCut=None,
                                setProjectGoals={'f1': (0.9, '>')},
                                runVerbose=0,
                                recommendOnly=None,
                                basicAutoMethod=None,
                                doExplore=True,
                                doTrain=True,
                                doPredict=True,
                                skewFactor=None,
                                toTerminal=True
                                ):
    """
        **autoFlaskEvaluateClassifier**

        Auto-process an ML job for Flask Servers

        **XXXXX**

        - Sample Call::

            Example Call


        - Expected Success Response::

            Example Success Response


        - Expected Fail Response::

            Example fail response

    """

    TRAININGFILENAME = 'Training'
    TESTINGFILENAME = 'Testing'

    tm.memorySnapshot('Start...', cnt=25, start=True)

    results = {}

    mlUtility.openLogs(logFile=transcriptFile,
                       errorFile=None, toTerminal=toTerminal)

    project = mlProject(projectName, projectName)

    project.setTrainingPreferences(
        crossValidationSplits=5,
        parallelJobs=-1,
        modelType=tm.TRAIN_CLASSIFICATION,
        modelList=modelList,
        useStandardScaler=False,
        gridSearchScoring=scoring,
        testSize=.2,
        logTrainingResultsFilename=logFileOut,
        gridSearchVerbose=runVerbose,
        bottomImportancePrecentToCut=bottomImportancePrecentToCut,
        useProbaForPredict=useProba,
        recommendOnly=recommendOnly,
        basicAutoMethod=basicAutoMethod,
        runHyperparameters=tm.RUNDEFAULT,
        runEstimatorHyperparameters=tm.RUNDEFAULT,
        runAutoFeaturesMode=True,
        skewFactor=skewFactor,
        runMetaClassifier=tm.RUNDEFAULT)

    if type(trainingFileDF) is bytes:
        project.importFile(TRAININGFILENAME,
                           type='df',
                           description=TRAININGFILENAME,
                           fileName=trainingFile,
                           df=pickle.loads(trainingFileDF),
                           hasHeaders=True)
    else:
        project.importFile(TRAININGFILENAME,
                           type='csv',
                           description=TRAININGFILENAME,
                           fileName=trainingFile,
                           hasHeaders=True)

    if type(testingFileDF) is bytes:
        project.importFile(TESTINGFILENAME,
                           type='df',
                           description=TESTINGFILENAME,
                           fileName=testingFile,
                           df=pickle.loads(testingFileDF),
                           hasHeaders=True)
    else:
        project.importFile(TESTINGFILENAME,
                           type='csv',
                           description=TESTINGFILENAME,
                           fileName=testingFile,
                           hasHeaders=True)

    project.setTarget(targetVariable)
    project.saveKey(TESTINGFILENAME, key)
    project.MergeFilesAsTrainAndTest(TRAININGFILENAME, TESTINGFILENAME)

    project.dropColumn(TRAININGFILENAME, key)

    project.setGoals(setProjectGoals)
    # project.setGoals( {'Accuracy': (0.9,'>'),
    # 'f1': (0.85,'>'),'AUROC': (0.9,'>')})
    project.setConfusionMatrixLabels(confusionMatrixLabels)

    project.setOngoingReporting(False, TRAININGFILENAME)

    project.exploreData(TRAININGFILENAME)
    results['recommendations'] = project.explore[TRAININGFILENAME]\
        .getRecommendationsAsObject()

    if doExplore:
        # mlUtility.runLog (project.explore[TRAININGFILENAME])
        # mlUtility.runLog (project.explore[TRAININGFILENAME].
        #                                           allStatsSummary())

        pass
        results['exploreheatmap'] = project.explore[TRAININGFILENAME].\
            plotExploreHeatMap(toWeb=True)

        # project.explore[TRAININGFILENAME].plotFeatureImportance()
        # project.explore[TRAININGFILENAME].plotColumnImportance()
        # project.explore[TRAININGFILENAME].plotHistogramsAll(10)
        # project.explore[TRAININGFILENAME].plotCorrelations()

    project.initCleaningRules(TRAININGFILENAME)
    results['cleaninglog'] = project.cleanProject(TRAININGFILENAME)
    project.prepProjectByName(TRAININGFILENAME, outFile=trainingFileOut)

    if doTrain:
        project.trainProjectByName(TRAININGFILENAME)

        # Reporting to web
        results['scores'] = project.displayAllScores(TRAININGFILENAME)
        final = {}
        final['bestmodel'] = project.bestModelName
        final['scoring'] = scoring
        final['bestscore'] = project.bestModelScore[scoring]
        final['model'] = project.bestModel
        results['final'] = final

        # Reporting to log
        mlUtility.runLog('\n\nThe best is {}'.format(project.bestModelName))
        mlUtility.runLog(project.bestModel)
        mlUtility.runLog('\n\n')
        # project.reportResultsOnTrainedModel(TRAININGFILENAME,
        # project.bestModelName)

    predictFileDF = None
    if doPredict:
        predict = project.createPredictFromBestModel(TRAININGFILENAME)

        # predict.importPredictFile('Kaggle Data', type='csv',
        #                           description='Raw Data',
        #                           fileName='./Data/titanic_test.csv',
        #                           hasHeaders = True)

        predict.importPredictFromDF(
            project.PullTrainingData(), readyForPredict=True)
        keyName, keyData = project.getKey()

        predict.prepPredict()
        predict.exportPreppedFile(
            predictFileOut, columnName=keyName, columnData=keyData)

        ans = predict.runPredict()

        # Prepare the predict file for Kaggle upload
        predict.addToPredictFile(keyName, keyData)
        if useProba:
            pass
        else:
            ans = [int(x) for x in ans]
        predict.addToPredictFile(targetVariable, ans)
        predict.keepFromPredictFile(predictSetOut)
        # predict.exportPredictFile(resultsFile)
        predictFileDF = predict.getPredictFileDF()
        # results['downloadfile'] = basedir + '/' + resultsFile

    mlUtility.closeLogs()

    if project is not None:
        del project
    if predict is not None:
        del predict

    return results, predictFileDF


def autoEvaluateClassifier(projectName=None,
                           trainingFile=None,
                           testingFile=None,
                           targetVariable=None,
                           key=None,
                           predictSetOut=[None],
                           trainingFileOut=None,
                           logFileOut=None,
                           transcriptFile=None,
                           predictFileOut=None,
                           resultsFile=None,
                           modelList=None,
                           confusionMatrixLabels=[],
                           scoring='f1',
                           useProba=False,
                           bottomImportancePrecentToCut=None,
                           setProjectGoals={'f1': (0.9, '>')},
                           runVerbose=1,
                           recommendOnly=None,
                           basicAutoMethod=None,
                           doExplore=True,
                           doTrain=True,
                           doPredict=True,
                           skewFactor=None,
                           toTerminal=True
                           ):
    """
        **autoEvaluateClassifier**

        Auto-process an ML job for

        **XXXXX**

        - Sample Call::

            Example Call


        - Expected Success Response::

            Example Success Response


        - Expected Fail Response::

            Example fail response

    """

    TRAININGFILENAME = 'Training'
    TESTINGFILENAME = 'Testing'

    mlUtility.openLogs(logFile=transcriptFile,
                       errorFile=None, toTerminal=toTerminal)

    project = mlProject(projectName, projectName)

    project.setTrainingPreferences(
        crossValidationSplits=5,
        parallelJobs=-1,
        modelType=tm.TRAIN_CLASSIFICATION,
        modelList=modelList,
        useStandardScaler=False,
        gridSearchScoring=scoring,
        testSize=.2,
        logTrainingResultsFilename=logFileOut,
        gridSearchVerbose=runVerbose,
        bottomImportancePrecentToCut=bottomImportancePrecentToCut,
        useProbaForPredict=useProba,
        recommendOnly=recommendOnly,
        basicAutoMethod=basicAutoMethod,
        runHyperparameters=tm.RUNDEFAULT,
        runEstimatorHyperparameters=tm.RUNDEFAULT,
        runAutoFeaturesMode=True,
        skewFactor=skewFactor,
        runMetaClassifier=tm.RUNDEFAULT)

    project.importFile(TRAININGFILENAME,
                       type='csv',
                       description=TRAININGFILENAME,
                       fileName=trainingFile,
                       hasHeaders=True)
    project.importFile(TESTINGFILENAME,
                       type='csv',
                       description=TESTINGFILENAME,
                       fileName=testingFile,
                       hasHeaders=True)

    project.setTarget(targetVariable)
    project.saveKey(TESTINGFILENAME, key)
    project.MergeFilesAsTrainAndTest(TRAININGFILENAME, TESTINGFILENAME)

    project.dropColumn(TRAININGFILENAME, key)

    project.setGoals(setProjectGoals)
    # project.setGoals( {'Accuracy': (0.9,'>'), 'f1': (0.85,'>'),
    #                   'AUROC': (0.9,'>')})
    # project.setConfusionMatrixLabels(confusionMatrixLabels)

    project.setOngoingReporting(False, TRAININGFILENAME)

    project.exploreData(TRAININGFILENAME)

    if doExplore:
        mlUtility.runLog(project.explore[TRAININGFILENAME])
        # mlUtility.runLog (project.explore[TRAININGFILENAME].\
        #                           allStatsSummary())
        project.explore[TRAININGFILENAME].plotExploreHeatMap()
        # project.explore[TRAININGFILENAME].plotFeatureImportance()
        # project.explore[TRAININGFILENAME].plotColumnImportance()
        # project.explore[TRAININGFILENAME].plotHistogramsAll(10)
        # project.explore[TRAININGFILENAME].plotCorrelations()

    project.initCleaningRules(TRAININGFILENAME)
    project.cleanProject(TRAININGFILENAME)
    project.prepProjectByName(TRAININGFILENAME, outFile=trainingFileOut)

    if doTrain:
        project.trainProjectByName(TRAININGFILENAME)

        mlUtility.runLog('\n\nThe best is {}'.format(project.bestModelName))
        mlUtility.runLog(project.bestModel)
        mlUtility.runLog('\n\n')
        project.reportResultsOnTrainedModel(
            TRAININGFILENAME, project.bestModelName)

    if doPredict:
        predict = project.createPredictFromBestModel(TRAININGFILENAME)

        # predict.importPredictFile('Kaggle Data', type='csv',
        #                           description='Raw Data',
        #                           fileName='./Data/titanic_test.csv',
        #                           hasHeaders = True)

        predict.importPredictFromDF(
            project.PullTrainingData(), readyForPredict=True)
        keyName, keyData = project.getKey()

        predict.prepPredict()
        predict.exportPreppedFile(
            predictFileOut, columnName=keyName, columnData=keyData)

        ans = predict.runPredict()

        # Prepare the predict file for Kaggle upload
        predict.addToPredictFile(keyName, keyData)
        if useProba:
            pass
        else:
            ans = [int(x) for x in ans]
        predict.addToPredictFile(targetVariable, ans)
        predict.keepFromPredictFile(predictSetOut)
        predict.exportPredictFile(resultsFile)

    mlUtility.closeLogs()


def getMLScoringFunctions():
    return sorted(SCORERS.keys())

# ----------------------------------------------------------------------------#


class mlProject (object):
    """

    mlProject is the top level object for training and running a ML project.
    Various object mothods are used to load, review, and train the data, as
    well as manage running predictions

    Example:
    project = mlProject('Customer Segements', 'clustering model should factor
    in both aggregate sales patterns and specific items purchased')


    """

    def __init__(self, name, description=None):

        self.name = name
        self.description = description
        self.dataFile = {}
        self.preppedTablesDF = {}
        self.defaultPreppedTableName = None
        self.batchTablesList = {}
        self.explore = {}
        self.cleaningRules = {}

        # ********** PARAMATER DEFFAULTS
        # Training variables
        self.crossValidationSplits = 10
        self.parallelJobs = -1
        self.modelType = None
        self.modelList = None
        self.testSize = .2
        self.randomState = 1234
        self.uniqueThreshold = 50
        self.dropDuplicates = True
        self.recommendOnly = False
        self.basicAutoMethod = True

        # Clustering
        # kmeans defaults

        self.varianceThreshold = .8
        self.clusterDimensionThreshold = 20
        self.kmeansClusters = 3
        self.useStandardScaler = True

        self.fbeta = 1.0
        self.runHyperparameters = tm.RUNDEFAULT
        self.runEstimatorHyperparameters = tm.RUNDEFAULT
        self.runMetaClassifier = tm.RUNDEFAULT

        self.smallSample = 25
        self.highDimensionality = 100

        # Gridsearch Variables
        self.gridSearchVerbose = 0
        self.gridSearchScoring = None

        self.featuresToReport = 10
        self.skewFactor = 3.0

        self.logTrainingResultsFilename = 'mlLibRunLog.csv'

        # THIS IS ALL INTERNAL STUFF

        # Training variable for tables
        self.targetVariable = {}
        self.targetVariableIsBoolean = {}
        self.targetVariableTrueValue = {}
        self.targetVariableConvertValues = {}
        self.trainedModels = {}
        self.modelListAsRun = None
        self.alias = {}

        # Prediction variables
        self.useProbaForPredict = False
        self.competitionMode = False

        # training prep data - preppedData class
        self.preppedData = {}

        self.overrideHyperparameters = {}
        self.hyperparametersOverrideForBaseEstimator = {}
        self.hyperparametersOverrideForMetaClassifier = {}
        self.runAutoFeaturesMode = False

        # Set merged testing and taining set data
        self.mergedTrainingAndTest = False
        self.mergedTrainingAndTestFileName = None
        self.isTrainingSet = 'IsTrainingSet'
        self.saveKeyData = None
        self.saveKeyColName = None

        self.modelScores = None
        self.bestModelName = None
        self.bestModelScore = None
        self.bestModel = None

        # Evaluation metrics
        self.featureImportanceThreshold = 0.05
        self.bottomImportancePrecentToCut = .20
        self.correlationThreshold = 0.10

        # Reporting
        self.featureImportance = {}
        self.correlations = {}
        self.confusionMatrixLabels = None
        self.ongoingReporting = False
        self.ongoingReportingFilename = None
        self.logDescription = None
        self.dataColumns = None
        s = str(datetime.datetime.now())
        self.runStartTime = '{}'.format(s[:16])
        # Goals
        self.goalsToReach = None
        return

    def setTrainingPreferences(self,
                               crossValidationSplits=None,
                               parallelJobs=None,
                               modelType=None,
                               modelList=None,
                               testSize=None,
                               randomState=None,
                               uniqueThreshold=None,
                               dropDuplicates=None,
                               clusterDimensionThreshold=None,
                               varianceThreshold=None,
                               kmeansClusters=None,
                               useStandardScaler=None,
                               fbeta=None,
                               runHyperparameters=None,
                               runEstimatorHyperparameters=None,
                               runMetaClassifier=None,
                               runAutoFeaturesMode=None,
                               smallSample=None,
                               highDimensionality=None,
                               gridSearchVerbose=None,
                               gridSearchScoring=None,
                               featuresToReport=None,
                               logTrainingResultsFilename=None,
                               useProbaForPredict=None,
                               recommendOnly=None,
                               basicAutoMethod=None,
                               competitionMode=None,
                               skewFactor=None,
                               bottomImportancePrecentToCut=None
                               ):
        """
            **setTrainingPreferences**

            setTrainingPreferences for an ML job

            **XXXXX**

            - Sample Call::

                Example sample call


            - Expected Success Response::

                Example Success Response


            - Expected Fail Response::

                Example fail response

        """

        if modelType is not None:
            if modelType in tm.availableModels:
                self.modelType = modelType
            else:
                mlUtility.raiseError(modelType + ' is not a valid model type')

        if modelList is not None:
            noAliasModelList = []
            for x in modelList:
                # First check for Alias
                mod = x.split('#')
                # Split out the first part of the model i.e. the alias value
                m = mod[0]
                if len(mod) > 1:  # add the alias
                    self.alias[mod[1]] = m
                if mlUtility.getFirst(m) not in\
                   tm.availableModels[self.modelType]:
                    mlUtility.raiseError('Model {} not found'.format(m))
                noAliasModelList.append(m)
            self.modelList = noAliasModelList
        elif self.modelType is not None:
            self.modelList = tm.availableModels[self.modelType]

        if parallelJobs is not None:
            self.parallelJobs = parallelJobs

        if useStandardScaler is not None:
            self.useStandardScaler = useStandardScaler

        if fbeta is not None:
            self.fbeta = fbeta

        if runHyperparameters is not None:
            self.runHyperparameters = runHyperparameters

        if runEstimatorHyperparameters is not None:
            self.runEstimatorHyperparameters = runEstimatorHyperparameters

        if runMetaClassifier is not None:
            self.runMetaClassifier = runMetaClassifier

        if featuresToReport is not None:
            self.featuresToReport = featuresToReport

        if testSize is not None:
            self.testSize = testSize

        if randomState is not None:
            self.randomState = randomState

        if uniqueThreshold is not None:
            self.uniqueThreshold = uniqueThreshold

        if dropDuplicates is not None:
            self.dropDuplicates = dropDuplicates

        if clusterDimensionThreshold is not None:
            self.clusterDimensionThreshold = clusterDimensionThreshold

        if varianceThreshold is not None:
            self.varianceThreshold = varianceThreshold

        if kmeansClusters is not None:
            self.kmeansClusters = kmeansClusters

        if gridSearchVerbose is not None:
            self.gridSearchVerbose = gridSearchVerbose

        if crossValidationSplits is not None:
            self.crossValidationSplits = crossValidationSplits

        if smallSample is not None:
            self.smallSample = smallSample

        if highDimensionality is not None:
            self.highDimensionality = highDimensionality

        if logTrainingResultsFilename is not None:
            self.logTrainingResultsFilename = logTrainingResultsFilename

        if useProbaForPredict is not None:
            self.useProbaForPredict = useProbaForPredict

        if competitionMode is not None:
            self.competitionMode = competitionMode

        if runAutoFeaturesMode is not None:
            self.runAutoFeaturesMode = runAutoFeaturesMode

        if skewFactor is not None:
            self.skewFactor = skewFactor

        if bottomImportancePrecentToCut is not None:
            self.bottomImportancePrecentToCut = bottomImportancePrecentToCut

        if recommendOnly is not None:
            self.recommendOnly = recommendOnly

        if basicAutoMethod is not None:
            self.basicAutoMethod = basicAutoMethod

        # Set the scoring function
        # https://scikit-learn.org/stable/modules/model_evaluation.html#scoring-parameter

        if gridSearchScoring is None:
            if self.modelType == tm.TRAIN_REGRESSION:
                self.gridSearchScoring = 'r2'
            elif self.modelType == tm.TRAIN_CLASSIFICATION:
                self.gridSearchScoring = 'accuracy'
            else:  # tm.TRAIN_CLUSTERING
                self.gridSearchScoring = None
        else:
            self.gridSearchScoring = gridSearchScoring

    def setHyperparametersOverride(
                                   self,
                                   modelName,
                                   override,
                                   forBaseEstimator=False,
                                   forMetaClassifier=False):
        """
        Purpose:
        Set the hyperparameters to override the defaults for a model

        Example::

            hyperparameters = {
                    'lasso__alpha' : [0.001, 0.01, 0.1, 1, 5, 10]
                    }
            project.setHyperparametersOverride(self, 'lasso', hyperparameters)


            hyperparameters = {
                'lasso__alpha': [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10]
                }
            hyperparameters = {
                'ridge__alpha': [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10]
            }
            hyperparameters = {
                'elasticnet__alpha':
                    [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10],
                'elasticnet__l1_ratio' : [0.1, 0.3, 0.5, 0.7, 0.9]
            }
            hyperparameters = {
                'randomforestregressor__n_estimators': [50, 100, 200, 500],
                'randomforestregressor__max_features': ['auto', 'sqrt', 0.33]}
            hyperparameters = {
                'gradientboostingregressor__n_estimators': [50, 100, 200, 500],
                'gradientboostingregressor__learning_rate':
                        [0.001, 0.05, 0.1, 0.5],
                'gradientboostingregressor__max_depth': [1, 5, 10, 50]}
            hyperparameters = {'decisiontreeregressor__max_depth':
                                [1, 8, 16, 32, 64, 200]}
            hyperparameters = {
                    'logisticregression__C' : np.linspace(1e-4, 1e3, num=50),
                    'logisticregression__max_iter': [25, 50, 100, 300, 500]
                    }
            hyperparameters = {
                    'logisticregression__C' : np.linspace(1e-4, 1e3, num=50),
                    'logisticregression__max_iter': [25, 100, 300, 500]
                    }
            hyperparameters = {'randomforestclassifier__n_estimators':
                                [100, 200],
                                'randomforestclassifier__max_features':
                                ['auto', 'sqrt', 0.33]}
            hyperparameters = {'gradientboostingclassifier__n_estimators':
                                [50, 100, 200, 500],
                'gradientboostingclassifier__max_depth': [1, 10, 50, 100],
                'gradientboostingclassifier__learning_rate':
                [.1, .01, .001,.0001]}

        """
        if forMetaClassifier:
            self.hyperparametersOverrideForMetaClassifier[modelName] = override
        elif forBaseEstimator:
            self.hyperparametersOverrideForBaseEstimator[modelName] = override
        else:
            self.overrideHyperparameters[modelName] = override

    def setConfusionMatrixLabels(self, list):
        """

           Example: project.setConfusionMatrixLabels(
                            [(0,'Paid'), (1, 'Default') ])

        """

        self.confusionMatrixLabels = list
        return

    def setTarget(self, value, boolean=False,
                  trueValue=None, convertTable=None, tableName=None):
        """
        Purpose: Set the target variable for supervised learning.

        Call: setTarget(self, value, boolean=False, trueValue=None,
                        convertTable=None, tableName=None):

        Example:
                project.setTarget('loan_status')


            trueValue = what is the true values
            boolean = is this a boolean value
            convertTable = a table of how to convert values

        """
        if tableName is not None:
            if tableName in self.preppedTablesDF:
                theName = tableName
        else:
            theName = self.defaultPreppedTableName
        self.targetVariable[theName] = value
        self.targetVariableIsBoolean[theName] = boolean
        self.targetVariableTrueValue[theName] = trueValue
        self.targetVariableConvertValues[theName] = convertTable
        return

    def importFile(self, name, type=None, description=None,
                   location=None, fileName=None, sheetName=None,
                   df=None, hasHeaders=False, range=None, isDefault=False):
        """
            def importFile(self, name, type=None, description=None,
                          location=None, fileName=None, sheetName=None,
                          hasHeaders = False,
                          range=None, isDefault=False):


            project.importFile('Loan Data', type='csv',
                    description='Lending Club Data from 2017-2018',
                    fileName='LendingClub2017_2018ready.csv',
                    hasHeaders = True, isDefault=True)

        """

        self.dataFile[name] = getData(name, type=type,
                                      description=description,
                                      location=location,
                                      fileName=fileName,
                                      sheetName=sheetName,
                                      range=range,
                                      df=df,
                                      hasHeaders=hasHeaders)
        self.preppedTablesDF[name] = self.dataFile[name].openTable()
        if isDefault:
            self.defaultPreppedTableName = name
        elif self.defaultPreppedTableName is None:
            self.defaultPreppedTableName = name

    def exportFile(self, name, filename):
        """
        Purpose: Export the named file. (Projects can have multiuple
        files associated with them)

        Call: def exportFile(self, name, filename):

        Example: project.exportFile('Loan Data', 'fileout.csv'):

        """
        if name in self.preppedTablesDF:
            self.preppedTablesDF[name].to_csv(filename, index=False)
        return

    def getColumn(self, name, columnName):
        """
        Purpose: Get a columns from the data file

        Call: def getColumn(self, name, column):

        Example: project.getColumn('Loan Data','Name')

        """
        if name in self.preppedTablesDF:
            df = self.preppedTablesDF[name]
            if columnName in df:
                return df[columnName]
        return None

    def dropColumn(self, name, columnName):
        if name in self.preppedTablesDF:
            df = self.preppedTablesDF[name]
            if columnName in df:
                df.drop(columnName, axis=1, inplace=True)
        return None

    # Used to save row keys, not used for training

    def saveKey(self, filename, columnName):
        if filename in self.preppedTablesDF:
            if columnName in self.preppedTablesDF[filename]:
                self.saveKeyData = self.preppedTablesDF[filename][columnName]\
                                   .tolist()
                self.saveKeyColName = columnName
            else:
                mlUtility.errorLog('Key, {}, not found'.format(columnName))
        return None

    # Used to get row keys, not used for training
    def getKey(self):
        if self.saveKeyColName is not None:
            return self.saveKeyColName, self.saveKeyData
        else:
            mlUtility.errorLog('No keys were saved. Sorry.')
            return None

    def MergeFilesAsTrainAndTest(self, trainingFile, testingFile):
        if trainingFile in self.preppedTablesDF and testingFile\
           in self.preppedTablesDF:
            # Mark files
            self.preppedTablesDF[trainingFile][self.isTrainingSet] = True
            self.trainingSetLength = len(self.preppedTablesDF[trainingFile])-1
            self.preppedTablesDF[testingFile][self.isTrainingSet] = False

            self.preppedTablesDF[trainingFile] = pd.concat(
                 objs=[self.preppedTablesDF[trainingFile],
                       self.preppedTablesDF[testingFile]],
                 axis=0, sort=False).reset_index(drop=True)

            self.mergedTrainingAndTest = True
            self.mergedTrainingAndTestFileName = testingFile
            mlUtility.runLog(
                'Training file, {}, and testing file, {}, merged'
                .format(trainingFile, testingFile))

        else:
            mlUtility.errorLog(
                'One or more filename ({}, {}) not found'
                .format(trainingFile, testingFile))
        return None

    def PullTrainingData(self):
        if self.mergedTrainingAndTest:
            if self.mergedTrainingAndTestFileName in self.preppedTablesDF:
                return (self.preppedTablesDF
                        [self.mergedTrainingAndTestFileName])
            else:
                mlUtility.errorLog('Training file, {}, not found'.format(
                    self.mergedTrainingAndTestFileName))

        return None


######
#
# Description:
#
# example:
#
# params
#           name =
#           value =
#
#
######
    def groupByValue(self, filename, columnList, value='mean'):

        if filename in self.preppedTablesDF:
            df = self.preppedTablesDF[filename]
        else:
            mlUtility.errorLog('Filename {} not found'.format(filename))
            return None

        if value not in ['mean']:
            mlUtility.errorLog('Group function {} not found'.format(svalue))
        if type(columnList) is not list:
            if columnList not in df:
                mlUtility.errorLog('Columns {} not found for {}'.format, value)
                return None
            else:
                columnsToRun = [columnList]
        else:
            for name in columnList:
                if name not in df:
                    mlUtility.errorLog(
                        'Columns {} not for {}'.format(name, value))
            columnsToRun = columnList

        if value == 'mean':
            return df.groupby(columnsToRun).mean()
        return None

    def exploreData(self, fileName=None):
        """
        Purpose: Run the explore data function. This will review the data
                 and make recommendations

        Call: exploreData(self):

        Example: project.exploreData()

        """
        if fileName is None:
            for name in self.preppedTablesDF:
                self.explore[name] = exploreData(
                    self.preppedTablesDF[name], self, name)
        else:
            self.explore[fileName] = exploreData(
                self.preppedTablesDF[fileName], self, fileName)

    def initCleaningRules(self, fileName=None):
        """
               Before adding any cleaning rules you must init

               project.initCleaningRules()

               project.addManualRuleForDefault(
                   ed.CLEANDATA_REBUCKET_TO_BINARY,
                   'term', [['36 months', ' 36 months'],
                   '36'])
               project.addManualRuleForDefault(
                   'ed.CLEANDATA_REBUCKET_TO_BINARY,
                   'term', [['60 months', ' 60 months'], '60'])

        """
        if fileName is None:
            for name in self.preppedTablesDF:
                self.cleaningRules[name] = cleaningRules(
                    self, self.explore[name])
        else:
            self.cleaningRules[fileName] = cleaningRules(
                self, self.explore[fileName])

    # Just run the cleaning rules - do not explore

    def cleanProject(self, fileName=None):
        """
        Purpose: Run the cleaning rules established for a project.

        Call: cleanProject(self)

        Example: project.cleanProject()

        """
        cleaningLog = []
        if fileName is None:
            for name in self.preppedTablesDF:
                cleanDataClass = cleanData(
                    self.preppedTablesDF[name],
                    self.cleaningRules[name],
                    isPredict=False)
                cleaningLog.append(l)
        else:
            cleaningLog = cleanData(
                self.preppedTablesDF[fileName],
                self.cleaningRules[fileName],
                isPredict=False)

        return cleaningLog

    def cleanAndExploreProject(self, fileName=None):
        """
        Purpose: Run clean and explore together

        Call: def cleanAndExploreProject(self)

        Example: project.cleanAndExploreProject()

        """

        if fileName is None:
            for name in self.preppedTablesDF:
                cleanData(
                    self.preppedTablesDF[name],
                    self.cleaningRules[name],
                    isPredict=False)

            for name in self.preppedTablesDF:
                self.explore[name] = exploreData(
                    self.preppedTablesDF[name], self, name)
        else:
            cleanData(
                self.preppedTablesDF[fileName],
                self.cleaningRules[fileName],
                isPredict=False)
            self.explore[fileName] = exploreData(
                self.preppedTablesDF[fileName], self, fileName)
        return

    def prepProjectByName(self, tableName=None, outFile=None):
        """
        Purpose: Prepare the 'table' for training. This will one-hot encode,
                 for example.

        Call: prepProjectByName(self, tableName=None)

        Example: project.prepProjectByName('Loan Data')

        """
        if tableName is not None:
            theName = tableName
        else:
            theName = self.defaultPreppedTableName

        if theName in self.preppedTablesDF:
            self.preppedData[theName] = prepData(theName, self, outFile)
        return

    def writePreppedFileByName(self, filename, tableName=None):
        """
        Purpose: Once a file has been cleaned and explorred

        Call:

        Example:

        """
        if tableName is not None:
            theName = tableName
        else:
            theName = self.defaultPreppedTableName
        if theName in self.preppedTablesDF:
            mlUtility.runLog('Exporting Prepped Data '+theName)
            self.preppedTablesDF[theName].to_csv(filename, index=False)
        return

    def writeTrainingSetFileByName(self, filename, tableName=None):
        """
        Purpose:

        Call:

        Example:

        """
        if tableName is not None:
            theName = tableName
        else:
            theName = self.defaultPreppedTableName
        if theName in self.preppedData:
            X_train, X_test, y_train, y_test = self.preppedData[theName]\
                .getTrainingSet()
            mlUtility.runLog('Exporting Training Set ' +
                             theName+' to file '+filename)
            X_train.to_csv(filename, index=False)
        return

    def trainProjectByName(self, tableName=None):
        """
        Purpose:

        Call:

        Example:

        """
        if tableName is not None:
            theName = tableName
        else:
            theName = self.defaultPreppedTableName
        if theName in self.preppedTablesDF:
            self.trainedModels[theName] = tm.trainModels(theName, self)
            self.trainedModels[theName].fitModels()
        return

    def prepProjectByBatch(self):
        """
        Purpose:

        Call:

        Example:

        """
        for tableName in self.batchTablesList:
            if tableName in self.preppedTablesDF:
                self.preppedData[tableName] = prepData(tableName, self)
        return

    def trainProjectByBatch(self):
        """
        Purpose:

        Call:

        Example:

        """
        for tableName in self.batchTablesList:
            if tableName in self.preppedTablesDF:
                self.trainedModels[tableName] = tm.trainModels(tableName, self)
                self.trainedModels[tableName].fitModels()
        return

    def exportBestModel(self, filename, tableName=None):
        """
        Purpose:

        Call:

        Example:

        """
        if tableName is not None:
            theName = tableName
        else:
            theName = self.defaultPreppedTableName
        predict = predictProject(self, theName, self.bestModelName)
        predict.exportPredictClass(filename)

    def createPredictFromBestModel(self, tableName=None):
        """
        Purpose:

        Call:

        Example:

        """
        if tableName is not None:
            theName = tableName
        else:
            theName = self.defaultPreppedTableName
        mlUtility.runLog(
            'Running Predict for Model {}'.format(self.bestModelName))
        return predictProject(self, theName, self.bestModelName)

    def createPredictFromNamedModel(self, namedModel, tableName=None):
        """
        Purpose:

        Call:

        Example:

        """
        if tableName is not None:
            theName = tableName
        else:
            theName = self.defaultPreppedTableName
        mlUtility.runLog('Running Predict for Model {}'.format(tableName))
        return predictProject(self, theName, tableName)

    def exportNamedModel(self, namedModel, filename, tableName=None):
        """
        Purpose:

        Call:

        Example:

        """
        if tableName is not None:
            theName = tableName
        else:
            theName = self.defaultPreppedTableName

        predict = predictProject(self, theName, namedModel)
        predict.exportPredictClass(filename)

    def addManualRuleForTableName(self, tableName, functionName,
                                  columnName, value, forPredict=True):
        """
        Purpose:

        Call:

        Example:

        """
        if tableName in self.preppedTablesDF:
            df = self.preppedTablesDF[tableName]
            self.cleaningRules[tableName].addManualRule(
                functionName, columnName, value, df, forPredict)

    def addManualRuleForDefault(self, functionName, columnName=None,
                                value=None, forPredict=True):
        """
        Purpose:

        Call:

        Example:

        """
        if self.defaultPreppedTableName in self.preppedTablesDF:
            df = self.preppedTablesDF[self.defaultPreppedTableName]
            self.cleaningRules[self.defaultPreppedTableName].addManualRule(
                functionName, columnName, value, df, forPredict)

    def setGoals(self, goals):
        """
        Purpose:

        Call:

        Example:
                project.setGoals({'AUROC':(0.70,'>'),'Precision':(0.386,'>'),
                                'fbeta':(0.44,'>')})
        """
        self.goalsToReach = goals
        return

    def setOngoingReporting(self, flag, fileName):
        """
        project.setOngoingReporting(True,'Loan Data')

        """
        self.ongoingReporting = flag
        self.ongoingReportingFilename = fileName
        return

    def displayAllScores(self, fileName, short=False):
        """

         project.displayAllScores('Loan Data')

         def displayAllScores(self, fileName):

        """

        scores = {}

        mlUtility.runLog('\nReport on file: {}'.format(fileName))
        model = self.trainedModels[fileName]

        cols = ['Model'] + model.shortModelScoresColumns
        if self.setGoals is not None:
            cols += ['Goals']

        lst = []
        for r in model.modelScores:
            row = model.modelScores[r]

            # Round Values
            for c in row:
                if row[c] is not None:
                    if isinstance(row[c], float):
                        row[c] = round(row[c], 3)

            row['Model'] = r

            # Test for goals
            listGoals = ''
            if self.goalsToReach is not None:
                for goal in self.goalsToReach:
                    if goal in row:
                        if row[goal] is not None:
                            val, operand = self.goalsToReach[goal]
                            if operand == '>':
                                if row[goal] > val:
                                    listGoals += '{}:{:5.3f}>{:5.3f} '.format(
                                        goal, row[goal], val)
                            elif operand == '<':
                                if row[goal] < val:
                                    listGoals += '{}:{:5.3f}<{:5.3f} '.format(
                                        goal, model.row[goal], val)
                            elif operand == '=':
                                if (row[goal]+.05 <= val) and\
                                   (row[goal]-.05 >= val):
                                    listGoals += '{}:{:5.3f}={:5.3f} '.format(
                                            goal, model.row[goal], val)

            lst.append(row)
            if len(listGoals) > 0:
                goalRow = {}
                goalRow['Model'] = 'Goals:' + listGoals
                lst.append(goalRow)

        scores['columns'] = cols
        scores['models'] = lst

        mlUtility.printAsTable(lst, columns=cols, toTerminal=(not short))

        # Message the goals
        msg = '    ** Project Goals: '
        if self.goalsToReach is not None:
            for goal in self.goalsToReach:
                val, operand = self.goalsToReach[goal]
                msg += '{} {} {:5.3f}, '.format(goal, operand, val)

        mlUtility.runLog(msg, toTerminal=short)

        if not short:
            mlUtility.runLog('\n')
            mlUtility.runLog('   Confusion           Predicted')
            mlUtility.runLog('   Matrix:       Negative    Positive')
            mlUtility.runLog('              +-----------+-----------+')
            mlUtility.runLog('   Actual Neg | True Neg  | False Pos | ')
            mlUtility.runLog(
                '   Actual Pos | False Neg | True Pos  |<--Recall = ' +
                'True Pos / (True Pos + False Neg)')
            mlUtility.runLog(
                '              +-----------+-----------+          = ' +
                'How many true were actually true')
            mlUtility.runLog(
                '                                ^ Precision = True Pos' +
                ' / (False Pos + True Pos) ')
            mlUtility.runLog(
                '                                          = How many did ' +
                'we predict correctly\n\n')
            mlUtility.runLog(
                '   Accuracy = how many out of the total did we predict ' +
                'correctly')
            mlUtility.runLog(
                '   F1 Score  = 2 * (Precision * recall) / (Precision + ' +
                'recall)  (1.0 is perfect precision and recall)')
            mlUtility.runLog(
                '   f-Beta = F1 score factored 1=best, 0=worst. β<1 favors' +
                ' precision, β>1 favors recall. β->0 only precision,' +
                ' β->inf only recall')
            mlUtility.runLog(
                '   MSE (Mean squared error) - distance from the fit line ' +
                '(Smaller the value better the fit)')
            mlUtility.runLog(
                '   R2 Compare model to simple model. Ratio of errors of' +
                ' MSE/Simple Model.  Score close to 1=Good, 0=Bad')
            mlUtility.runLog(
                '   AUROC area under curve of true positives to false ' +
                'positives. Closer to 1 is better')

        return scores

    def reportResultsOnTrainedModel(self, fileName, modelName):
        """
        Purpose:

        Call:

        Example:

        """
        mlUtility.runLog('\nReport on model: '+modelName)

        model = self.trainedModels[fileName].fittedModels[modelName]
        scores = self.trainedModels[fileName].modelScores[modelName]

        if scores['roc_curve'] is not None:
            fpr, tpr, threshold = scores['roc_curve']
        else:
            fpr, tpr, threshold = None, None
        confusionMatrix = scores['CM']

        for s in self.trainedModels[fileName].shortModelScoresColumns:
            mlUtility.runLog('  {} = {}'.format(s, scores[s]))
        mlUtility.runLog('  Confusion Matrix = {}\n  DataShape = {}\n'.format(
            confusionMatrix, self.preppedTablesDF[fileName].shape))

        mlUtility.runLog('\nModel details:\n')
        mlUtility.runLog(model)

        if hasattr(model, 'best_params_'):
            mlUtility.runLog('\nModel Best Params:\n')
            mlUtility.runLog(model.best_params_)
        mlUtility.runLog(
            '\n\nHyperparamaters: ',
            self.trainedModels[fileName].hyperparameters[modelName])

        if fpr is not None:

            fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 6))

            ax[0].plot(threshold, tpr + (1 - fpr))
            ax[0].set_xlabel('Threshold')
            ax[0].set_ylabel('Sensitivity + Specificity')

            ax[1].plot(threshold, tpr, label="tpr")
            ax[1].plot(threshold, 1 - fpr, label="1 - fpr")
            ax[1].legend()
            ax[1].set_xlabel('Threshold')
            ax[1].set_ylabel('True Positive & False Positive Rates')
            plt.show()

            function = tpr + (1 - fpr)
            index = np.argmax(function)

            optimalThreshold = threshold[np.argmax(function)]
            mlUtility.runLog('Optimal Threshold:', optimalThreshold)
            mlUtility.runLog()
            mlUtility.runLog()

            plt.title('Receiver Operating Characteristic')
            plt.plot(fpr, tpr, 'b', label='AUC = %0.2f' % scores['AUROC'])
            plt.legend(loc='lower right')
            plt.plot([0, 1], [0, 1], 'r--')
            plt.xlim([0, 1])
            plt.ylim([0, 1])
            plt.ylabel('True Positive Rate')
            plt.xlabel('False Positive Rate')
            plt.show()

        return

        self.showFeatureImportances(fileName, modelName)

        if confusionMatrix is not None:
            # Plot non-normalized confusion matrix

            if self.confusionMatrixLabels is not None:
                classes = []
                for val, desc in self.confusionMatrixLabels:
                    classes.append('{}({})'.format(desc, val))

                plt.figure()
                plot_confusion_matrix(
                    confusionMatrix,
                    classes=classes,
                    normalize=False,
                    title='Confusion matrix, without normalization')
                plt.show()

                # Plot normalized confusion matrix
                # plt.figure()
                # plot_confusion_matrix(confusionMatrix, classes=classes,
                #                  normalize=True,
                #                  title='Normalized confusion matrix')

    def showFeatureImportances(self, fileName, modelName):
        """
        Purpose:

        Call:

        Example:

        """
        if fileName is not None:
            theName = fileName
        else:
            theName = self.defaultPreppedTableName
        if modelName in self.modelList:
            scores = self.trainedModels[fileName].modelScores[modelName]
            if scores['FI'] is not None:
                print('\nFeatures Importance for ', modelName)
                (pd.Series(scores['FI'], index=self.dataColumns)
                 .nlargest(self.featuresToReport).plot(kind='barh',
                 figsize=(8, 6), title='Features for '+modelName))
                plt.show()
            elif scores['COEF'] is not None:
                # The estimated coefficients will all be around 1:
                print(
                    '\nFeature Importance Using Estimated coefficients for ',
                    modelName)
                (pd.Series(scores['COEF'], index=self.dataColumns)
                 .nlargest(self.featuresToReport).plot(kind='barh',
                 figsize=(8, 6), title='Coefficients for '+modelName))
                plt.show()
            else:
                mlUtility.runLog(
                    'The model,{}, was not found'.format(modelName))
                return
        else:
            mlUtility.runLog('The model,{}, was not found'.format(modelName))

    def logTrainingResultsRunDescription(self, description='None'):
        """
        Purpose:

        Call:

        Example:

        """
        self.logDescription = description

    def logTrainingResults(self, fileName,
                           outputFileName, inputModelName=None):
        """
        Purpose:

        Call:

        Example:

        """
        # mlUtility. traceLog(('\nLogging Results: ')

        if len(outputFileName) == 0:
            return

        results = []

        modelNames = {'gbc': 'gradientboostingclassifier__',
                      'l1': 'logisticregression__',
                      'l2': 'logisticregression__',
                      'rfc': 'randomforestclassifier__',
                      'bagging': 'baggingclassifier__',
                      'adaboost': 'adaboostclassifier__',
                      'gaussiannb': 'gaussiannb__',
                      'decisiontree': 'decisiontreeclassifier__',
                      'kneighbors': 'kneighborsclassifier__',
                      'sgd': 'sgdclassifier__',
                      'lasso': 'lasso__',
                      'ridge': 'ridge__',
                      'enet': 'elasticnet__',
                      'rf': 'randomforestregressor__',
                      'gb': 'gradientboostingregressor__',
                      'dtr': 'decisiontreeregressor__',
                      'kmeans': 'kmeansclusters__',
                      'xgbc': 'xgbclassifier__',
                      'stack': 'stackingclassifier__',
                      'etc': 'extratreesclassifier__',
                      'vote': 'votingclassifier__',
                      'svc': 'svc__'
                      }

        hyperparametersToReport = ['loss', 'max_depth', 'learning_rate',
                                   'C', 'max_iter',
                                   'solver', 'max_features',
                                   'n_estimators', 'max_samples',
                                   'algorithm', 'penalty', 'tol',
                                   'var_smoothing',
                                   'min_samples_split',
                                   'min_samples_leaf', 'subsample',
                                   'validation_fraction',
                                   'n_iter_no_change',
                                   'criterion', 'splitter', 'alpha',
                                   'n_neighbors', 'leaf_size',
                                   'p', 'voting']

        scoresToReport = ['AUROC', 'fbeta', 'Recall',
                          'Precision', 'RunTime', 'f1',
                          'Accuracy', 'MAE', 'r2']

        header = 'Model, Description'
        for report in scoresToReport:
            header += ', {}'.format(report)
        for param in hyperparametersToReport:
            header += ', {}'.format(param)
        header += ', runParams, BestParams, Date, Time'
        # mlUtility. traceLog(('\n')
        # mlUtility. traceLog((header)
        header += '\n'

        # Check is the file exists and than open for write or append
        myFile = Path(outputFileName)
        if myFile.is_file():
            file = open(outputFileName, 'a')
        else:
            file = open(outputFileName, 'w')
            file.write(header)

        # Determine if the model is to report on all or just part.
        if inputModelName is None:
            modelListToProcess = self.modelListAsRun
        else:
            modelListToProcess = [inputModelName]

        for modelName in modelListToProcess:

            model = self.trainedModels[fileName].fittedModels[modelName]
            scores = self.trainedModels[fileName].modelScores[modelName]

            row = '{},"{}"'.format(modelName, self.logDescription)
            for report in scoresToReport:
                if scores[report] is None:
                    row += ', None'
                else:
                    row += ', {:5.3f}'.format(scores[report])

            for param in hyperparametersToReport:
                lookup = modelNames[mlUtility.getFirst(modelName)]+param
                # mlUtility. traceLog(('lookup=',lookup)
                if lookup in model.best_params_:
                    row += ', {}'.format(model.best_params_[lookup])
                else:
                    if param in model.best_params_:
                        row += ', {}'.format(model.best_params_[param])
                    else:
                        row += ','

            hp = self.trainedModels[fileName].hyperparameters[modelName]
            hpStr = '{'
            for h in hp:
                hpStr += '{}: {},'.format(h, hp[h])
            hpStr += '}'

            row += ',"{}","{}",{}, {}'.format(
                hpStr, model.best_params_, self.runStartTime,
                datetime.datetime.now())
            # mlUtility. traceLog((row)
            row += '\n'
            file.write(row)

        file.close()
        # mlUtility. traceLog(('\n')
        # for x in model.best_params_ :
        #    mlUtility.runLog (x)


class predictProject (object):
    """
        Purpose: predictProject

        Call:

        Example:

    """

    def __init__(self, project, tableName=None, namedModel=None):
        self.name = project.name
        self.description = project.description
        self.modelType = project.modelType
        self.cleaningRules = None
        self.predictFile = None
        self.predictDataDF = None
        self.predictSet = None
        self.readyToRun = False
        self.useProbaForPredict = project.useProbaForPredict
        self.useStandardScaler = project.useStandardScaler

        if tableName is not None:
            if tableName in project.preppedTablesDF:
                theName = tableName
            else:
                theName = project.defaultPreppedTableName
        else:
            theName = project.defaultPreppedTableName

        if namedModel:
            name = namedModel
        else:
            name = project.bestModelName

        theTrainedModel = project.trainedModels[theName]
        if theName in project.cleaningRules:
            self.cleaningRules = project.cleaningRules[theName]

        if name in theTrainedModel.fittedModels:
            self.modelName = name
            self.modelScore = theTrainedModel.modelScores[name]
            if self.modelType == tm.TRAIN_CLUSTERING:
                self.model = theTrainedModel.fittedModels[name]
            else:
                self.model = theTrainedModel.fittedModels[name]\
                    .best_estimator_
        else:
            mlUtility.raiseError('project name,{}, not found'.format(name))

    def importPredictFile(self, name, type=None, description=None,
                          location=None, fileName=None, sheetName=None,
                          hasHeaders=False, range=None):
        """
        Purpose:

        Call:

        Example:

        """
        self.predictFile = getData(name,
                                   type=type,
                                   description=description,
                                   location=location,
                                   fileName=fileName,
                                   sheetName=sheetName,
                                   range=range,
                                   hasHeaders=hasHeaders)
        self.predictDataDF = self.predictFile.openTable()

    def importPredictFileFromProject(self, project, tableName):
        """
        Purpose:

        Call:

        Example:

        """
        if tableName in project.preppedTablesDF:
            self.predictDataDF = project.preppedTablesDF[tableName]

    def importPredictFromDF(self, df, readyForPredict=False):
        """
        Purpose:

        Call:

        Example:

        """
        if readyForPredict:
            self.predictSet = df.reset_index(drop=True)
            self.readyToRun = True
            mlUtility.runLog('Prepped Predict data from DataFrame')
        else:
            self.predictDataDF = df

    def prepPredict(self):
        """
        Purpose:

        Call:

        Example:

        """
        if self.readyToRun:
            pass
        else:
            prep = prepPredictData(self)
            self.predictSet = prep.getPredictSet()
            self.readyToRun = True

    def exportPreppedFile(self, filename, columnName=None,
                          columnData=None, columnName2=None,
                          columnData2=None):
        """
        Purpose:

        Call:

        Example:

        """
        if self.predictSet is not None:
            if columnName is not None and columnData is not None:
                temp = self.predictSet.copy(deep=True)
                temp[columnName] = columnData

                if columnName2 is not None and columnData2 is not None:
                    temp[columnName2] = columnData2
                mlUtility.runLog('Writing prepped file {}'.format(filename))
                temp.to_csv(filename, index=False)
            else:
                self.predictSet.to_csv(filename, index=False)

    def getColumn(self, columnName):
        """
        Purpose: Get a columns from the data file

        Call: def getColumn(self, column):

        Example: prdict.getColumn('Name')

        """
        if self.predictDataDF is not None:
            if columnName in self.predictDataDF:
                return self.predictDataDF[columnName]
        elif self.predictSet is not None:
            if columnName in self.predictSet:
                return self.predictSet[columnName]
        return None

    def exportPredictClass(self, filename):
        """
        Purpose:

        Call:

        Example:

        """
        with open(filename, 'wb') as f:
            pk.dump(self, f)

    def addToPredictFile(self, columnName, columnData):
        """
        Purpose:

        Call:

        Example:

        """
        if self.predictDataDF is not None:
            self.predictDataDF[columnName] = columnData
        elif self.predictSet is not None:
            self.predictSet[columnName] = columnData
        return None

    def removeFromPredictFile(self, columns):
        """
        Purpose:

        Call:

        Example:

        """
        if self.predictDataDF is not None:
            pred = self.predictDataDF
        elif self.predictSet is not None:
            pred = self.predictSet
        if pred is None:
            mlUtility.errorLog('No Predict File')
            return
        if type(columns) is not list:
            if columns in pred:
                pred.drop(columns, axis=1, inplace=True)
            else:
                mlUtility.errorLog('Columns {} not found to drop'.format(name))
        else:
            for name in columns:
                if name in pred:
                    pred.drop(name, axis=1, inplace=True)
                else:
                    mlUtility.errorLog(
                        'Columns {} not found to drop'.format(name))
        return None

    def keepFromPredictFile(self, columns):
        """
        Purpose:

        Call:

        Example:

        """
        logData = ''
        if self.predictDataDF is not None:
            pred = self.predictDataDF
        elif self.predictSet is not None:
            pred = self.predictSet
        if pred is None:
            mlUtility.errorLog('No Predict File')
            return
        if type(columns) is not list:
            for name in pred:
                if name == columns:
                    pass
                else:
                    pred.drop(name, axis=1, inplace=True)
                    logData += name + ', '
        else:
            for name in pred:
                if name in columns:
                    pass
                else:
                    pred.drop(name, axis=1, inplace=True)
                    logData += name + ', '
        mlUtility.runLog('Columns {} dropped'.format(logData))
        return None

    def exportPredictFile(self, filename):
        """
        Purpose:

        Call:

        Example:

        """
        if self.predictDataDF is not None:
            pred = self.predictDataDF
        elif self.predictSet is not None:
            pred = self.predictSet
        if pred is None:
            mlUtility.errorLog('No Predict File to Export')
            return

        mlUtility.runLog('Writing predict file {}'.format(filename))
        pred.to_csv(filename, index=False)

    def getPredictFileDF(self):
        """
        Purpose: Return a datraframe of the predict file.

        Call:

        Example:

        """
        pred = None
        if self.predictDataDF is not None:
            pred = self.predictDataDF
        elif self.predictSet is not None:
            pred = self.predictSet
        return pred

    @ignore_warnings(category=ConvergenceWarning)
    @ignore_warnings(category=DataConversionWarning)
    def runPredict(self):
        """
        Purpose:

        Call:

        Example:

        """

        probaOK = hasattr(self.model, 'predict_proba') and callable(
            getattr(self.model, 'predict_proba'))
        try:
            if self.readyToRun:
                if self.useProbaForPredict and probaOK:
                    # This only works on binary for no
                    if self.useStandardScaler:
                        mlUtility.runLog('Using Standard Scaler')
                        pred = self.model.predict_proba(
                            StandardScaler().fit_transform(self.predictSet))
                    else:
                        p = self.model.predict_proba(self.predictSet)
                        pred = [x[1] for x in p]
                else:
                    if self.useStandardScaler:
                        mlUtility.runLog('Using Standard Scaler')
                        pred = self.model.predict(
                            StandardScaler().fit_transform(self.predictSet))
                    else:
                        pred = self.model.predict(self.predictSet)
                return pred
            return None

        except NotFittedError as e:
            mlUtility.runLog(repr(e))


def loadPredictProject(filename):
    """
    Purpose:

    Call:

    Example:

    """
    with open(filename, 'rb') as f:
        return pk.load(f)


#
# https://scikit-learn.org/stable/auto_examples/model_selection/
#         plot_confusion_matrix.html
#
def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
        Purpose:

        Call:

        Example:

    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        # cm = cm.astype('float')/cm.sum(axis=0)
        # mlUtility. traceLog(("Normalized confusion matrix")
    else:
        # mlUtility. traceLog(('Confusion matrix, without normalization')
        pass

    # mlUtility.runLog (cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()


def makeStack(classifier, list, alias=None):
    """
        Purpose:

        Call:

        Example:

    """
    stacker = []
    stack = classifier
    if list is not None:
        for x in list:
            name = mlUtility.getFirst(x)
            stacker.append(x)
            stack += ':' + x
    if alias is not None:
        stacker.append(stack+'#'+alias)
    else:
        stacker.append(stack)
    return stacker
