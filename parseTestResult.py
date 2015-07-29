import sys
import argparse
from xml.dom import minidom
from scipy import stats
from rpy2.robjects.packages import importr
import rpy2.robjects as ro
import collections
import numpy


parser = argparse.ArgumentParser(description='Compare test results.')


parser.add_argument('--in1', help='Input XML location.', type=str)
parser.add_argument('--in2', help='Input XML location.', type=str)

args = parser.parse_args()


#################################################################
'''helper method for flatten an iterable'''
def flatten(iterable):
	results = []
	for i in iterable:
		if isinstance(i, collections.Iterable) and not isinstance(i, basestring):
			results.extend(flatten(i))
		else:
			results.append(i)
	return results
#################################################################


def compareXML():
	in1 = minidom.parse(args.in1)
	in2 = minidom.parse(args.in2)

	testcaseIn1 = in1.getElementsByTagName('testcase') 
	testcaseIn2 = in2.getElementsByTagName('testcase') 

	stats = importr('stats')
	lsr = importr('lsr')

	toCompare = {}
	for t in testcaseIn1:
		testName = t.attributes['name'].value.split(' ')[0]
		if testName not in toCompare:
			toCompare[testName] = [[], []]
		
		testTime = t.attributes['time'].value

		toCompare[testName][0].append(float(testTime))
	
	for t in testcaseIn2:
		testName = t.attributes['name'].value.split(' ')[0]
		if testName not in toCompare:
			toCompare[testName] = [[], []]
		
		testTime = t.attributes['time'].value

		toCompare[testName][1].append(float(testTime))



	for testName, testTime in toCompare.items():
		print testName, sum(testTime[0]), sum(testTime[1]), numpy.mean(testTime[0]), numpy.mean(testTime[1])
	
	testTimeIn1 = []
	testTimeIn2 = []
	for testName, testTime in toCompare.items():
		testTimeIn1.append(testTime[0])
		testTimeIn2.append(testTime[1])

	testTime1 = []
	testTime2 = []

	for i in range(0, len(testTimeIn1[0])):
		t1 = []
		t2 = []
		for j in range(0, len(testTimeIn1)):
			t1.append(testTimeIn1[j][i])
			t2.append(testTimeIn2[j][i])
		#print t, sum(t)
		testTime1.append(sum(t1))
		testTime2.append(sum(t2))
		#print testTime1



		
	ttest = stats.t_test(ro.FloatVector(testTime1), ro.FloatVector(testTime2))
	print ttest
	effectSize = str(lsr.cohensD(ro.FloatVector(testTime1), ro.FloatVector(testTime2))).split(']')[1].strip() 
	testName = args.in1.split('/')[-1]
	print "%s,%s,%s" % (testName, str(ttest.rx2('p.value')).split(']')[1].strip(), effectSize)#str(ttest.rx2('p.value')).split(']')[1].strip()

	'''
	for testName, testTime in toCompare.items():
		ttest = stats.t_test(ro.FloatVector(testTime[0]), ro.FloatVector(testTime[1]), 'greater')
		effectSize = str(lsr.cohensD(ro.FloatVector(testTime[0]), ro.FloatVector(testTime[1]))).split(']')[1].strip() 
		print testName, ttest, effectSize#str(ttest.rx2('p.value')).split(']')[1].strip()
		#print testName, stats.ttest_rel(testTime[0], testTime[1])
	'''

compareXML()
