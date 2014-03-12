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
