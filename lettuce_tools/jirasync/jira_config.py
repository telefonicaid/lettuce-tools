import requests
import json
import re
import argparse
from lettuce import world
import traceback


def jira(status):
    """
    Jira decorator for executing Jira testcases
    Saves execution status in case a step fails.
    Usage: Add it to every step in terrain.py
    - @jira("Impeded") for prerequisites or procedure steps
    - @jira("Failed") for result steps
    """

    def wrapper(f):
        def save_status(*args, **kwargs):
            try:
                r = f(*args, **kwargs)
            except Exception, e:
                world.jiraStatus = status
                world.exception = traceback.format_exc()
                raise e
            return r
        return save_status
    return wrapper


class Jira_Config:
    """
    Class for Jira synchronization, testcase publication, linking and execution
    """

    jirabase_url = "https://jirapdi.tid.es"
    restapi_url = "/rest/api/2"
    server_base_url = jirabase_url + restapi_url

    def __init__(self, id_project, id_component, id_user, id_password):

        self.project = id_project
        self.session = requests.Session()
        self.session.auth = (id_user, id_password)
        self.session.headers.update({'x-test': 'true'})

        """Find component id from its name, necessary for API requests"""
        resp = self.session.get(self.server_base_url + "/project/" + self.project + "/components", \
                                headers={'x-test2': 'true'}, verify=False)
        data = json.loads(resp.content)
        for item in data:
            if item["name"] == id_component:
                self.component_id = item["id"]

        try:
            self.component_id
        except:
            assert False, "Component %s of project %s does not exist. " % (id_component, id_project)

    def to_dic(self, a_list):
        """
        function to_dic transform json with list into dictionaries to be process
        easily
        """

        dic = {}
        for item in a_list:
            if type(a_list) is list:
                dic.update(item)
            if type(a_list) is dict:
                dic = dict(dic.items() + a_list.items())
        return dic

    def get_feature(self, jira_key):

        description = ""
        sumary = ""

        try:
            resp = self.session.get(self.server_base_url + "/issue/" + jira_key, \
                                    headers={'x-test2': 'true'}, verify=False)
            data = json.loads(resp.content)
            description = (self.to_dic(data["fields"])["description"])
            sumary = (self.to_dic(data["fields"])["summary"])
        except:
            print(" No connection to Jira get, using mock")

        return [sumary, description]

    def publish_testcase(self, scenario, test_key):
        """
        Testcase Publication: It takes feature info to fill Jira fields
        - Pre-requisites field: "Given" steps
        - Procedure: "When" steps
        - Expected result: "Then" steps
        - Dataset: Examples
        - Description: All steps
        """

        summary = (scenario.pop(0).split(":")[1]).replace("\n", "")

        """Check whether its a simple scenario (no examples) or a complex one"""
        try:
            [description, dataset] = ("".join(scenario)).replace("\t", "").split("Examples:")
            print("\t\t Complex scenario with dataset")
        except:
            print("\t\t Simple scenario without dataset")
            dataset = ""
            description = ("".join(scenario)).replace("\t", "")

        """Split whole scenario into prerrequisites, procedure and result"""
        description_parts = re.search("(Given.*)(When.*)(Then.*)", description, flags=re.DOTALL)
        prerequisites = description_parts.group(1)    # 0 is the whole expression
        procedure = description_parts.group(2)
        result = description_parts.group(3)

        if(test_key is ""):  # New Scenario to be published as a TestCase

            print("\t\t Publishing scenario (" + summary + ")")
            payload = {"fields":  {"project": {"key": self.project}, "components": [{"id": self.component_id}], \
                                   "summary": summary, "description": description, "customfield_10070": prerequisites,\
                                   "customfield_10071": procedure, "customfield_10072": result, "customfield_10153": \
                                   dataset, "issuetype": {"name": "Test Case"}}}

            try:
                resp = self.session.post(self.server_base_url + "/issue/", \
                                         headers={'x-test2': 'true', 'Content-Type': 'application/json'}, \
                                         verify=False, data=json.dumps(payload))
                data = json.loads(resp.content)
            except:
                print("No connection to Jira post, usign mock")
                return self.project + "-1"

            return data["key"]

        else:  # A TestCase already exists for this scenario
            print("\t\t Updating scenario (" + summary + ")")
            payload = {"fields":  {"summary": summary.split("_" + self.project)[0], "components": \
                                   [{"id":self.component_id}], "description": description, "customfield_10070": \
                                   prerequisites, "customfield_10071": procedure, "customfield_10072": result, \
                                   "customfield_10153": dataset}}
            resp = self.session.put(self.server_base_url + "/issue/" + test_key, \
                                    headers={'x-test2': 'true', 'Content-Type': 'application/json'},\
                                    verify=False, data=json.dumps(payload))

    def link_testcases(self, scenarios_key, user_story_key):
        """
        Links new TestCases to corresponding UserStories
        """

        for item in scenarios_key:

            try:
                payload = {"type": {"name": "Tests"}, "inwardIssue": {"key": user_story_key}, \
                           "outwardIssue": {"key": item}}
                self.session.post(self.server_base_url + "/issueLink", \
                                  headers={'x-test2': 'true', 'Content-Type': 'application/json'}, verify=False, \
                                  data=json.dumps(payload))
            except:
                print(" No connection to Jira post, usign mock link")

        return True

    def check_update_jira(self):
        """
        Parse lettuce own arguments and include jira argument detection
        """

        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbosity",
                            dest="verbosity",
                            default=4,
                            help='The verbosity level')
        parser.add_argument("-s", "--scenarios",
                            dest="scenarios",
                            default=None,
                            help='Comma separated list of scenarios to run')
        parser.add_argument("-t", "--tag",
                            dest="tags",
                            default=None,
                            action='append',
                            help='Tells lettuce to run the specified tags only; '
                            'can be used multiple times to define more tags'
                            '(prefixing tags with "-" will exclude them and '
                            'prefixing with "~" will match approximate words)')
        parser.add_argument("-r", "--random",
                            dest="random",
                            action="store_true",
                            default=False,
                            help="Run scenarios in a more random order to avoid interference")
        parser.add_argument("--with-xunit",
                            dest="enable_xunit",
                            action="store_true",
                            default=False,
                            help='Output JUnit XML test results to a file')
        parser.add_argument("--xunit-file",
                            dest="xunit_file",
                            default=None,
                            type=str,
                            help='Write JUnit XML to this file. Defaults to '
                            'lettucetests.xml')
        parser.add_argument("--failfast",
                            dest="failfast",
                            default=False,
                            action="store_true",
                            help='Stop running in the first failure')
        parser.add_argument("--pdb",
                            dest="auto_pdb",
                            default=False,
                            action="store_true",
                            help='Launches an interactive debugger upon error')
        parser.add_argument('root')
        parser.add_argument('jira')
        args = parser.parse_args()

        return args

    def execute_testcase(self, test_id, status):
        """
        Create or updates TestCase executions in case Jira option is enabled
        """

        Jira = self.check_update_jira().jira
        if Jira:  # Jira is enabled
            print ("Execute testcase " + test_id + " with status " + status)

            """Get last TestCase Execution id and status"""
            resp = self.session.get(self.server_base_url + "/issue/" + test_id, headers={'x-test2': 'true'}, \
                                    verify=False)
            data = json.loads(resp.content)
            testcase = data["fields"]["subtasks"].pop()
            testcase_exec = testcase["key"]
            testcase_exec_status = testcase["fields"]["status"]["name"]

            if testcase_exec_status != (status):  # New execution status != Last execution status -> new tc execution
                #print "Different statuses: "+testcase_exec_status +" "+ status

                """Create new TestCase execution"""
                payload = {"transition": {"id": "31"}}
                resp = self.session.post(self.server_base_url + "/issue/" + test_id + \
                                         "/transitions?expand=transitions.fields", \
                                         headers={'x-test2': 'true', 'Content-Type': 'application/json'}, \
                                         verify=False, data=json.dumps(payload))
                resp = self.session.get(self.server_base_url + "/issue/" + test_id, headers={'x-test2': 'true'}, \
                                        verify=False)
                data = json.loads(resp.content)
                testcase_exec = (data["fields"]["subtasks"].pop())["key"]

                """Set status for new TestCase execution"""
                if status == "Passed":
                    payload = {"transition": {"id": "21"}}
                else:  # If status is Failed or Impeded, fill Jira description with exception trace
                    payload = {"fields": {"description": world.exception}}
                    resp = self.session.put(self.server_base_url + "/issue/" + testcase_exec, \
                                            headers={'x-test2': 'true', 'Content-Type': 'application/json'}, \
                                            verify=False, data=json.dumps(payload))
                    if status == "Failed":
                        payload = {"transition": {"id": "11"}}
                    elif status == "Impeded":
                        payload = {"transition": {"id": "51"}}
                resp = self.session.post(self.server_base_url + "/issue/" + testcase_exec + \
                                         "/transitions?expand=transitions.fields", \
                                         headers={'x-test2': 'true', 'Content-Type': 'application/json'}, \
                                         verify=False, data=json.dumps(payload))

            else:  # New execution status == Last execution status -> Update last testcase execution
                #print "Same statuses: "+testcase_exec_status +" "+ status
                payload = {"fields": {}}
                if status == "Failed" or status == "Impeded":
                    payload = {"fields": {"description": world.exception}}
                resp = self.session.put(self.server_base_url + "/issue/" + testcase_exec, \
                                        headers={'x-test2': 'true', 'Content-Type': 'application/json'}, \
                                        verify=False, data=json.dumps(payload))
