import argparse
import bson
import os
import pymongo
import re
import sys
from pymongo import MongoClient


parser = argparse.ArgumentParser(description='Store test result info into db.')

#parser.add_argument('--log', help='Name of the log file', type=str, required=True )
parser.add_argument('--input', help='File that contains the test info', type=str, required=True )
parser.add_argument('--batch', help='Batch insert. Used only with empty database', action='store_true', required=False )
parser.add_argument('--db', help='Name of DB.',  type=str, required=True)

args = parser.parse_args()



def generateDB():
    filesInDB = open('.filesInDBApache', 'a')
    files = open('.filesInDBApache', 'r').read().split('\n')
    prevRunID = -1

    prevTestName = ''

    for test in open(args.input, 'r'):
        test = test.strip()
        if test in files:
            continue

        test = test.split(',')

        runID = test[0]
        buildNumber = runID
        testComponent = test[1]
        testClass = test[2]
        try:
            testStepName = test[3]
            stepTiming = test[5]
            testID = testComponent+'.'+testClass
            testName = testID
        except IndexError:
            continue

        if testName != prevTestName:
            if not prevTestName == '':
                testStat = db.testStat.find({"_id": prevTestID})
                '''
                testStatJSON = {
                    "_id": prevTestID,
                    "testName": prevTestName,
                    "duration": [duration],
                    "passed": [passed],
                    "buildNumber": [prevRunID],
                    "testRun": [prevRunID],
                    "testSteps": testStepTiming[prevTestName]
                }
                print testStatJSON
                sys.exit(0)
                '''
                if testStat.count() == 0:
                    testStatJSON = {
                        "_id": prevTestID,
                        "testName": prevTestName,
                        "duration": [duration],
                        "passed": [passed],
                        "buildNumber": [prevRunID],
                        "testRun": [prevRunID],
                        "testSteps": [testStepTiming[prevTestName]]
                    }
                    db.testStat.insert(testStatJSON)
                else:
                    #print ''
                    db.testStat.update({"_id": prevTestID}, {"$push": {"duration": duration, "passed": passed, "buildNumber": prevRunID, 'testRun': prevRunID, 'testSteps': testStepTiming[prevTestName]}})

            prevRunID = runID
            prevTestName = testName
            prevTestID = testID
            testStepTiming = {}
            duration = 0



        #900,org.apache.zookeeper,ClientReconnectTest,testClientReconnect,Passed,0.626
        #


        passed = test[4]
        if passed.lower() == 'passed':
            passed = True
        else:
            passed = False

        if testName not in testStepTiming:
            testStepTiming[testName] = []
        testStepTiming[testName].append([stepTiming, testStepName])
        duration += float(stepTiming)


    testStat = db.testStat.find({"_id": prevTestID})
    if testStat.count() == 0:
        testStatJSON = {
            "_id": prevTestID,
            "testName": prevTestName,
            "duration": [duration],
            "passed": [passed],
            "buildNumber": [prevRunID],
            "testRun": [prevRunID],
            "testSteps": [testStepTiming[prevTestName]]
        }
        db.testStat.insert(testStatJSON)
    else:
        #print ''
        db.testStat.update({"_id": prevTestID}, {"$push": {"duration": duration, "passed": passed, "buildNumber": prevRunID, 'testRun': prevRunID, 'testSteps': testStepTiming[prevTestName]}})


    






#generateDBForTest("3.0.0-370", "6", "logs/6_3.0.0-370.log")
#generateDBForTest("3.0.0-370", "6", "logs/344_2.8.0.4613.log")




conn = MongoClient()
db = conn[args.db]
generateDB()

