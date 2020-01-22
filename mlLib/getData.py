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

import mlLib.mlUtility as mlUtility


# Comment Out Google APIs for easy Distribution
#from oauth2client import file, client, tools
#from googleapiclient import discovery
#from apiclient.discovery import build
#from httplib2 import Http



    

# Data Dictionary for a single table type
class getData (object):
    
    KAT_TABLE_ERROR = 'There was a kat table error.'
    GOOGLE_SHEET_ERROR = 'There was an error getting the google sheet'
   
    
    def __init__(self, name, type=None, description=None, location=None, fileName=None, range=None, sheetName=None, df=None, hasHeaders = False):
              
                
        try:
            self.name = name
            self.description = description
            
            if type is None:
                if '.csv' in fileName:
                    self.type = 'csv'
                elif '.xls' in fileName: 
                    self.type = 'xls'
            else:
                self.type = type
            
            self.location = location
            self.fileName = fileName
            self.range = range
            self.sheetName = sheetName
            self.properties = None
            self.hasHeaders = hasHeaders
            self.dataFrame = df
            self.explore = None

            
        
        except AssertionError:
            raise Exception(self.KAT_TABLE_ERROR)
            
        except Exception as e:
            raise e
          


    def __str__(self):
        str =  '  Name: {}\n'.format(self.name)
        str += '     Description: {}\n'.format(self.description) 
        str += '     Type: {}\n'.format(self.type) 
        str += '     Location: {}\n'.format(self.location) 
        str += '     Filename: {}\n'.format(self.filename)
        str += '     Sheet: {}\n'.format(self.sheetName)
        str += '     Range: {}\n'.format(self.sheetRange())
        str += '     Properties: {}\n\n'.format(self.properties)
        str += '     Has Headers: {}\n\n'.format(self.hasHeaders)    
        
     
        return str
    
    def validateFilePath(self):
        if self.location is None:
            return (self.fileName)
        else:
            return (self.location + self.fileName)


    def validateGoogleSheet(self):
        return (self.location)

    
    def openTable(self): 
        def headerValue(s):
            if self.hasHeaders:
                return(0)
            else:
                return(None)
                
        compression='gzip'
        if self.type == 'csv':
            path = self.validateFilePath()
            self.dataFrame = pd.read_csv(path, header=headerValue(self), low_memory=False)
# Comment Out Google APIs for easy Distribution
#        elif self.type == 'GoogleSheet':
#            self.dataFrame = self.openGoogle()
#            self.fixHeaders()
#            self.fixNan()
        elif self.type == 'xls':
            path = self.validateFilePath()
            self.dataFrame = pd.read_excel(path, header=headerValue(self), sheet_name=self.sheetName)
        elif self.type == 'gz':
            path = self.validateFilePath()
            self.dataFrame = pd.read_csv(path, header=headerValue(self), low_memory=False, compression='gzip')
        elif self.type == 'df':
            pass
        else:
            return None
        
        return self.dataFrame
    
    
    def getTableDF(self):
        return self.dataFrame
    
    # for GoogleSheets  = we need to fix the Dataframe columns header
    def fixHeaders(self):
            
        newcolumns = {}
        for x in self.dataFrame.columns.tolist():
            p = int(x)
            s = str(self.dataFrame.loc[0,p])
            newcolumns[p] = s           
       
        # Rename the indexs
        newindex = {}
        for i in range(1,self.dataFrame.shape[0]+1):
            newindex[i] = i-1
 
       # Drop the old label row and reindex
        self.dataFrame = self.dataFrame.drop([0], axis=0).rename(columns=newcolumns, index = newindex)
        
        return None



    # for GoogleSheets  = we need to fix the Dataframe columns header
    def fixNan(self):
        self.dataFrame.replace(to_replace='', value=np.nan, inplace=True)
       
  

    
    def sheetRange(self):
        if self.range is not None and self.sheetName is not None:
            return (self.sheetName + "!" + self.range)
        elif self.range is not None:
            return (self.range)
        else:
            return None


