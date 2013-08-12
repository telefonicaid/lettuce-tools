'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''

import os
from check_results import ResultChecker
import argparse
import shutil
from datetime import datetime
import re
import sys
from lettuce.bin import main as lettucelaunch

jira = False


def copyfile(src, dst):
    try:
        print "SRC"
        print src
        print "DST"
        print dst
        shutil.copy(src, dst)        
    except:
        print "Error in file copy"


def create_report_dir(formatedtime):
    if not os.path.exists("./testreport/" + formatedtime):
        os.makedirs("./testreport/" + formatedtime)
    return "./testreport/" + formatedtime


def execute_test(path, xunit_file, tags):
    global jira
    os.system("lettuce" + tags + " --with-xunit --xunit-file=" + xunit_file + " " + path + " " + str(jira))
    #lettucelaunch(["--with-xunit", "--xunit-file=" + xunit_file, path, str(jira)])


def run_tests(test_type, epics, features, formatedtime, jirasync, tags):
    """
    Iterate through directory and execute given testsuites, epics and features
    with or without jira synchronization.
    """
    print("Running %s Tests" % test_type)
    print features
    for root, dirs, list_files in os.walk("./" + test_type + "/"):
        for files in list_files:
            if files.endswith(".feature"):
                for epic in epics:
                    if  epic + "\\" in root or epic + "/" in root or "all" == epic:
                        for feature in features:
                            if files.startswith(feature) or "all" == feature:
                                if jirasync:  # Jira synchronization (testcase publication)
                                    os.system("jirasync " + root)
                                root_scheme = re.split("\\\\|/", root)
                                root_scheme.pop()
                                rootepic = root_scheme.pop()
                                execute_test(root + "/" + files, create_report_dir(formatedtime) + "/" + test_type \
                                             + "-" + rootepic + "--" + files.split(".").pop(0) + ".xml", tags)


def main(args=sys.argv[1:]):

    """ Parse arguments provided in letucetdaf.py command"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-js", "--jirasync", help="Defines the synchronization scheme with Jira. Synchronize files, \
                        publish results in jira or all mixed", default="none", choices=["none", "sync", "pub", "all"])
    parser.add_argument("-ep", "--epics", help="Defines the epics to be tested separated by commas. \
                        Use all for complete test", default="all")
    parser.add_argument("-tg", "--tags", help="Defines the tags to be tested separated by commas.", default="")
    parser.add_argument("-ft", "--features", help="Defines the features to be testeds separated by commas. \
                        Use all to test them all", default="all")
    parser.add_argument("-en", "--environment", help="Defines the environment to execute test (e.g. dev, int,...)",
                        default="dev")
    parser.add_argument("-ts", "--testsuite", help="Selects the testsuite", default="all", \
                        choices=["comp", "int", "e2e", "all"])
    parser.add_argument("-tm", "--timestamp", help="Stores the results in timestamped folders", action="store_true")
    args = parser.parse_args()

    epics = []
    timestamp = ""
    tags = ""

    if args.timestamp:  # Stores the results in timestamped folders
        timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    if args.jirasync == "pub" or args.jirasync == "all":  # Publish testcase execution in Jira
        jira = True
    if args.tags:
        for item in args.tags.split(","):
            tags = "".join([tags, " --tag=", item])
    if args.jirasync == "sync" or args.jirasync == "all":  # Create testcases for each scenario in Jira
        jirasync = True
    else:
        jirasync = False
    if args.epics:
        epics = args.epics.split(",")  # Epics to be executed
    if args.environment:
        copyfile("./settings/" + args.environment + "-properties.json", "./properties.json")  # Get env properties
    if args.features:
        features = args.features.split(",")  # Features to be executed

    if  ("comp" in args.testsuite or "all" in args.testsuite):  # Execute components testsuite
            run_tests("component", epics, features, timestamp, jirasync, tags)

    if  ("e2e" in args.testsuite or "all"in args.testsuite):  # Execute e2e testsuite
            run_tests("e2e", epics, features, timestamp, jirasync, tags)

    if  ("int" in args.testsuite or "all"in args.testsuite):  # Execute integration testsuite
            run_tests("integration", epics, features, timestamp, jirasync, tags)

    try:
        failures = ResultChecker(timestamp).get_results()  # Create lettuce reports
        exit(failures)
    except:
        print "There has not been generated any lettuce report"
        exit(1)

    if __name__ == "__main__":
        main()
