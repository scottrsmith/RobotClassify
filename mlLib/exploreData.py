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

# NumPy for numerical computing
import numpy as np

# Pandas for DataFrames
import pandas as pd


# Libs to convert images for web display
import io
import base64

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


# Matplotlib for visualization
from matplotlib import pyplot as plt

# display plots in the notebook
#%matplotlib inline 

# Seaborn for easier visualization
import seaborn as sns
import mlLib.mlUtility as mlUtility
from mlLib.cleanData import *

#from sklearn.feature_selection import VarianceThreshold

from sklearn.ensemble import ExtraTreesClassifier
from sklearn.feature_selection import SelectFromModel
#from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer




"""

Explore the data - what decisions have to be made to get ready for the clean"

1. What columns have null data
2. what columns have duplicates
3. What columns are binary data
4. what categores need:
   - to fix capitalization
   - to regroup / combine
    
5. What columns need outliers dropped

6. what columns have missing features

"""


def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png',
                bbox_inches='tight')
    img.seek(0)
    return base64.b64encode(img.getvalue())
 

def is_outlier(points, thresh=3.5):
    """
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    """
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh   



# from http://eurekastatistics.com/using-the-median-absolute-deviation-to-find-outliers/
def doubleMADsfromMedian(y,thresh=3.5):
    # warning: this function does not check for NAs
    # nor does it address issues when 
    # more than 50% of your data have identical values
    try:
        m = np.median(y)
        abs_dev = np.abs(y - m)
        left_mad = np.median(abs_dev[y <= m])
        right_mad = np.median(abs_dev[y >= m])
        y_mad = left_mad * np.ones(len(y))
        y_mad[y > m] = right_mad
       
        modified_z_score = 0.6745 * abs_dev / y_mad
        #    modified_z_score = abs_dev / y_mad
        modified_z_score[y == m] = 0
        return modified_z_score > thresh
        
        
    except Exception as e:
        raise e
    except RuntimeWarning:
        return []
   

    
def getHistogram(series):
    hist = {}
    for value in series:
        if value in hist:
            hist[value] += 1
        else:
            hist[value]  = 1
    return hist


def getStats (series):
    
    s = series.describe()  
    stats = {}
    
    # Stats for all
    stats['count'] = s['count']
    if hasattr(series, 'cat'):
        stats['dataType'] = 'category'
    else:
        stats['dataType'] = series.dtype
    #mlUtility.runLog('dtype={}'.format(series.dtype))
    
    # Null Count
    stats['nullCount'] = series.isnull().sum()
    
    
    stats['mean'] = None
    stats['median'] = None
    stats['std'] = None 
    stats['min'] = None
    stats['1%'] = None
    stats['2.5%'] = None
    stats['5%'] = None
    stats['25%'] = None
    stats['50%'] = None
    stats['75%'] = None
    stats['97.5%'] = None
    stats['95%'] = None
    stats['99%'] = None
    stats['max'] = None        
    stats['first'] = None
    stats['last']  = None  
    stats['top'] = None
    stats['freq'] = None
   
    
 
    stats['histogram'] = getHistogram(series)
    # Status for Objects
    if series.dtype == 'object':
        stats['unique'] = s['unique']
        stats['top'] = s['top']
        stats['freq'] = s['freq']

    elif hasattr(series,'cat'):
        stats['unique'] = s['unique']
        stats['top'] = s['top']
        stats['freq'] = s['freq']
        
    # stats for dates
#    elif hasattr(series, 'datetime'):
    elif series.dtype == 'datetime64[ns]':
        stats['unique'] = s['unique']
        stats['top'] = s['top']       
        stats['freq'] = s['freq']      
        stats['first'] = s['first']    
        stats['last'] = s['last']    

    elif series.dtype == 'bool':
        stats['unique'] = s['unique']
        stats['unique'] = len(series.unique())


    else:
        # Status for numbers
        stats['mean'] = s['mean']
        stats['median'] = np.median(series)
        stats['std'] = s['std'] 
        stats['min'] = s['min']
        stats['25%'] = s['25%']
        stats['50%'] = s['50%']
        stats['75%'] = s['75%']
        stats['max'] = s['max']        
        q = series.quantile([.01, 0.025, 0.05, 0.95, 0.975, 0.99])
        stats['1%'], stats['2.5%'], stats['5%'], stats['95%'], stats['97.5%'], stats['99%'] = q[0.01], q[0.025], q[0.05], q[0.95], q[0.975], q[0.99] 
         
        stats['unique'] = len(series.unique())
        stats['top'] = None
        stats['freq'] = 0
        hist = stats['histogram']
        for value in hist:
            if hist[value] >= stats['freq']:
                stats['freq'] = hist[value]
                stats['top'] = value
         
   
    # test for Binary
    if stats['unique'] == 2 and series.dtype != 'object':
        stats['binary']=True
    else:
        stats['binary']=False
#    print ('\n\nStats')
#    print (stats)

#    print ('\n\ns')
#    print (s)


    return stats
    


def runExploreTest(function, project, explore, df, dfCopy, colName, stats):
    rules, dropped, cleanFunctions = function(project, explore, df, dfCopy, colName, stats)
    #mlUtility.runLog(' After Function {}\n'.format(df))
    
    if len(rules) > 0:
        #mlUtility.runLog('Column, {}, running function {}'.format(colName, function))
        # Run the Rules for the column     
        for r in cleanFunctions:
            #mlUtility.runLog ('   -running clean function={}'.format(r))
            r.execute(df, project, None) 
        if function in newColumnTests:
            for x in getOneHotEncodeColumns(colName, df.columns.tolist()):
                dfCopy[x] = df[x]
     
        elif not dropped:
            dfCopy[colName] = df[colName]
        
    return rules, dropped

   
    



def testTextSignificance(project, explore, df, dfCopy, name, stats):
    rules = {}
    cleanFunction = []
    dropped = False

    vectorizer = TfidfVectorizer()
    #print (df[name])
    X = vectorizer.fit_transform(df[name])
    if X.shape[1]<=stats['unique']:
        return {},[],False
    wc = np.asarray(X.mean(axis=0))
    d={}
    for w,c in zip(vectorizer.get_feature_names(),wc[0]):
        d[w]=c
    
    top = []
    sig = .01
    for topVals,c in sorted(d.items(), key=lambda item: item[1], reverse=True):
        if c < sig:
            break
        top.append((topVals,None))
    if len(top)<=1:
        return {},[],False
        
    # now that we have the list of top words, we need to rebucket
    #project.addManualRuleForDefault(ed.CLEANDATA_REBUCKET_BY_INCLUDE, 'Name',  rebucket)
    explore.addExploreRules(rules, name , CLEANDATA_REBUCKET_BY_INCLUDE, value=top, key=None)
    cleanFunction.append(explore.getRuleFunction(CLEANDATA_REBUCKET_BY_INCLUDE, name, value=top , df=df, forPredict=True))

    #project.addManualRuleForDefault(ed.CLEANDATA_SET_CATEGORY_DATATYPE, 'Name',None)
    explore.addExploreRules(rules, name , CLEANDATA_REFACTOR_DATA, 'factorize')
    cleanFunction.append(explore.getRuleFunction(CLEANDATA_REFACTOR_DATA, name, 'factorize'))
    #print ('name=',name)
    #print ('new values=',top)
    #print ('df=',df[name])
    return rules, dropped, cleanFunction




def testIDField(project, explore, df, dfCopy, name, stats):
    rules = {}
    cleanFunction = []
    dropped = False
    # Do the tests
    if stats['unique'] >= stats['count'] * .90:
        # Add tge ryes
        # this is an ID field of uniqie values, needs to be dropped
        # addRecommendation ( name, explore, value=None, key=None):
        explore.addExploreRules(rules, name , CLEANDATA_DROP_ID_FIELD, value=name, key=None)

        # explore.getRuleFunction(functionName, columnName, value , df=None, forPredict=True):
        cleanFunction.append(explore.getRuleFunction(CLEANDATA_DROP_ID_FIELD, name, value=name , df=df, forPredict=True))
        dropped = True
    return rules, dropped, cleanFunction



def testRebucket(project, explore, df, dfCopy, name, stats):
    rules = {}
    cleanFunction = []
    other = []
    dropped = False
    items = ''
    # Do the tests
    histogram = stats['histogram']
    if stats['unique'] <= project.uniqueThreshold:
        for item, value in histogram.items():
            if value < project.smallSample:
                # addRecommendation ( name, explore, value=None, key=None):
                # explore.getRuleFunction(functionName, columnName, value , df=None, forPredict=True):           
                other.append(item)
                items += str(item)

        # use rebuckets for other - Need at least two
        if len(other)>1:
            explore.addExploreRules(rules, name , CLEANDATA_REBUCKET, value=other, key=str(items))
            cleanFunction.append(explore.getRuleFunction(CLEANDATA_REBUCKET, name, value=[other,'Others'] , df=df, forPredict=True))
        
            #self.addRecommendation(name,CLEANDATA_CONVERT_CATEGORY_TO_INTEGER)
            explore.addExploreRules(rules, name , CLEANDATA_CONVERT_CATEGORY_TO_INTEGER)
            cleanFunction.append(explore.getRuleFunction(CLEANDATA_CONVERT_CATEGORY_TO_INTEGER, name))
                
    return rules, dropped, cleanFunction

def testDefaultFactorize(project, explore, df, dfCopy, name, stats):
    rules = {}
    cleanFunction = []
    dropped = False
    # Do the tests
    
    type = dfCopy.dtypes[name]                      
    if type == 'object' or hasattr(dfCopy[name], 'cat') or type == 'datetime64[ns]':
#        if stats['unique'] <= stats['count'] * .10:
#            # do nothing. can use one-hot encoding
#            if stats['nullCount'] > 0:
#                explore.addExploreRules(rules, name , CLEANDATA_MARK_MISSING)
#                cleanFunction.append(explore.getRuleFunction(CLEANDATA_MARK_MISSING, name))
#            explore.addExploreRules(rules, name , CLEANDATA_SET_CATEGORY_DATATYPE)
#            cleanFunction.append(explore.getRuleFunction(CLEANDATA_SET_CATEGORY_DATATYPE, name))
#        else:
        #dfCopy[name], _ = pd.factorize(dfCopy[name])
        #dfCopy[name] = dfCopy[name].astype('int64')
        explore.addExploreRules(rules, name , CLEANDATA_REFACTOR_DATA, 'factorize')
        cleanFunction.append(explore.getRuleFunction(CLEANDATA_REFACTOR_DATA, name, 'factorize'))
    return rules, dropped, cleanFunction



def testOneHotEncoding(project, explore, df, dfCopy, name, stats):
    rules = {}
    cleanFunction = []
    dropped = False
    # Do the tests
    
    if stats['nullCount'] > 0:
        explore.addExploreRules(rules, name , CLEANDATA_MARK_MISSING)
        cleanFunction.append(explore.getRuleFunction(CLEANDATA_MARK_MISSING, name))

    explore.addExploreRules(rules, name , CLEANDATA_SET_CATEGORY_DATATYPE)
    cleanFunction.append(explore.getRuleFunction(CLEANDATA_SET_CATEGORY_DATATYPE, name))
    explore.addExploreRules(rules, name , CLEANDATA_ONE_HOT_ENCODE)
    cleanFunction.append(explore.getRuleFunction(CLEANDATA_ONE_HOT_ENCODE, name))
    
    return rules, dropped, cleanFunction

      
  
def testCatgory(project, explore, df, dfCopy, name, stats):
    rules = {}
    cleanFunction = []
    dropped = False
    # Do the tests
    if stats['unique'] <= stats['count'] * .50:
        # Add tge ryes
        # this is an ID field of uniqie values, needs to be dropped
        #
        # addRecommendation ( name, explore, value=None, key=None):
        # explore.getRuleFunction(functionName, ColName, value , df=None, forPredict=True):
        explore.addExploreRules(rules, name , CLEANDATA_CONVERT_CATEGORY_TO_INTEGER)
        cleanFunction.append(explore.getRuleFunction(CLEANDATA_CONVERT_CATEGORY_TO_INTEGER, name))
    return rules, dropped, cleanFunction
 
 
def testZeroFill(project, explore, df, dfCopy, name, stats):
    rules = {}
    cleanFunction = []
    dropped = False
    # Do the tests
    if stats['nullCount'] > 0:
        if stats['binary']==True:
            explore.addExploreRules(rules, name , CLEANDATA_ZERO_FILL, value=None, key=None)
            cleanFunction.append(explore.getRuleFunction(CLEANDATA_ZERO_FILL, name, value=None , df=df, forPredict=True))
            
        else:
            explore.addExploreRules(rules, name , CLEANDATA_ZERO_FILL, value='mean', key=None)
            cleanFunction.append(explore.getRuleFunction(CLEANDATA_ZERO_FILL, name, value='mean' , df=df, forPredict=True))        
    return rules, dropped, cleanFunction


# with the total_series_size, 
#          number of uniqie values
#          and the precent of uniqie values
def checkForImbalanced (name, stats, series, isObject=False):

    
    uniqueValues = stats['unique']
    topPrecent = len(series) / stats['freq']
    topValue = stats['top']
   
    # test for unbalanced
               
    if uniqueValues==2 and topPrecent> .80:
        return True
               
    if uniqueValues==3 and topPrecent> .70:
        return True
        
    if uniqueValues==4 and topPrecent> .60:
        return True

    if uniqueValues>=5 and topPrecent> .50:
        return True
    return False


def testImbalanced(project, explore, df, dfCopy, name, stats):
    rules = {}
    cleanFunction = []
    dropped = False
    # Do the tests
    if checkForImbalanced(name, stats, df[name], isObject=False):
        explore.addExploreRules(rules, name , CLEANDATA_IMBALANCED_DATA, 
                                value='Top value {} with {}%'.format(stats['count']/stats['freq'], stats['top']*100.), key=None)
        cleanFunction.append(explore.getRuleFunction(CLEANDATA_IMBALANCED_DATA, name, value=None , df=df, forPredict=True))
        
    return rules, dropped, cleanFunction



def testSkewed(project, explore, df, dfCopy, name, stats):
    rules = {}
    cleanFunction = []
    dropped = False
    # Do the tests
    skew = df[name].skew()
    if skew > project.skewFactor:
        # Add tge ryes
        # this is an ID field of uniqie values, needs to be dropped
        #
        # addRecommendation ( name, explore, value=None, key=None):
        # explore.getRuleFunction(functionName, ColName, value , df=None, forPredict=True):
        explore.addExploreRules(rules, name , CLEANDATA_REFACTOR_DATA, value='skewed', key=None)
        cleanFunction.append(explore.getRuleFunction(CLEANDATA_REFACTOR_DATA, name, value='skewed' , df=df, forPredict=True))
    return rules, dropped, cleanFunction


def testForSparse(project, explore, df, dfCopy, name, stats):
    rules = {}
    cleanFunction = []
    dropped = False
    # Do the tests
    sparseScore = stats['nullCount'] / len(series)
    if sparseScore > .5:
        # Add tge ryes
        # this is an ID field of uniqie values, needs to be dropped
        #
        # addRecommendation ( name, explore, value=None, key=None):
        # explore.getRuleFunction(functionName, ColName, value , df=None, forPredict=True):
        explore.addExploreRules(rules, name , CLEANDATA_REFACTOR_DATA, value='sparse', key=None)
        cleanFunction.append(explore.getRuleFunction(CLEANDATA_REFACTOR_DATA, name, value='sparse' , df=df, forPredict=True))
        dropped = True
    return rules, dropped, cleanFunction

 

#columnTests = {'object': [ testIDField, testOneHotEncoding, testRebucket, testCatgory, testTextSignificance],
#                 'number': [testIDField, testZeroFill, testImbalanced, testSkewed],
#                 'bool': [testIDField],
#                 'date': [testIDField] 
#                }
columnTests = {'object': [ testOneHotEncoding, testRebucket, testCatgory, testIDField],
                 'number': [testIDField, testZeroFill, testImbalanced, testSkewed],
                 'bool': [testIDField],
                 'date': [testIDField] 
                }
                 
newColumnTests = [testOneHotEncoding] 


'''
def TEMPLATE(project, explore, df, dfCopy, name, stats):
    rules = {}
    cleanFunction = []
    dropped = False
    # Do the tests
    if TEST:
        # Add tge ryes
        # this is an ID field of uniqie values, needs to be dropped
        #
        # addRecommendation ( name, explore, value=None, key=None):
        # explore.getRuleFunction(functionName, ColName, value , df=None, forPredict=True):
        explore.addExploreRules(rules, name , CLEANDATA, value=None, key=None)
        cleanFunction.append(explore.getRuleFunction(CLEANDATA, name, value=None , df=df, forPredict=True))
        dropped = True
    return rules, dropped, cleanFunction
'''
   

class exploreData(object):
    
    def __init__(self, df, project, name):
        
       
        self.columns = {}
        self.recommendations = {}
        self.colsToDrop = []
        self.dataFrame = df
        self.project = project
        self.fileName = name
        #self.featureImportance = None
        #self.correlations = None
        if name in project.targetVariable:
            self.target = project.targetVariable[name]
        else:
            self.target = None
        self.topColumns = None
        self.correlations = None
        self.featureImportance = None
        
        
        # Init explore heatmap to zeros
        self.heatMap = pd.DataFrame(np.zeros([len(exploreHeatMap),len(df.columns)], dtype=float), index=exploreHeatMap, columns=df.columns)

        
        d  = np.zeros([len(exploreHeatMap),len(df.columns)], dtype=float)
        self.heatMap = pd.DataFrame(d, index=exploreHeatMap, columns=df.columns)
        
        if self.project.recommendOnly:
            self.featureRecommendations(project, name, df)
        elif self.project.basicAutoMethod:
            self.featureEvaluation(project, name, df)
        else:
            self.featureTesting(project, name, df)
        

    '''
    Feature Evalution does a basic conversation of string data for a brute-force test
            
                     
    '''
    def featureEvaluation(self, project, name, df, toWeb=False):
        mlUtility.runLog ('Basic Automethod. Evaluating correlations and feature importance\n')
        
        # make a copy of the data to do numerical evaluations
        dfCopy = df.copy()
        #dfCopy.to_csv('CorrFI-TestData-before.csv')
        #if self.target is not None:
        #    dfCopy[self.target].dropna()
        if project.isTrainingSet in dfCopy:
           dfCopy.drop(project.isTrainingSet, axis=1,  inplace=True)

        for name in dfCopy:
            type = dfCopy.dtypes[name]                      
            if type == 'object' or hasattr(dfCopy[name], 'cat'):
                dfCopy[name], _ = pd.factorize(dfCopy[name])
                dfCopy[name] = dfCopy[name].astype('int64')
            elif type == 'datetime64[ns]':
                dfCopy[name], _ = pd.factorize(dfCopy[name])
                dfCopy[name] = dfCopy[name].astype('int64')
            dfCopy[name].fillna(-np.inf, inplace = True)
            
            
        # for each column, now use the best freature engineering score    
        
        #           
        if self.target is not None:
             self.correlations = self.calcCorrelations(dfCopy)
             y = dfCopy[self.target]
             dfCopy.drop(self.target, axis=1, inplace=True)
             self.featureImportance = self.calcFeatureImportance(dfCopy, y)
        #dfCopy.to_csv('CorrFI-TestData.csv')
    
        evaluationColumns = dfCopy.columns                
        
        del dfCopy

        print ('Exploring Data', end='')
        
        for name in df:
            print ('.', end='')
            stats = getStats(df[name])
            self.columns[name] = stats
            #print ('name in ', name, stats['dataType'])
            #mlUtility.runLog('\nStat for=',name)
            #mlUtility.runLog(self.columns[name])
            if name != self.target:
                if stats['dataType'] == 'object':
                    self.reviewObjects(name, stats, df[name], project)
                elif hasattr(self.dataFrame[name],'cat'):
                    self.reviewObjects(name, stats, df[name], project)
                elif stats['dataType'] == 'datetime64':
                    self.reviewDatetime(name, stats, df[name])
                elif stats['dataType'] == 'bool':
                    self.reviewBool(name, stats, df[name])
                else:
                    self.reviewNumbers(name, stats, df[name])  
        print ()
        if self.target is not None:
            self.evaluateColumnImportance(evaluationColumns, self.correlations, self.featureImportance, doDrop=True)
        return
#        try:

        
#        except AssertionError:
#            raise Exception(self.KAT_TABLE_ERROR)
            
#        except Exception as e:
#            raise e
  
        
    '''
    Feature testing does 
    '''
  
    def featureTesting(self, project, name, df):
        mlUtility.runLog  ('Advanced. Evaluating correlations and feature importance\n')
        bestScores = {}
        bestRules = {}
        #mlUtility.runLog (' First Entry\n {}'.format(df))
         
        # make a copy of the data to do numerical evaluations
        dfCopy = df.copy()
        #mlUtility.runLog (' after copy\n {}'.format(df))
        #dfCopy.to_csv('CorrFI-TestData-before.csv')
        
        # Build the training data into floats
        #if self.target is not None:
        #    dfCopy[self.target].dropna(inplace=True)
        if project.isTrainingSet in dfCopy:
           dfCopy.drop(project.isTrainingSet, axis=1,  inplace=True)

        defaultRules = {}
        #mlUtility.runLog('Begin default factorizing')
        
        for colName in dfCopy:
            saveCol = df[colName]
            self.columns[colName] = getStats(df[colName])
            rules, dropped = runExploreTest(testDefaultFactorize,self.project, self, df, dfCopy, colName, self.columns[colName])
            defaultRules[colName] = rules
            df[colName] = saveCol 
        #mlUtility.runLog (' after default explore tests\n {}'.format(df))
             
        # Get the initial scores for each column
        #print (dfCopy)
        correlations = self.calcCorrelations(dfCopy)
        featureImportance = self.calcFeatureImportance(dfCopy, dfCopy[self.target])
        for colName in dfCopy:
            if colName == self.target or colName == project.isTrainingSet:
                pass
            else:
                
                bestScores[colName] = featureImportance[colName] + abs(correlations[self.target][colName])
                bestRules[colName] = defaultRules[colName]
                #mlUtility.runLog(' --- "{}" score {}, Default Rules {}'.format(colName, bestScores[colName], defaultRules[colName]))
        
        #mlUtility.runLog('End default factorizing')
        
        # for each column in the source file 
        allRules = []
        for colName in dfCopy:
            print ('.', end='')
            stats = self.columns[colName] 
            if colName != self.target:
                # for each column transformation test
                #type = df.dtypes[name]  
                datatype = stats['dataType']
                saveCol = dfCopy[colName]
                if stats['dataType'] == 'object':
                    tests = columnTests['object']
                elif hasattr(df[colName],'cat'):
                    tests = columnTests['object']
                elif stats['dataType'] == 'datetime64':
                    tests = columnTests['date']
                elif stats['dataType'] == 'bool':
                    tests = columnTests['bool']
                else:
                    tests = columnTests['number']
                testingColumn = df[colName]
                #print ('Datatype', stats['dataType'], colName)
                #mlUtility.runLog (' DF Column bfore funcion run\n {}'.format(df))
                for functionName in tests:
                    #def runExploreTest(function, project, explore, df, dfCopy, colName, stats
                    #print ('functionName=',colName, functionName)
                    rules, dropped = runExploreTest(functionName,self.project, self, df, dfCopy, colName, stats)
                    #mlUtility.runLog (' DF After run\n {}'.format(df.columns.tolist()))
                    
                    if dropped:
                        bestScores[colName] = 999
                        bestRules[colName] = rules
                        #mlUtility.runLog ('Dropped {} bestscore={}, bestRules={}'.format(colName,
                        #           bestScores[colName],bestRules[colName] ))
                        break                       
                    if rules is not None:
                        correlations = self.calcCorrelations(dfCopy)
                        featureImportance = self.calcFeatureImportance(dfCopy,dfCopy[self.target])
                        encodedColumns = getOneHotEncodeColumns(colName, dfCopy.columns.tolist())
                        #mlUtility.runLog ('  Coil name={}'.format(colName))
                        #mlUtility.runLog ('  Dataframe columns={}'.format(dfCopy.columns.tolist()))
                        #mlUtility.runLog ('  encoded columns={}'.format(encodedColumns))
                        if len(encodedColumns)>0:
                            score = 0
                            for x in encodedColumns:
                                allRules.append(tuple((x, featureImportance[x] + abs(correlations[self.target][x]), rules)))
                                score += featureImportance[x] + abs(correlations[self.target][x])
                            dfCopy.drop(encodedColumns, axis=1, inplace=True)
                            df.drop(encodedColumns, axis=1, inplace=True)
                            
                            # Do stuff for one-hot encoded
                            # Take the column one-hot encoded and add scores to root column
                        else:
                            score = featureImportance[colName] + abs(correlations[self.target][colName])
                        allRules.append(tuple((colName, score, rules)))
                        if bestScores[colName] < score:
                            #mlUtility.runLog ('best for column={} bestscore={}, bestRules={}'.format(colName,
                            #          bestScores[colName],bestRules[colName] ))
                            bestScores[colName] = score
                            bestRules[colName] = rules
                    df[colName] = testingColumn
                dfCopy[colName] = saveCol
        # Get the best rules
        for colName in bestRules:
            #mlUtility.runLog ('Final best rules for column={} bestscore={}, bestRules={}'.format(colName,
            #                          bestScores[colName],bestRules[colName] ))
            self.recommendations[colName] = bestRules[colName]
            for explore in bestRules[colName]:
                #mlUtility.runLog  ('bestRules[{}]={}'.format(colName, bestRules[colName]))
                if explore in exploreHeatMap:
                    self.heatMap.at[explore, colName] += 1
        #mlUtility.runLog ('All Rules\n')
        #for c,s,r in allRules:
        #    mlUtility.runLog ('  --col={}, score={}, rule={} '.format(c,s,r))


    def featureRecommendations(self, project, name, df):
        mlUtility.runLog  ('Evaluating Recommendations\n')
         
        # make a copy of the data to do numerical evaluations
        dfCopy = df.copy()
        #mlUtility.runLog (' after copy\n {}'.format(df))
        #dfCopy.to_csv('CorrFI-TestData-before.csv')
        
        # Build the training data into floats
        #if self.target is not None:
        #    dfCopy[self.target].dropna(inplace=True)
        if project.isTrainingSet in dfCopy:
           dfCopy.drop(project.isTrainingSet, axis=1,  inplace=True)

        
        for colName in dfCopy:
            saveCol = df[colName]
            self.columns[colName] = getStats(df[colName])
            rules, dropped = runExploreTest(testDefaultFactorize,self.project, self, df, dfCopy, colName, self.columns[colName])
            df[colName] = saveCol 
        #mlUtility.runLog (' after default explore tests\n {}'.format(df))
             

        for colName in dfCopy:
            # print ('.', end='')
            stats = self.columns[colName] 
            if colName != self.target:
                # for each column transformation test
                #type = df.dtypes[name]  
                datatype = stats['dataType']
                saveCol = dfCopy[colName]
                if stats['dataType'] == 'object':
                    tests = columnTests['object']
                elif hasattr(df[colName],'cat'):
                    tests = columnTests['object']
                elif stats['dataType'] == 'datetime64':
                    tests = columnTests['date']
                elif stats['dataType'] == 'bool':
                    tests = columnTests['bool']
                else:
                    tests = columnTests['number']
                testingColumn = df[colName]
                #print ('Datatype', stats['dataType'], colName)
                #mlUtility.runLog (' DF Column bfore funcion run\n {}'.format(df))
                for functionName in tests:
                    #def runExploreTest(function, project, explore, df, dfCopy, colName, stats
                    #print ('functionName=',colName, functionName)
                    rules, dropped = runExploreTest(functionName,self.project, self, df, dfCopy, colName, stats)
                    #mlUtility.runLog (' DF After run\n {}'.format(df.columns.tolist()))
                    
                    df[colName] = testingColumn
                dfCopy[colName] = saveCol


 
    def __str__ (self):
        str = ''
        #print (self.recommendations)
        for key, value in self.recommendations.items():
            if len(value) > 0:
                str += '\nRecommendations for column {}, type {}\n'.format(key, self.columns[key]['dataType'])
                for k, v in value.items():
                    if v is None:
                        str+= '  --->{}\n'.format(k)
                    else:
                        str+= '  --->{} value={}\n'.format(k,v)
            else:
                str += '\nNo Recommendations for column {}, type {}\n'.format(key, self.columns[key]['dataType'])
        return str
    
    
    def __getitem__ (self, name):
        if name in self.columns:
            if name in self.recommendations:
                return self.columns[name], self.recommendations[name]
        return None


    def getRecommendationsAsObject (self):
        
        recList = []
        for key, value in self.recommendations.items():
            
            column_recommendations = {}
            column_recommendations['name'] = key
            column_recommendations['type'] = self.columns[key]['dataType']
            column_recommendations['list'] = []
            column_recommendations['count'] = 0
            if len(value) > 0:
                for k, v in value.items():
                    column_recommendations['count'] += 1
                    if v is None:
                        column_recommendations['list'].append(k)
                    else:
                        column_recommendations['list'].append('{} value={}'.format(k,v))
            recList.append(column_recommendations)
        return recList



    def addExploreRules(self, rules, name, explore, value=None, key=None):
        if self.project.recommendOnly:
            self.addRecommendation(name, explore, value, key)
            return
        else:
            if key is not None :
                rules[explore+CLEANDATA_BREAK+key] = value
            else:
                rules[explore] = value
            return 
    
    
    def getRuleFunction(self, explore, name, value=None , df=None, forPredict=True):
        if self.project.recommendOnly:
            return None
        else:
            return getRule(explore, name, value , df, forPredict)
        
        
    def statsSummary (self, name):
        if name in self.columns:     
            stats = self.columns[name]
            dStats = {}
            for s in stats:
                if stats[s] is None:
                    dStats[s] = 'None'
                else:
                    dStats[s] = stats[s]
             
            str = 'Stats for Column: {}  datatype={}\n'.format(name, dStats['dataType'])
            str += '   mean:   {:<12.4}   first:  {}\n'.format(dStats['mean'] ,dStats['first'])
            str += '   median: {:<12}   last:   {}\n'.format(dStats['median'], dStats['last'])
            str += '   std:    {:<12.4}   top:    {}\n'.format(dStats['std'], dStats['top'])
            str += '   min:    {:<12}   freq:   {}\n'.format(dStats['min'], dStats['freq']   )
            str += '   max:    {:<12}   uniqie: {:<12}\n'.format(dStats['max'],dStats['unique'] )
            str += ' count:    {:<12}   nulls:  {:<12}\n\n'.format(dStats['count'],dStats['nullCount'] )
#            str += '    1%:    {:<10}   2.5%:   {:<10}   5%:   {:<10}      25%:   {:<10}    50%:   {:<10}\n'.format(stats['1%'], stats['2.5%'], stats['5%'] , stats['25%'] ,stats['50%'])
#            str += '   50%:    {:<10}   75%:    {:<10}  95%:   {:<10}    97.5%:   {:<10}    99%:   {:<10}\n'.format(stats['50%'], stats['75%'], stats['95%'] , stats['97.5%'] , stats['99%'])
            #mlUtility. traceLog((name)
            if stats['dataType'] == 'bool':
                pass
            elif stats['dataType']=='datetime64':
                pass
            elif hasattr(self.dataFrame[name],'cat'):
                pass
            elif stats['dataType'] != 'object':
                str += '   {:9d}% {:9.1f}% {:9d}% {:9d}% {:9d}% {:9d}% {:9d}% {:9.1f}% {:9d}%\n'.format(1, 2.5, 5, 25, 50, 75, 95, 97.5, 99)
                str += '   {:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f}\n'.format(stats['1%'], stats['2.5%'], stats['5%'], stats['25%'], stats['50%'], stats['75%'], stats['95%'] , stats['97.5%'] , stats['99%'])
            return str
        return 'No stats for column '+ name

    def allStatsSummary (self):
        str = 'List of all Stats\n'
        for name in self.dataFrame.dtypes.index:
            str += self.statsSummary(name)
            str += '\n'
        return str
            

    def dataSummary (self, rows=5):     
        mlUtility.runLog ('\n\nData Summary:')
        mlUtility.runLog ('\n\nFirst {} rows: '.format(rows))
        mlUtility.runLog (self.dataFrame.head(n=rows))
        mlUtility.runLog ('\n\nLast {} rows: '.format(rows))
        mlUtility.runLog (self.dataFrame.tail(n=rows))
        mlUtility.runLog ('\n')
        



    def getColumnValues(self, name):
        if name in self.dataFrame:
            return self.dataFrame[name].unique().tolist()
        return []

        


    def evaluateColumnImportance(self, columns, correlations, featureImportance, doDrop=False):
    
        colsToDrop = self.colsToDrop
        target = self.target
                
    
        col = []
        for name,i in sorted(featureImportance.items(), key=lambda item: item[1]):
            if name not in colsToDrop:
                col.append(name)
    
        # Top 80% of 
        topFI = col[round(len(col) * self.project.bottomImportancePrecentToCut):]
        #print (topFI)
    
        targetCorrABS = abs(correlations[target].copy())
        targetCorr = correlations[target].copy()
        #print ('\n\n Top Corr')
        #print (targetCorr)
    #    for name in targetCorr.index:
        col = []
        for name,_ in sorted(targetCorrABS.items(), key=lambda item: item[1]):
            #c = targetCorr[name]
            if name!=target:
                if name not in colsToDrop:
                    col.append(name)
                    c = targetCorr[name]
                    if c >= self.project.correlationThreshold or c<= -(self.project.correlationThreshold):
                        self.addRecommendation(name,CLEANDATA_HIGH_CORRELATION,c)
                        #print (name,' has high corr =',c)

                
        topCorr = col[round(len(col) * self.project.bottomImportancePrecentToCut):]
        #print (topCorr)
    
        self.topColumns = list(set(topCorr + topFI))
        mlUtility.runLog ('\nTop Columns = {}'.format(self.topColumns))
        # Add to the drop list if columns not included
        for name in columns:
            if name != target:
                if featureImportance[name] > self.project.featureImportanceThreshold:
                    #print (name, 'high feature importance',featureImportance[name])
                    self.addRecommendation(name,CLEANDATA_HIGH_FEATURE_IMPORTANCE,c)
            
                if name not in colsToDrop and doDrop:
                    if name not in self.topColumns:
                        #print ('Drop low importance', name) 
                        self.colsToDrop.append(name)
                        self.addRecommendation(name,CLEANDATA_DROP_LOW_FEATURE_IMPORTANCE_AND_CORR,
                             'FI={}, Corr={}'.format(featureImportance[name],correlations[self.target][name]))
                             

    def reviewObjects (self, name, stats, data, project):
        
        # Determine what type of data this object is.
        # alpha - only letters
        # alpha-umeric - mnumbers and letters
        # is it multiple words
        # Uniqie % = 
        # 
        
    
        # is it a Category
        # is it an ID - 100% unque, 
        # Part number
        # name
        # Description/text
        # 
        
                
        if stats['nullCount'] > 0:
            self.addRecommendation(name,CLEANDATA_MARK_MISSING,None)
            
        # Category   
        # Text Field      
        # ID
    
        # Check for small samples
        histogram = stats['histogram']
        
        if stats['unique'] <= project.uniqueThreshold:
            for item, value in histogram.items():
                if value < project.smallSample:
                    self.addRecommendation(name,CLEANDATA_REBUCKET,item, str(item))
                    
        # chck for large samples
        elif stats['unique'] > project.highDimensionality:
            self.addRecommendation(name,CLEANDATA_DIMENSIONALITY_REDUCTION,stats['unique'])
    
        # check for capitalization
    
        for item in iter(histogram.keys()):
            if item is not np.nan :
                lower = item.lower()
                #mlUtility. traceLog(("item, lower = ",item, lower)
                if item != lower:
                    if lower in histogram:
                        #mlUtility. traceLog(('   --> add recommendations',lower, item)
                        self.addRecommendation(name,CLEANDATA_FIX_CASE,[lower, item], lower+CLEANDATA_BREAK+str(item))
                upper = item.upper()
                if item != upper:
                    if upper in histogram:
                        self.addRecommendation(name,CLEANDATA_FIX_CASE+CLEANDATA_BREAK, [upper, item],
                                     upper+CLEANDATA_BREAK+str(item))
    
        # Figure out how uniqie the values are and make a recommendation
        if stats['unique'] >= stats['count'] * .90:
            # this is an ID field of uniqie values, needs to be dropped
            self.addRecommendation(name,CLEANDATA_DROP_ID_FIELD)
            self.colsToDrop.append(name)
        elif stats['unique'] <= stats['count'] * .10:
            # do nothing. can use one-hot encoding
            self.addRecommendation(name,CLEANDATA_SET_CATEGORY_DATATYPE,None)
        elif stats['unique'] <= stats['count'] * .50:
            # factorize!
            self.addRecommendation(name,CLEANDATA_CONVERT_CATEGORY_TO_INTEGER)
        else:
            self.addRecommendation(name,CLEANDATA_CONVERT_COLUMN_TO_INTEGER) 
            
        
        # Determine if a key
        pass
        
        # Check for unbalanced
        #checkForImbalanced (name, stats, data, isObject=True)
                
        return 
    
        


    def addRecommendation (self, name, explore, value=None, key=None):
        if name in self.recommendations:
            nameRecs = self.recommendations[name]
        else:
            nameRecs = {}
            self.recommendations[name] = nameRecs
            
        if key is not None :
            nameRecs[explore+CLEANDATA_BREAK+key] = value
        else:
            nameRecs[explore] = value
        
        if explore in exploreHeatMap:
            self.heatMap.at[explore, name] += 1
   


    def calcFeatureImportance(self, df, y):
        from xgboost import XGBClassifier
        
        
        target = self.project.targetVariable[self.project.defaultPreppedTableName]
                
        # Create separate object for input features
        #y = df[target][:self.project.trainingSetLength]

   
        # Create separate object for target variable
        #df.drop(target, axis = 1, inplace=True)
        col = df.columns

        # Build a forest and compute the feature importances
        forest = XGBClassifier(random_state=self.project.randomState, n_jobs=-1)

        forest.fit(df[:self.project.trainingSetLength], y[:self.project.trainingSetLength])
        importances = forest.feature_importances_
        #indices = np.argsort(importances)[::-1]
        
        importance = {}
        for n,i in zip(df.columns,importances):
            if n != self.target:
                importance[n] = i
        
        return importance

        

    def calcCorrelations(self, df):
        return df[:self.project.trainingSetLength].corr() 


  
    
    def reviewNumbers (self, name, stats, series):
        # is it a Category?
        # is it an ID - 100% unque, 
        # Part number (repeats)
        # name
        # Description/text
        # skewed
        # Normal distribution
        # 
         
        #print (name)
        if stats['nullCount'] > 0:
            if stats['binary']==True:
                self.addRecommendation(name,CLEANDATA_ZERO_FILL,name)
            else:
                self.addRecommendation(name,CLEANDATA_ZERO_FILL,'mean')
        
        #recommendations['Remove the top 1% for '+ name] =  stats['99%']
        #recommendations['Remove the bottom 1% for '+ name] =  stats['1%']
        
        self.checkforOutliers (name, series, stats, strong=True)
        
                 
        # Check for unbalanced
            
        if checkForImbalanced (name, stats, series, isObject=False):
            self.addRecommendation(name , CLEANDATA_IMBALANCED_DATA, 
                                    value='Top value {} with {}%'.format(stats['count']/stats['freq'], stats['top']*100.), key=None)
        skew = series.skew()
        if skew > self.project.skewFactor:
            self.addRecommendation(name,CLEANDATA_REFACTOR_DATA,'skewed')
            
       
        sparseScore = stats['nullCount'] / len(series)
        if  sparseScore > .5:
            self.addRecommendation(name,CLEANDATA_REFACTOR_DATA,'sparse')
        
        if stats['unique'] == stats['count']:
            # this is an ID field of uniqie values, needs to be dropped
            self.addRecommendation(name,CLEANDATA_DROP_ID_FIELD)
            self.colsToDrop.append(name)
        

        return
  
    

        
    def reviewDatetime (self, name, stats, series):

        return 

    def reviewBool (self, name, stats, series):

        return 

           
    
    def checkforOutliers (self, name, series, stats, strong=True):
        
        numItems = len(series)
        
        if stats['unique'] < (numItems * .50) or stats['std']==0:
            return
        
        
        if series.isnull().values.any():
            return
        
        p25 = stats['25%']
        p75 = stats['75%']
    
        p1 = stats['1%']
        p99 = stats['99%']
         
        
        level1 = doubleMADsfromMedian(series)
        if len(level1)>0:
            valuesL1 = [ series[key] for key, value in level1.items() if value==True ]
            
            below25 = [ x for x in valuesL1 if x < p25]
            above75 = [ x for x in valuesL1 if x > p75]
            
            if len(below25) > 0 and strong:
                level2 = doubleMADsfromMedian(below25)
                if len(level2)>0:
                    valuesL2 = [ value for mask, value in zip(np.nditer(level2), below25) if mask==True ]
                    below1 = [ x for x in valuesL2 if x < p1]
                    if len(below1) > 0:
                        self.addRecommendation(name,CLEANDATA_REMOVE_ITEMS_BELOW,np.max(below1))
                
            if len(above75) > 0 and strong:
                level2 = doubleMADsfromMedian(above75)
                if len(level2)>0:
                    valuesL2 = [ value for mask, value in zip(np.nditer(level2), above75) if mask==True ]
                    above99 = [ x for x in valuesL2 if x > p99]
                    if len(above99) > 0:
                        self.addRecommendation(name,CLEANDATA_REMOVE_ITEMS_ABOVE, np.min(above99))
    
        return None
    
        



    def plotExploreHeatMap(self, toWeb=False):           
            
        # Make the figsize 9 x 8
        plt.figure(figsize=(14,10))
        
        # Plot heatmap of correlations
        sns.heatmap(self.heatMap, annot=False, cbar=True, cmap='Reds', fmt='.0f')
        
        if toWeb:
            #
            # Convert plot to PNG image
            encoded = fig_to_base64(plt)
            return 'data:image/png;base64, ' + encoded.decode('utf-8')
            
        else:
            plt.show()
            return None


   

    def plotNumericColumn(self, name):
        if name in self.dataFrame:
        # Violin plot using the Seaborn library
            sns.violinplot(self.dataFrame[name])
            plt.show()
        
        

    def plotHistogramsAll(self, size=14):
        # Plot histogram grid
        self.dataFrame.hist(figsize=(size,size), xrot=-45)
        # Clear the text "residue"
        plt.show()
        
        
    def plotSegmentation(self, x, y=None, hue=None):
        if x in self.dataFrame:
            if y==None or y in self.dataFrame:
                sns.boxplot(x=x, y=y, data=self.dataFrame)
                plt.show()
                sns.violinplot(x=x, y=y, data=self.dataFrame)
                plt.show()
                # Scatterplot of satisfaction vs. last_evaluation
                if hue in self.dataFrame:
                    sns.lmplot(x=x, y=y, hue=hue, data=self.dataFrame, fit_reg=False)
                    plt.show()

    def plotColumnImportance(self):
        cor = []
        imp = []
        for name in self.topColumns:
            cor.append(self.correlations[self.target][name])
            imp.append(self.featureImportance[name])
    
   
        df = pd.DataFrame({'Correlation to Target': cor,
                          'Feature Importance': imp}, index=self.topColumns)
        df.plot.barh()
        plt.show()



    def plotCorrelations(self):
      
        mask = np.zeros_like(self.correlations, dtype=np.bool)
        mask[np.triu_indices_from(mask)] = True
        
        # Make the figsize 9 x 8
        plt.figure(figsize=(14,10))
        # Plot heatmap of correlations
        sns.heatmap(self.correlations, annot=True, mask=mask, cbar=True, cmap='Greens', fmt='.3f')
        plt.show()


    def plotFeatureImportance(self):
        
        col = []
        imp = []
        for c,i in sorted(self.featureImportance.items(), key=lambda item: item[1]):
            col.append(c)
            imp.append(i)
            
        
        # Plot the feature importances of the forest
        
        #names = list(importance.keys())
        #values = list(importance.values())

        #tick_label does the some work as plt.xticks()
        plt.xlabel('Importance')
        plt.ylabel('Column')
        plt.title('Feature Importance')
        #plt.barh(*zip(*sorted(importance.items())))
        plt.barh(col, imp)
        
#        plt.bar(range(len(importance)),values,tick_label=names)
        #plt.savefig('bar.png')
        plt.show()
        return

    def plotCategoryColumn(self, name, figsize=(6,7)):
        if name in self.dataFrame:
            plt.figure(figsize=figsize)
            sns.countplot(y=name, data=self.dataFrame)
            plt.show()        





