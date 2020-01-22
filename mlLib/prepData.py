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
# 
from __future__ import print_function 
from __future__ import division
import pandas as pd
import numpy as np
# Function for splitting training and test set
from sklearn.model_selection import train_test_split

from .cleanData import cleanData, cleaningRules
import mlLib.trainModels as tm
import mlLib.mlUtility as mlUtility


pd.set_option('display.max_columns', 100)
pd.set_option('display.float_format', lambda x: '%.6f' % x)


# Isolate data types that you want to highlight
# create an indicator variable 


class prepData(object):

    def __init__ (self, name, project, outFile=None):

        if name not in project.preppedTablesDF:
            mlUtility.raiseError('table not found')
            return None

        df = project.preppedTablesDF[name]
        self.tableName = name
        self.X = None
        self.y = None
        self.project = project


        # only to datapred for modelTypes with target variables
        if project.modelType != tm.TRAIN_CLUSTERING:
        
            # First Check if the targetVariable needs dummies
            if  df[project.targetVariable[name]].dtype=='object':
                targetValue = 'Object Error'
                if project.targetVariableIsBoolean[name]:
                    df[project.targetVariable[name]] =  (df[project.targetVariable[name]]==
                                                     project.targetVariableTrueValue[name]).astype(int)
                    targetValue = 'Boolean'
                elif project.targetVariableConvertValues[name] is not None:
                    for fromValue, toValue in project.targetVariableConvertValues[name]:
                        df[project.targetVariable[name]].replace(fromValue, toValue, inplace=True)
                    df[project.targetVariable[name]] = df[project.targetVariable[name]].astype(int)
                    targetValue = 'Integer'
                mlUtility.runLog( 'Converting target Variable {} for {}'.format(project.targetVariable[name],targetValue))
 
   
        
            #Create new dataframe with dummy features
            col = [x for x in df.dtypes[(df.dtypes=='object')].index] + [x for x in df.dtypes[(df.dtypes=='category')].index]
            
            # Remove target variable from hot encoding
            if project.targetVariable[name] in col:
                col = [x for x in col if x != project.targetVariable[name]]
            
            
            self.X = pd.get_dummies(df, columns=col)
            
            # File is engineered, now do stuf before training
            
            self.removeTestingFileInX(project,project.targetVariable[name])
            
            if outFile is not None:
                self.X.to_csv(outFile, index=False)
                mlUtility.runLog( 'Writing prepped training File {}'.format(outFile))
            

        
            # Create separate object for input features
            self.y = self.X[project.targetVariable[name]]

       
            # Create separate object for target variable
            self.X.drop(project.targetVariable[name], axis = 1, inplace=True)
            project.dataColumns = self.X.columns
                                      
                
        
        # Split X and y into train and test sets
        #mlUtility. traceLog(("project.testSize, random_state=project.randomState = ", project.testSize, project.randomState)
        if project.modelType==tm.TRAIN_CLASSIFICATION:
            if project.testSize==0:
                self.X_train = self.X
                self.y_train = self.y
                self.X_test = None
                self.y_test = None
            else:
                 self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y,
                              test_size=project.testSize, random_state=project.randomState, stratify=self.y)
        elif project.modelType == tm.TRAIN_CLUSTERING:
            #Create new dataframe with dummy features
            col = [x for x in df.dtypes[(df.dtypes=='object')].index] + [x for x in df.dtypes[(df.dtypes=='category')].index]
            self.X = pd.get_dummies(df, columns=col)
            
            self.removeTestingFileInX(project, None)

            self.X_train = self.X
            self.X_test, self.y_train, self.y_test = None, None, None
        else:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=project.testSize,
                         random_state=project.randomState)

        # Do scalars
        return 
            
    
    def getTrainingSet (self):
        return self.X_train, self.X_test, self.y_train, self.y_test
     
     
#        self.mergedTrainingAndTest = False
#        self.mergedTrainingAndTestFileName = None
#            if self.mergedTrainingAndTestFileName in self.preppedTablesDF:
#                return (self.preppedTablesDF[self.mergedTrainingAndTestFileName])
# self.isTrainingSet, 
#    def execute(self, df, project,cleaningRules=None):
#        if project.mergedTrainingAndTest:
#            mask = (df[self.name] <= self.value) & df[project.isTrainingSet]
##        else:
#            mask = (df[self.name] <= self.value)
#            
#        df.drop(df[mask].index, inplace=True)
#        return None



    def removeTestingFileInX(self, project, targetVariable):
        if project.mergedTrainingAndTest:
            if project.mergedTrainingAndTestFileName in project.preppedTablesDF:
                testingMask =  self.X[project.isTrainingSet]==False
                self.X.drop(project.isTrainingSet, axis=1, inplace=True)
                
                project.preppedTablesDF[project.mergedTrainingAndTestFileName] = self.X.loc[self.X[testingMask].index]
                
                if targetVariable is not None:
                    project.preppedTablesDF[project.mergedTrainingAndTestFileName].drop(targetVariable, axis=1, inplace=True)
                
                self.X.drop(self.X[testingMask].index, inplace=True)



class prepPredictData(object):

    def __init__ (self, project):
        
        
        # run the cleaning rules:
        cleanData(project.predictDataDF, project.cleaningRules, isPredict=True)

        #Create new dataframe with dummy features
        df = project.predictDataDF
        col = [x for x in df.dtypes[(df.dtypes=='object')].index] + [x for x in df.dtypes[(df.dtypes=='category')].index]
         
        self.predict = pd.get_dummies(df, columns=col)
        
        self.predict.fillna(0, inplace=True)

        #for xxx in self.predict.columns:
        #    mlUtility.runLog ('Predict Columns', xxx)
              
        return 
    
    def getPredictSet (self):
        return self.predict
     

