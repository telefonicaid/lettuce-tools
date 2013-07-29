import re
from colorama import Fore, init, AnsiToWin32
from jira_config import Jira_Config
import sys


def update_feature(root, files, jira_project):

    init(wrap=False)
    stream = AnsiToWin32(sys.stderr).stream

    print >>stream, Fore.BLUE + "Updating feature in file" + files + " ...\n"

    header = []
    old_feature = []
    data_feature = []
    counter = 0

    # issueKey extraction from the file name. Character _ is used as a separator
    user_story_key = jira_project.project + (files.split(".",).pop(0)).split("_" + jira_project.project).pop(1)

    # Jira issue download and summary, description set up
    feature = jira_project.get_feature(user_story_key)
    summary = feature[0]
    description = feature[1]

    # Open the file, create the data_feature and remove the header and the feature description leaving just
    # the scenarios description
    try:
        with open(root + "/" + files, mode="r") as toupdate_feature:

            for readline in toupdate_feature:

                    data_feature.append(readline)

            # Look for the header
            for item in data_feature:
                if "Feature" in item:
                    break
                counter = counter + 1

            header = data_feature[0:counter]

            for item in range(counter):
                data_feature.pop(0)
            # Look for the old feature info
            counter = 0

            for item in data_feature:
                if "Scenario" in item:
                    break
                counter = counter + 1

            old_feature = data_feature[0:counter]

            for item in range(counter):

                data_feature.pop(0)

    except:
        print >>stream, Fore.RED + "Error de carga de archivo"

    # Publish all the test cases not published before in Jira

    scenarios_key = update_testcases(data_feature, [], jira_project)

    # Creates links in Jira between Test cases and User Stories

    jira_project.link_testcases(scenarios_key, user_story_key)

    # Process the feature description and removes html formating elements

    sain_feature = sanitize_feature(description)

    # Compose updated feature with the information downloaded from jira
    if not (summary and sain_feature):
        # Keep the current feature if there were problems getting it from Jira
        old_feature.extend(data_feature)
        header.extend(old_feature)
        ready_feature = header

    else:
        ready_feature = compose_feature(header, sain_feature, data_feature, summary)
    try:
        with open(root + "/" + files, mode="w") as toupdate_feature:

            toupdate_feature.truncate()
            toupdate_feature.seek(0)

            for writeline in ready_feature:
                if "Scenario" in writeline and not not scenarios_key and \
                writeline.find(jira_project.project + "-") == -1:
                    writeline = writeline.replace("\n", "") + "_" + scenarios_key.pop(0) + "\n"
                toupdate_feature.write(writeline)
            toupdate_feature.flush()
    except:
        print >>stream, Fore.RED + "Error de escritura de archivo"
    print >>stream, Fore.GREEN + "\t\tIssue: " + user_story_key + " has been updated \n"


def sanitize_feature(feature):

    """ Removes html formating characters and aligns the information contained in the feature"""

    feature = feature.replace("<br />", "\n")
    feature = feature.replace("</p>", "\n")
    feature = re.sub(r'<[^>]*?>', '', feature)  # remove the rest of the html tags
    featuresplit = feature.splitlines()
    sanitized = ["\t" + item + '\n' for item in featuresplit if item != ""]
    return sanitized


def compose_feature(header, sain_feature, scenarios, summary):

    """ Composes feature file with the header, the information updated from Jira, the sanitized feature
    description and the scenarios"""

    sain_feature.insert(0, "Feature: " + summary + "\n\n")
    sain_feature.append(" \n")
    sain_feature.extend(scenarios)
    header.extend(sain_feature)

    return header


def update_testcases(pending_scenarios, scenarios_key, jira_project):

    init(wrap=False)
    stream = AnsiToWin32(sys.stderr).stream

    scenario_counter = 0
    scenario = []
    scenarios = []
    scenarios.extend(pending_scenarios)

    # Start the scenario with first "Scenario definition" in the list

    try:
        scenario.append(scenarios.pop(0))

        for item in scenarios:
            if ("Scenario") in item:
                break
            scenario_counter = scenario_counter + 1

        for item in range(scenario_counter):
                    scenario.append(scenarios.pop(0))

        #check if the Test case has been published previously based on the issue key and requests the publication

        try:
            test_key = jira_project.project + (scenario[0].split("_" + jira_project.project)[1]).replace("\n", "")
            print >>stream, Fore.MAGENTA + "\t Scenario detected to be updated" + Fore.YELLOW
            jira_project.publish_testcase(scenario, test_key)
        except:
            print >>stream, Fore.MAGENTA + "\t Scenario detected to be published" + Fore.YELLOW
            scenarios_key.append(jira_project.publish_testcase(scenario, ""))

        update_testcases(scenarios, scenarios_key, jira_project)

    except:

        print >>stream, Fore.WHITE + "\t No more scenarios to be processed \n"

    return scenarios_key
