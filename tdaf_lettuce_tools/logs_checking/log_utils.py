# -*- coding: utf-8 -*-
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
from e2e.common.sd_utils import SDUtils
from copy import deepcopy

sd_utils = SDUtils()


class LogUtils(object):

    LOG_TAG = {'TIME': 'time=', 'LEVEL': 'lvl=', 'UNICA_CORRELATOR': 'corr=', \
              'TRANSACTION_ID': 'trans=', 'OPERATION_TYPE': 'op=', 'MESSAGE': 'msg='}
  
    ALLOWED_LEVEL_VALUES = ('FATAL', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE')

    def reset_logs(self, path, logs):
        """
        Delete logs given in param 'logs'.
        """
        try:
            for log in logs:
                os.remove(path + log)
        except:
            print "Error deleting logs"

    def check_log_format(self, path, log):
        """
        Check that the format of the log entries, the dates and the levels is valid
        """

        with open(path + "service_directory.log") as log_file:
            for line in log_file:
                try:
                    for item in line.split(' | '):
                        if self.LOG_TAG["TIME"] in item:
                            try:
                                datetime.strptime(item.replace(self.LOG_TAG["TIME"], ""), "%Y-%m-%d %H:%M:%S.%fZ")
                            except ValueError:
                                assert False, "DATE field has bad format: %s" % item.replace(self.LOG_TAG["TIME"], "")
                        if self.LOG_TAG["LEVEL"] in item:
                            assert item.replace(self.LOG_TAG["LEVEL"], "") in self.ALLOWED_LEVEL_VALUES, \
                            "LEVEL field value not allowed: %s" % item.replace(self.LOG_TAG["LEVEL"], "")
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
                if param == "MESSAGE" or param == "UNICA_CORRELATOR" or param == "TRANSACTION_ID" :
                    if not (re.search(params[param].split("=")[1], log_line[self.LOG_TAG[param].replace("=", "")])):
                        result_found = False
                        break
                else:
                    if not (params[param].split("=")[1] == log_line[self.LOG_TAG[param].replace("=", "")]):
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
                for item in line.split(' | '):
                    parsed_line[item.split('=')[0]] = item.split('=')[1]
                parsed_log.append(deepcopy(parsed_line))
            return parsed_log
