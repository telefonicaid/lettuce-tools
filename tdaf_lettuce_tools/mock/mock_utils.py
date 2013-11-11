# -*- coding: utf-8 -*-
'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''
from lettuce import world
from string import Template
import subprocess
import time
import requests
import json


class MockUtils(object):

    def start_mock(self):
        """
        Start the mock if not already started and store the process in the world.
        """
        if not hasattr(world, "mock_working") or world.mock_working == False:
            run_command = " ".join([world.config["environment"]["python_alias"],
                                   world.config["mock"]["run_command_params"]])
            out = open(world.config["mock"]["out_file"], 'w')
            err = open(world.config["mock"]["err_file"], 'w')
            world.mock_process = subprocess.Popen(run_command.split(), stdout=out, stderr=err)
            time.sleep(1)
            world.mock_working = True

    def stop_mock(self):
        """
        Stop the mock if not already stopped.
        """
        if hasattr(world, "mock_working") and world.mock_working == True:
            world.mock_process.terminate()
            time.sleep(0.5)
            world.mock_working = False

    def mock_is_working(self):
        """
        Check whether the mock is working
        """
        if hasattr(world, "mock_working") and world.mock_working == True:
            return True
        else:
            return False

    def set_invalid_data(self, type,  request, status_code, delay=None):
        """
        Configure the mock to give a bad answer to a request.
        :param request: Path in the request line that will trigger the response.
        :param type: Status code of the response to be sent.
        :param delay: Time the mock should wait before sending the response.
        """
        if type == "[BAD_DATA]":
            body = "really bad data"

        if type == "[EMPTY_DATA]":
            body = ""

        if type == "[BLANK_DATA]":
            body = " "

        if type == "[CORRUPT_DATA]":
            body = "@#~ñ"

        headers = dict()
        headers.update({"Content-Type": "application/json"})
        headers.update({"Content-Length": str(len(json.dumps(body)))})
        response_info = dict()
        response_info.update({"status_code": int(status_code)})
        response_info.update({"headers": headers})
        response_info.update({"body": body})
        if delay != None:
            """If the response has to be given with delay, set the parameter."""
            response_info.update({"delay": int(delay)})

        """Send the configuration request to the mock."""
        url = "".join([world.config["mock"]["base_url"], "/mock_configurations/", request])
        try:
            requests.post(url, json.dumps(response_info))
        except:
            assert False, "Error configuring the mock. URL: %s. Data: %s" \
                % (url, response_info)

    def get_request_and_send_response_of_type_with_data(self, step, request,
                                                        status_code,
                                                        response_index=None,
                                                        delay=None):
        """
        Configure the mock to give a specific answer to a request.
        :param step: Current Lettuce step.
        :param request: Path in the request line that will trigger the response.
        :param type: Status code of the response to be sent.
        :param response_index: Index of the data to be sent as response content.
        :param delay: Time the mock should wait before sending the response.
        """

        """Build the response information based on the data provided."""
        if response_index != None:
            """If the index is provided, set just the row specified as body"""
            body = step.hashes[int(response_index)]
            """ Format the step values when they contain json values """
            """ If attributes in expected body, transform them into json """
            try:
                body["attributes"] = json.loads(body["attributes"])
            except:
                pass
            """ If binding tules in expected body, transform them into json """
            try:
                body["binding_rules"] = json.loads(body["binding_rules"])
            except:
                pass
        else:
            """If the index is not provided, set the full table as body"""
            body = step.hashes

            for item in body:
                """ Format the step values when they contain json values """
                """ If attributes in expected body, transform them into json """
                try:
                    item["attributes"] = json.loads(item["attributes"])
                except:
                    pass
                """ If binding tules in expected body, transform them into json """
                try:
                    item["binding_rules"] = json.loads(item["binding_rules"])
                except:
                    pass

        headers = dict()
        headers.update({"Content-Type": "application/json"})
        response_info = dict()
        response_info.update({"status_code": int(status_code)})
        response_info.update({"headers": headers})

        if len(body) != 0 or body == []:
            headers.update({"Content-Length": str(len(json.dumps(body)))})
            response_info.update({"body": body})
        if delay != None:
            """If the response has to be given with delay, set the parameter."""
            response_info.update({"delay": int(delay)})

        """Send the configuration request to the mock."""
        url = "".join([world.config["mock"]["base_url"], "/mock_configurations/", request])
        try:
            requests.post(url, json.dumps(response_info))
        except:
            assert False, "Error configuring the mock. URL: %s. Data: %s" \
                % (url, response_info)

    def validate_stored_request(self, request, params=None, body_data=None):
        """
        Validates de data stores in the mock .
        :param request: URL template to set the corresponding values.
        :param data: Values to be validated
        """
        url = "".join([world.config["mock"]["base_url"], "/mock_configurations/", request])
        try:
            response = requests.get(url)
        except:
            assert False, "Error getting stored info from mock."

        try:
            world.mock_json = response.json()
            world.mock_params = response.json()["query_params"]
            world.mock_body = response.json()["body"]
        except:
            assert False, "Error getting stored info from mock."

        assert response.status_code == 200, "Error getting stored info from mock."

        """ params validation """
        if params != None:
            assert len(params) == len(world.mock_params.split("&")), \
            "The number of expected and send params is different. Expected %s Received %s" % (params, world.mock_params.split("&"))

            for item in world.mock_params.split("&"):
                assert item in params.values(), \
            "Item %s was not found in expected params %s" % (item, params)

        if body_data != None:
            """ If attributes in expected body, transform them into json """
            try:
                body_data["attributes"] = json.loads(body_data["attributes"])
            except:
                pass
            """ If binding tules in expected body, transform them into json """
            try:
                body_data["binding_rules"] = json.loads(body_data["binding_rules"])
            except:
                pass

            assert len(body_data) == len(json.loads(world.mock_body)), \
            "The number of expected and send params is different. Expected %s Received %s" % (body_data,json.loads(world.mock_body))


            assert body_data == json.loads(world.mock_body), \
            "The expected body and received body are different. Expected %s, Received %s" % (body_data, world.mock_body)
