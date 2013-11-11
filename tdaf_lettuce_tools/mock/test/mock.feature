# -*- coding: utf-8 -*-
Feature: TDAF Mock tests

         TDAF Mock  test suite
 
    Scenario Outline: Configure and consume GET request
        Given the mock is alive
        When I configure the mock in <url> to answer with <status_code> and <body>
        And I request the mock with a GET to <url>
        Then I receive <status_code> and <body>
        And I check the mock has been called in <url>
        And the mock queues are empty
        Examples:
            | url   | status_code | body             |
            | /test | 315         | {"name": "test"} |

