import logging
import os


# Completely reset default logging config
ROOT = logging.getLogger()
map(ROOT.removeHandler, list(ROOT.handlers))
map(ROOT.removeFilter, list(ROOT.handlers))


LOG_FORMAT = logging.Formatter(
        fmt='%(asctime)s %(levelname)s %(threadName)s %(name)s %(filename)s:%(lineno)d %(message)s',
        datefmt='%Y-%m-%d %H:%M:%SZ')


STDERR = logging.StreamHandler()
STDERR.setFormatter(LOG_FORMAT)
STDERR.setLevel(logging.DEBUG)
ROOT.addHandler(STDERR)

if bool(os.environ.get('KAMA_DEBUG', False)):
    ROOT.setLevel(logging.DEBUG)
else:
    ROOT.setLevel(logging.INFO)


def get_logger(name):
    log = logging.getLogger(name)
    return log
