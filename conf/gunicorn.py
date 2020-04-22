import multiprocessing

bind = '0.0.0.0:9080'
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 60 * 10
daemon = True

loglevel = 'debug'
errorlog = './pyrenees_gunicorn.log'
accesslog = './pyrenees_gunicorn_access.log'
