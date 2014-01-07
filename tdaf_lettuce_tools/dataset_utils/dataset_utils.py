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
        Removes al the data elements tagged with the text [MISSING_PARAM] in lettuce
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
        Generate a fixed length param for elements tagged with the text [LENGTH] in lettuce
        :param param: Lettuce param
        :return param with the desired length
        """
        try:
            seeds = {'STRING': 'a', 'INTEGER': 1}
            if "_WITH_LENGTH_" in param:
                seed, length = param[1:len(data[item]) - 1].split("_WITH_LENGTH_")
                param = seeds[seed] * int(length)
        finally:
            return param

    def generate_fixed_length_params(self, data):
        """
        Generate a fixed length data for elements tagged with the text [LENGTH] in lettuce
        :param data: Lettuce step hash entry
        :return data with the desired params with the desired length
        """
        try:
            seeds = {'STRING': 'a', 'INTEGER': 1}
            for item in data.keys():
                if "_WITH_LENGTH_" in data[item]:
                    seed, length = data[item][1:len(data[item]) - 1].split("_WITH_LENGTH_")
                    data[item] = seeds[seed] * int(length)
        finally:
            return data

    def infere_datatypes(self, data):
        """
        Transformes data from string to primitive type
        :param data: Data to be transformed
        :return data with the correct type
        """

        """ Separate the process of lists, dicts and plain items"""
        try:

            if isinstance(data, dict):
                for item in data:
                    try:
                        data[item] = int(data[item])
                    except:
                        try:
                            _get_item_with_type(data[item])
                        except:
                            continue

            if isinstance(data, list):
                for item in range(1, len(data)):
                    try:
                        data[item] = int(data[item])
                    except:
                        try:
                            _get_item_with_type(data[item])
                        except:
                            continue

            if not isinstance(data, list) and not isinstance(data, dict):
                """ Assumption of single item """
                try:
                    data = int(data)
                except:
                        try:
                            _get_item_with_type(data)
                        except:
                            return data
        finally:
            return data

    def _get_item_with_type(self, data):
        """
        Generates the instances attributes dictionary from a list of keys and values in the lettuce step
        :param data: values to be parsed as boolean
        """
        try:
            if "[TRUE]" in data:
                data = True
            if "[FALSE]" in data:
                data = False
            else:
                data = float(data)
        finally:
            return data

