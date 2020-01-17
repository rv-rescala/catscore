import time

def calc_time(message=''):
    def _calc_time(func):
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kargs):
            start = time.time()
            ret = func(*args, **kargs)
            print(f'{func.__name__} executing time : {time.time() - start:0.4} sec')
            return ret
        return wrapper
    return _calc_time