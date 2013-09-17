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
import os
import re
from datetime import datetime
from copy import deepcopy

class LogUtils(object):

    TIMESTAMP = 'TIMESTAMP'
    LEVEL = 'LEVEL'
    CORRELATOR = 'CORRELATOR'
    TRANSACTION_ID = 'TRANSACTION_ID'
    OPERATION_TYPE = 'OPERATION_TYPE'
    MESSAGE = 'MESSAGE'

    ALLOWED_LEVEL_VALUES = ('FATAL', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE')

    def reset_logs(self, path, logs):
        """
        Delete logs given in param 'logs'.
        """
        for log in logs:
            os.remove(path + log)

    def check_log_format(self, path, log):
        """
        Check that the format of the log entries, the dates and the levels is valid
        """
        with open(path + log) as log_file:
            for line in log_file:
                try:
                    [date, machine, component, level, trace_id, user_id, op_type, message] = line.split(' | ')
                    try:
                        datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%fZ")
                    except ValueError:
                        assert False, "DATE field has bad format: %s" % date
                    assert level in self.ALLOWED_LEVEL_VALUES, \
                        "LEVEL field value not allowed: %s" % level
                except ValueError:
                    assert False, "Log entry has wrong format: %s" % line

    def search_in_log(self, path, log, params):
        """
        Search for the first entry in the log that matches the given parameters
        """
        parsed_log = self._parse_log(path, log)
        for log_line in parsed_log:
            result_found = True
            for param in params:
                if param == self.MESSAGE:
                    if not (re.search(params[param], log_line[param])):
                        result_found = False
                        break
                else:
                    if not (params[param] == log_line[param]):
                        result_found = False
                        break
            if result_found:
                return log_line
        assert False, "Log not found with parameters %s" % params

    def _parse_log(self, path, log, lines='all'):
        """
        Return the entire log or just the last lines as an array of dictionaries
        """
        with open(path + log) as log_file:
            if lines != 'all':
                lines_to_parse = log_file.readlines()[-lines:]
            else:
                lines_to_parse = log_file.readlines()
            parsed_log = []
            parsed_line = {}
            for line in lines_to_parse:
                [parsed_line[self.TIMESTAMP],
                 parsed_line[self.LEVEL],
                 parsed_line[self.CORRELATOR],
                 parsed_line[self.TRANSACTION_ID],
                 parsed_line[self.OPERATION_TYPE],
                 parsed_line[self.MESSAGE]] = line.split(' | ')
                parsed_log.append(deepcopy(parsed_line))
            return parsed_log
