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
import json


class DatasetUtils(object):

    def prepare_data(self, data):
        """
        Generate a fixed length data for elements tagged with the text [LENGTH] in lettuce
        Removes al the data elements tagged with the text [MISSING_PARAM] in lettuce
        Transformes data from string to primitive type
        :param data: hash entry
        :return cleaned data
        """
        try:
            data = self.generate_fixed_length_params(data)
            data = self.remove_missing_params(data)
            data = self.infere_datatypes(data)
            return data
        except:
            return None

    def remove_missing_params(self, data):
        """
        Removes all the data elements tagged with the text [MISSING_PARAM] in lettuce
        :param data: Lettuce step hash entry
        :return data without not desired params
        """
        try:
            for item in data.keys():
                if "[MISSING_PARAM]" in data[item]:
                    del(data[item])
        finally:
            return data

    def generate_fixed_length_param(self, param):
        """
        Generate a fixed length param if the elements matches the expression
        [<type>_WITH_LENGTH_<length>] in lettuce. E.g.: [STRING_WITH_LENTGH_15]
        :param param: Lettuce param
        :return param with the desired length
        """
        try:
            if "_WITH_LENGTH_" in param:
                if "_ARRAY_WITH_LENGTH_" in param:
                    seeds = {'STRING': 'a', 'INTEGER': 1}
                    seed, length = param[1:-1].split("_ARRAY_WITH_LENGTH_")
                    param = list(seeds[seed] for x in xrange(int(length)))
                elif "JSON_WITH_LENGTH_" in param:
                    length = param[1:-1].split("JSON_WITH_LENGTH_")[1]
                    param = dict((str(x), str(x)) for x in xrange(int(length)))
                else:
                    seeds = {'STRING': 'a', 'INTEGER': 1}
                    seed, length = param[1:-1].split("_WITH_LENGTH_")
                    param = seeds[seed] * int(length)
        finally:
            return param

    def generate_fixed_length_params(self, data):
        """
        Generate a fixed length data for the elements that match the expression
        [<type>_WITH_LENGTH_<length>] in lettuce. E.g.: [STRING_WITH_LENTGH_15]
        :param data: Lettuce step hash entry
        :return data with the desired params with the desired length
        """
        try:
            for item in data.keys():
                data[item] = self.generate_fixed_length_param(data[item])
        finally:
            return data

    def infere_datatypes(self, data):
        """
        Process the input data and replace the values in string format with the
        the appropriate primitive type, based on its content
        :param data: list of items, dict of items or single item
        :return processed list of items, dict of items or single item
        """

        """ Separate the process of lists, dicts and plain items"""
        try:

            if isinstance(data, dict):  # dict of items
                for item in data:
                    data[item] = self._get_item_with_type(data[item])

            elif isinstance(data, list):  # list of items
                for pos in range(len(data)):
                    data[pos] = self._get_item_with_type(data[pos])

            else:  # single item
                data = self._get_item_with_type(data)
        finally:
            return data

    def _get_item_with_type(self, data):
        """
        Transform data from string to primitive type
        :param data: Data to be transformed
        :return data with the correct type
        """
        if "[TRUE]" in data:  # boolean
            data = True
        elif "[FALSE]" in data:  # boolean
            data = False
        elif data.startswith("{") and data.endswith("}"):  # json
            data = json.loads(data)
        else:
            try:  # maybe an int
                data = int(data)
            except:
                try:  # maybe a float
                    data = float(data)
                except:
                    pass  # if no condition matches, leave the data unchanged
        return data
