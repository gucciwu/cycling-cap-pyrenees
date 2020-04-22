def timer(func):
    import time
    import logging

    def wrapper(*args, **kwargs):
        start_time = time.time()
        f = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logging.debug("%f seconds used to execute function %s" % (duration, getattr(func, "__name__")))
        return f

    return wrapper
