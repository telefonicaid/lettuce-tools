'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''

import glob
from xml.dom import minidom


class ResultChecker(object):
    def __init__(self, directory):
        self.path = './testreport/' + directory + '/'
        self.test = 0
        self.failures = 0
        self.us = 0
        self.testcases = 0
        self.dict = {}  # Dict of key = US name and value = number of testcases

    def _get_files(self):
        filePattern = "".join([self.path, "*.xml"])
        files = glob.glob(filePattern)
        return files

    def get_results(self):
        """
        Parse lettuce reports files to get total results and metrics
        """
        for a_file in self._get_files():  # Iterate through files
            doc = minidom.parse(a_file)

            testsuite = doc.getElementsByTagName("testsuite")[0]

            """Count total UserStories"""
            uskey = (a_file.split('-', 1)[1]).rsplit('.', 1)[0]  # Remove e2e/component prefix (same US) and xml suffix
            if uskey not in self.dict:
                self.dict[uskey] = '0'

            # Print each file with its total tests and failures
            print a_file, testsuite.getAttribute("tests"), testsuite.getAttribute("failures")

            self.test += int(testsuite.getAttribute("tests"))  # Steps total
            self.failures += int(testsuite.getAttribute("failures"))  # Failed steps total
            old_classname = " "

            """Count total TestCases"""
            for testcase in doc.getElementsByTagName('testcase'):
                # Wrong number of TestCases are created into XML when working with simple scenarios
                # Count an scenario if its name starts with | (example) and only the first appearance
                # of an scenario which doesn't start with | (steps of a simple scenario)
                if testcase.attributes['classname'].value != old_classname or \
                    testcase.attributes['name'].value.startswith('|'):
                    old_classname = testcase.attributes['classname'].value
                    self.dict[uskey] = int(self.dict[uskey]) + 1
        print
        print "*********************************"
        print "OVERALL: Tests: %s Failures: %s" % (self.test, self.failures)
        freq = ""
        """Create Metrics from US dict"""
        for us in self.dict:
            self.testcases += int(self.dict[us])
            freq = ','.join([freq, str(self.dict[us])])
        self.us = len(self.dict)
        freq = freq[1:]
        print "Total US: %s Total TestCases: %s TestCases frequency: %s " % (self.us, self.testcases, freq)
        print "TestCases/US:" 
        for item in self.dict:
            print item+":"+str(self.dict[item])
        print "*********************************"
        if self.test == 0:
            return 1
        else:
            return self.failures


if __name__ == "__main__":
    checker = ResultChecker()
    checker.get_results()

