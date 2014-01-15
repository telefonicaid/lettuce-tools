'''
(c) Copyright 2013 Telefonica, I+D. Printed in Spain (Europe). All Rights
Reserved.

The copyright to the software program(s) is property of Telefonica I+D.
The program(s) may be used and or copied only with the express written
consent of Telefonica I+D or in accordance with the terms and conditions
stipulated in the agreement/contract under which the program(s) have
been supplied.
'''

from functools import wraps
from dataset_utils import DatasetUtils


def auto_expand(f):
    '''Automation of the detection and execution of the fixed length pattern'''
    @wraps(f)
    def wrapper(*args, **kwargs):
        dataset_utils = DatasetUtils()
        args = map(dataset_utils.generate_fixed_length_param, args)
        kwargs.update(dataset_utils.generate_fixed_length_params(kwargs))
        return f(*args, **kwargs)
    return wrapper


@auto_expand
def test(arg1, arg2, arg3):
    print 'arg1', arg1
    print 'arg2', arg2
    print 'arg3', arg3


if __name__ == '__main__':
    test('[STRING_WITH_LENGTH_5]',
         arg3='standard chain',
         arg2='[STRING_WITH_LENGTH_10]')
