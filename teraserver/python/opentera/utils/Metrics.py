import time
import inspect


def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        exec_time = (time2-time1)*1000.0
        if exec_time > 200:
            print("WARNING: %s: %s took %0.3f ms" % (f.__module__, f.__name__, exec_time))
        return ret
    return wrap


# Will not play well with @staticmethod and @classmethod for now...
def timing_for_all_methods(cls):
    for name, method in inspect.getmembers(cls):
        if (not inspect.ismethod(method) and not inspect.isfunction(method)) or inspect.isbuiltin(method) \
                or method.__name__ == '__init__':
            continue
        # print("Decorating function %s" % name)
        setattr(cls, name, timing(method))
    return cls
