# -*- coding: utf-8 -*-
from lettuce import step, world
from mock.mock_utils import MockUtils
from dataset_utils.dataset_utils import DatasetUtils
import requests
import json

mock_utils = MockUtils()
dataset_utils = DatasetUtils()

@step(u'the mock is alive')
def the_mock_is_alive(step):
    mock_utils.start_mock()


@step(u'I configure the mock in (.*) to answer with (.*) and (.*)')
def i_configure_the_mock_in_url_to_answer_with_status_and_body(step, url, status, body):
    url = world.config["mock"]["base_url"] + "/mock_configurations" + url

    headers = dict()
    headers.update({"Content-Type": "application/json"})
    body = dataset_utils.infere_datatypes(body)
    headers.update({"Content-Length": str(len(json.dumps(body)))})

    response_info = dict()
    response_info.update({"status_code": int(status)})
    response_info.update({"headers": headers})

    response_info.update({"body": body})

    requests.post(url, json.dumps(response_info))


@step(u'I request the mock with a GET to (.*)')
def i_request_the_mock_with_a_get_to_url(step, url):
    url = world.config["mock"]["base_url"] + url
    world.res = requests.get(url)


@step(u'I receive (.*) and (.*)')
def i_receive_status_and_body(step, status_code, body):
    assert int(status_code) == world.res.status_code, \
        "Response http code received [%s] is different to the http code expected [%s] " \
        % (world.res.status_code, status_code)
    assert body == world.res.text, \
        "Response body received [%s] is different to the body expected [%s] " \
        % (world.res.text, body)


@step(u'I check the mock has been called in (.*) with a (.*)')
def check_the_mock_has_been_called_with_a_get(step, url, method):
    url = world.config["mock"]["base_url"] + "/mock_configurations" + url
    res = requests.get(url)
    assert res.status_code == 200, \
        "Response status code received [%s] is different to the status code expected [%s] " \
        % (res.status_code, "200")
    assert json.loads(res.text)["method"] == method, \
        "Response method received [%s] is different to the method expected [%s] " \
        % (json.loads(res.text)["method"], method)


@step(u'the mock queues are empty')
def the_mock_queues_are_empty(step):
    url = world.config["mock"]["base_url"] + "/queues"
    res = requests.get(url)

