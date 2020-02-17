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
import datetime
from pathlib import Path


# cases:   name, name+name, name:name
def getFirst(value):
    plus = value.split('+')
    colon = value.split(':')
    # case 1: name and case 2: name+name
    if len(colon) == 1 and len(plus) >= 1:
        return plus[0]
    # case 3
    else:
        return colon[0]

    # return value.split('+')[0]


def removePlus(value):
    return value.split('+')[0]


# ######
# ##  LOG FILES
# ######
def openLogs(logFile=None, errorFile=None, append=True, toTerminal=True):

    global runLog_
    global utilityErrorLogFile_
    global utilityLogFile_
    global utilityLogFileToTerminal_
    global runFileNameParams_

    runLog_ = True
    utilityErrorLogFile_ = None
    utilityLogFile_ = None
    utilityLogFileToTerminal_ = toTerminal
    runFileNameParams_ = tuple((logFile, errorFile, append, toTerminal))

    if logFile is not None:
        myFile = Path(logFile)
        if myFile.is_file() and append:
            utilityLogFile_ = open(logFile, 'a')
            utilityLogFile_.write('\n')
        else:
            utilityLogFile_ = open(logFile, 'w')

    if errorFile is not None:
        myFile = Path(errorFile)
        if myFile.is_file() and append:
            utilityErrorLogFile_ = open(errorFile, 'a')
            utilityErrorLogFile_.write('\n')
        else:
            utilityErrorLogFile_ = open(errorFile, 'w')
    return


def reOpenLogs():
    global runLog_
    global utilityErrorLogFile_
    global utilityLogFile_
    global utilityLogFileToTerminal_
    global runFileNameParams_

    if runLog_:
        closeLogs()
        p1, p2, p3, p4 = runFileNameParams_
        openLogs(p1, p2, True, p4)


def runLog(message='', useTime=False, toTerminal=True):
    global runLog_
    global utilityErrorLogFile_
    global utilityLogFile_
    global utilityLogFileToTerminal_
    global runFileNameParams_

    if runLog_:
        if useTime:
            msg = '{} @ {}'.format(message, datetime.datetime.now())
        else:
            msg = '{}'.format(message)
        if utilityLogFile_ is not None:
            utilityLogFile_.write(msg+'\n')
    if toTerminal and utilityLogFileToTerminal_:
        print(msg)


def errorLog(message):
    global runLog_
    global utilityErrorLogFile_
    global utilityLogFile_

    msg = 'ERR: {} @ {}'.format(message, datetime.datetime.now())
    print(msg)
    if utilityErrorLogFile_ is not None:
        utilityErrorLogFile_.write(msg+'\n')
    runLog(msg, useTime=False, toTerminal=False)


def closeLogs():
    global runLog_
    global utilityErrorLogFile_
    global utilityLogFile_

    if utilityErrorLogFile_ is not None:
        utilityErrorLogFile_.close()
    utilityErrorLogFile_ = None

    if utilityLogFile_ is not None:
        utilityLogFile_.close()
    utilityLogFile_ = None
    runLog_ = False

    return


#######
# Trace Log files FILES
#######

def openTraceLog(logFile=None, toTerminal=True, append=False):
    global activityTraceLog_
    global activityTraceLogToTerminal_
    global utilityTraceLogFile_

    activityTraceLog_ = False
    activityTraceLogToTerminal_ = True
    utilityTraceLogFile_ = None

    if logFile is not None:
        myFile = Path(logFile)
        if myFile.is_file() and append:
            utilityTraceLogFile_ = open(logFile, 'a')
            utilityTraceLogFile_.write('\n')
        else:
            utilityTraceLogFile_ = open(logFile, 'w')
    activityTraceLog_ = True
    activityTraceLogToTerminal_ = toTerminal


def traceLog(message, useTime=False, toTerminal=True):
    global activityTraceLog_
    global activityTraceLogToTerminal_
    global utilityTraceLogFile_

    if toTerminal is None:
        printToTerminal = activityTraceLogToTerminal_
    else:
        printToTerminal = toTerminal
    if activityTraceLog_:
        if useTime:
            msg = '{} @ {}'.format(message, datetime.datetime.now())
        else:
            msg = '{}'.format(message)

        if utilityTraceLogFile_ is not None:
            utilityTraceLogFile_.write(msg+'\n')

        if printToTerminal:
            runLog(msg)
        runLog(msg, useTime=False, toTerminal=False)
    return


def closeTraceLog():
    global activityTraceLog_
    global activityTraceLogToTerminal_
    global utilityTraceLogFile_

    if activityTraceLog_ is not None:
        activityTraceLog_.close()

    activityTraceLog_ = False
    utilityTraceLogFile_ = None
    activityTraceLogToTerminal_ = True

    return


def makeCSVList(message):
    row = ''
    comma = ''
    for x in message:
        row += comma
        row += '{}'.format(x)
        comma = ','
    row += '\n'
    return row


def openCSVLog(logFile=None, toOpen=False, headerList=None):
    global CSVLogRunLogName_
    global CSVLogRunActive_
    global CSVHeader_

    CSVLogRunLogName_ = logFile
    CSVLogRunActive_ = toOpen
    headerList

    CSVHeader_ = CSVLogRunLog_ = None

    if toOpen:
        myFile = Path(CSVLogRunLogName_)
        if myFile.is_file():
            pass
        else:
            File = open(CSVLogRunLogName_, 'w')
            File.write(makeCSVList(headerList))
            File.close()


def CSVLog(messageList):
    global CSVLogRunLogName_
    global CSVLogRunActive_
    global CSVHeader_

    if CSVLogRunActive_:
        myFile = Path(CSVLogRunLogName_)
        if myFile.is_file():
            File = open(CSVLogRunLogName_, 'a')
            File.write(makeCSVList(messageList))
            File.close()
        else:
            File = open(CSVLogRunLogName_, 'w')
            File.write(makeCSVList(CSVHeader_))
            File.write(makeCSVList(messageList))
            File.close()


# Convert text to an integer
# For example, to change an ID or PartNumber
#
# Base 27 is A to Z with zero being undefined (BC != ABC)
def convertAlphaTextToInteger(txt, base=26.0):

    # 0 1 2 3 4 5 6 7 8 9 A  B  C  D  E  F  G  H  I  J  K  L  M  N  O  P
    #   Q  R  S  T  U  V  W  X  Y  Z
    # 0 1 2 3 4 5 6 6 7 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25
    #  26 27 28 29 30 31 32 33 34 35
    def convert(c):
        ascii = ord(c)
#        if ascii >=48 and ascii <= 57:  # 0 (48) to 9 (57)
#            return int(ascii-48)
        if ascii >= 65 and ascii <= 90:  # A (65) to Z(90)
            return int(ascii - 64)          # because A = 1 and 0 is undefined
        if ascii >= 97 and ascii <= 122:  # a (97)to z (122)
            return int(ascii - 96)
        # Ignore anything else
        return None

    def myMap(txt):
        lst = []
        for c in txt:
            v = convert(c)
            if v is not None:
                lst.append(v)
        return lst

    # Convert to upper case and Integer values
    if type(txt) == int or type(txt) == float:
        return int(txt)
    lst = myMap(str(txt))

    #
    value = 0
    power = len(lst) - 1
    for i in range(len(lst)):
        value += (base**power) * lst[i]
        i += 1
        power -= 1

    return int(value)


def convertColumnToHash(df, name):
    df[name] = df[name].apply(lambda x: hash(x))


def raiseError(message):
    errorLog(message)


def table(rows, margin=0, columns=[]):
    """
    Return string representing table content, returns table as string and as
        a list of strings.
    It is okay for rows to have different sets of keys, table will show union
        of columns with
    missing values being empty spaces.
    :param rows: list of dictionaries as rows
    :param margin: left space padding to apply to each row, default is 0
    :param columns: extract listed columns in provided order, other columns
        will be ignored
    :return: table content as string and as list
    """
    def projection(cols, columns):
        return [(x, cols[x]) for x in columns if x in cols]\
                if columns else cols.items()

    def row_to_string(row, columns):
        values = [(row[name] if name in row else "").rjust(size)
                  for name, size in columns]
        return "|%s|" % ("|".join(values))

    def header(columns):
        return "|%s|" % ("|".join([name.rjust(size)
                         for name, size in columns]))

    def divisor(columns):
        return "+%s+" % ("+".join(["-" * size for name, size in columns]))
    data = [dict([(str(a), str(b)) for a, b in row.items()]) for row in rows]
    cols = dict([(x, len(x) + 1)
                 for row in data for x in row.keys()]) if data else {}
    for row in data:
        for key in row.keys():
            cols[key] = max(cols[key], len(row[key]) + 1)
    # extract certain columns to display (or all if not provided)
    proj = projection(cols, columns)
    table = [divisor(proj), header(proj), divisor(proj)] + \
        [row_to_string(row, proj) for row in data] + [divisor(proj)]
    table = ["%s%s" % (" " * margin, tpl)
             for tpl in table] if margin > 0 else table
    table_text = "\n".join(table)
    return (table_text, table)


def printAsTable(rows, margin=0, columns=[], toTerminal=True):
    """
    Print table in console for list of rows.
    """
    txt, _ = table(rows, margin, columns)
    runLog(txt, toTerminal=toTerminal)


class Counters(object):
    def __init__(self, start, stop, maxes, features):
        # print (start, stop, maxes, features)
        self.maxes = maxes.copy()  # Reverse if the max digets
        self.featureList = features.copy()
        self.counter = start.copy()  # Reverse order of a number
        self.stop = stop.copy()

        self.maxes.reverse()
        self.featureList.reverse()
        self.counter.reverse()
        self.stop.reverse()
        self.skip = [0] * len(start)

    def registerSkip(self, name, option):
        i = 0
        for n in self.featureList:
            if name == n:
                self.skip[i] = option
                # print ('skip=',self.skip)
                return True
            i += 1
        return False

    def testSkip(self):
        for digit, option in enumerate(self.skip):
            # print ('   test=',digit, option,)
            if option > 0:
                if self.counter[digit] == option:
                    return False
        return True

    def get(self, name):
        clen = 0
        for getName in self.featureList:
            if getName == name:
                return(self.counter[clen])
            clen += 1

    def __getitem__(self, name):
        clen = 0
        for getName in self.featureList:
            if getName == name:
                return(self.counter[clen])
            clen += 1

    def getNext(self, MinDigits=None):
        if self.testEqual(self.stop):
            return False
        working = True
        while working:
            if self.update():
                if self.testSkip():
                    if MinDigits is not None:
                        digets = 0
                        for x in self.counter:
                            if x > 0:
                                digets += 1
                        if digets == MinDigits:
                            return True
            else:
                return False

    def testEqual(self, test2):
        for x, y in zip(self.counter, test2):
            if x != y:
                return False
        return True

    def update(self):
        working = True
        digit = 0
        while working:
            if digit == len(self.counter):
                return False
            digitValue = self.counter[digit]
            maxValue = self.maxes[digit]
            if digitValue < maxValue:
                digitValue += 1
                self.counter[digit] = digitValue

                return True
            elif digitValue == maxValue:
                self.counter[digit] = 0
                digit += 1

            if self.testEqual(self.maxes):
                return False
        return True

    def display(self):
        show = ''
        counter = self.counter.copy()
        while len(counter) > 0:
            show += str(counter.pop())
        return show

    def getAll(self):
        return self.counter.copy()
