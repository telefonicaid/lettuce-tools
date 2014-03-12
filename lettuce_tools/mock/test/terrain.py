# -*- coding: utf-8 -*-
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
