# time_log by Oliver Rice


import time as t
from functools import wraps


class TimeLog:
    def __init__(self):
        self.class_list = []
        self.method_list = []
        self.class_length = None
        self.method_length = None

    def log_time(self, fn):
        @wraps(fn)
        def wrap(*args, **kwargs):
            s0 = t.perf_counter()
            result = fn(*args, **kwargs)
            print(f'{str(fn).split()[1].split(".")[0].rjust(self.class_length)}.'
                  f'{fn.__name__.ljust(self.method_length)}'
                  f' : completed in {round(t.perf_counter() - s0, 2)}s')
            return result
        return wrap

    def log_time_spacer(self, fn):
        @wraps(fn)
        def wrap(*args, **kwargs):
            s0 = t.perf_counter()
            result = fn(*args, **kwargs)
            print(f'{str(fn).split()[1].split(".")[0].rjust(self.class_length)}.'
                  f'{fn.__name__.ljust(self.method_length)}'
                  f' : completed in {round(t.perf_counter() - s0, 2)}s\n')
            return result
        return wrap

    def set_length(self):
        self.class_length = max(self.class_list)
        self.method_length = max(self.method_list)


if __name__ == '__main__':
    print('Running time_log')
