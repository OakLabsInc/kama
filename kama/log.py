import logging
import os


LOG_FORMAT = logging.Formatter(
        fmt='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%SZ')


STDERR = logging.StreamHandler()
STDERR.setFormatter(LOG_FORMAT)
STDERR.setLevel(logging.DEBUG)


def get_logger(name):
    log = logging.getLogger(name)
    if bool(os.environ.get('KAMA_DEBUG', False)):
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    log.addHandler(STDERR)
    return log
