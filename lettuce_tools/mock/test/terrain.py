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
from lettuce import before, after
from test_utils import TestUtils
from mock.mock_utils import MockUtils

test_utils = TestUtils()
mock_utils = MockUtils()


@before.all
def before_all():
    test_utils.initialize()
    mock_utils.start_mock()

@after.all
def after_all(total):
    mock_utils.stop_mock()
