import subprocess
import os
import re
import argparse
import sys
import urllib
from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup


parser = argparse.ArgumentParser(description='Store Log info into db.')

parser.add_argument('--project', help='Name of the apache project listed on Jenkins (check https://builds.apache.org/view/All/)', type=str, required=True )
#parser.add_argument('--summaryPage', help='Summary page of the apache project listed on Jenkins', action='store_true', required=False )
#parser.add_argument('--dst', help='Output folder that stores the summary pages', type=str, required=False )

args = parser.parse_args()


buildHistoryURL = 'https://builds.apache.org/view/All/job/%s/buildHistory/all' % (args.project)
apacheURL = 'https://builds.apache.org%stestReport'
summaryURL = 'https://builds.apache.org%s'

buildHistoryFile = '.%s_build_history' % (args.project)
buildListFile = '.%s_build_list' % (args.project)
crawledListFile = '.%s_crawled_list' % (args.project)

def crawl():
    #if not args.summaryPage:
    os.system('wget --no-check-certificate --secure-protocol=SSLv3 %s -O %s' % (buildHistoryURL, buildHistoryFile))
    parseHTML()
    crawlTestResults()
    #if args.summaryPage:
    crawlSummaryPage()
    


def parseHTML():
    index = open(buildHistoryFile, "r").read()


    buildListF = open(buildListFile, "a")
    buildList = open(buildListFile, "r").read().split('\n')

    parsedIndex = BeautifulSoup(index)


    runToBuild = {}

    for build in parsedIndex.findAll('td'):
        if re.match('([0-9]+\.[0-9]+\.[0-9]+\.[0-9])', build.text) or re.match('([0-9]+\.[0-9]+\.[0-9]+-[0-9]+)', build.text) or re.match('(\#[0-9]+)', build.text):
            td = BeautifulSoup(str(build))
            try:
                run = td.find('a', attrs={'class': 'build-status-link'})['href']
                run = run.replace('/console', '/')
                buildListF.write(build.text+";"+run+"\n")
                print build.text + ' ' + run
            except TypeError:
                continue
    
def crawlTestResults():
    buildList = open(buildListFile, "r").read().split('\n')
    crawledListF = open(crawledListFile, "a")
    crawledList = open(crawledListFile, "r").read().split('\n')


    for build in buildList:
        build = build.strip()
        if build == '':
            continue
        runID = build.split(';')[0]
        buildNum = build.split(';')[1]
        if runID not in crawledList:
            crawledListF.write(runID+"\n")
            testResultURL = apacheURL % (buildNum)
            try:
                parseTests(runID, buildNum, testResultURL)
            except AttributeError:
                continue


def parseTests(runID, buildNum, testResultURL):
    os.system('rm .temp'+args.project)
    os.system('wget --no-check-certificate --secure-protocol=SSLv3 %s -O .temp%s' % (testResultURL, args.project))

    testResult = open('.temp'+args.project, 'r').read()



    testResult = BeautifulSoup(testResult)


    output = open(args.project, 'a')


    try:
        resultTable = testResult.find('table', attrs={'id': 'testresult'})
        resultTableBody = BeautifulSoup(str(resultTable.find('tbody')))
    except AttributeError:
        return
    

    for tr in resultTableBody.findAll('tr'):
        # for each test package
        #while 'result-passed' not in tr or tr.find('a', attrs='model-link inside') != None:
        url = tr.find('a', attrs='model-link inside')['href']
        # url for test classes
        classURL = apacheURL % (buildNum)+ '/'+url
        classes = BeautifulSoup(urllib.urlopen(classURL))

        packageName = tr.find('a', attrs='model-link inside').text

        for testClass in classes.find('table', attrs={'id': 'testresult'}).find('tbody').findAll('tr'):
            testClassURL = testClass.find('a', attrs='model-link inside')['href']
            testClassURL = classURL + testClassURL
            print 'Downloading %s' % testClassURL
            tests = BeautifulSoup(urllib.urlopen(testClassURL))

            testClassName = testClass.find('a', attrs='model-link inside').text 

            for test in tests.find('table', attrs={'id': 'testresult'}).find('tbody').findAll('tr'):
                testName = test.find('a', attrs='model-link inside').text
                if test.find('span', attrs='result-passed') != None:
                    passFail = test.find('span', attrs='result-passed').text
                if test.find('span', attrs='result-skipped') != None:
                    passFail = test.find('span', attrs='result-skipped').text
                if test.find('span', attrs='result-regression') != None:
                    passFail = test.find('span', attrs='result-regression').text
                if test.find('span', attrs='result-failed') != None:
                    passFail = test.find('span', attrs='result-failed').text
                
                for t in test.findAll('td'):
                    for attr, val in t.attrs:
                        if attr == 'data':
                            testTime = val

                #print ','.join([runID.replace('#', ''), packageName, testClassName, testName, passFail, testTime])
                output.write(','.join([runID.replace('#', ''), packageName, testClassName, testName, passFail, testTime])+'\n')

                

def crawlSummaryPage():
    index = open(buildHistoryFile, "r").read()
    
    buildList = open(buildListFile, "r").read().split('\n')
    parsedIndex = BeautifulSoup(index)

    runToBuild = {}

    fileList = []

    projectName = args.project
    for root, folder, fileName in os.walk('apacheSummaryPages/' + projectName):
        for f in fileName:
            fileList.append(f)

    for build in parsedIndex.findAll('td'):
        if re.match('([0-9]+\.[0-9]+\.[0-9]+\.[0-9])', build.text) or re.match('([0-9]+\.[0-9]+\.[0-9]+-[0-9]+)', build.text) or re.match('(\#[0-9]+)', build.text):
            td = BeautifulSoup(str(build))
            try:
                run = td.find('a', attrs={'class': 'build-status-link'})['href']
                run = run.replace('/console', '/')
                outputName = run.split('/')[-2] + '.html'

                pageURL = summaryURL % run
                outputLoc = 'apacheSummaryPages/' + args.project + '/' + outputName
                if outputName in fileList:
                    continue

                print 'wget --no-check-certificate --secure-protocol=SSLv3 %s -O %s' % (pageURL, outputLoc)
                os.system('wget --no-check-certificate --secure-protocol=SSLv3 %s -O %s' % (pageURL, outputLoc))
            except TypeError:
                continue

    return


    



crawl()


