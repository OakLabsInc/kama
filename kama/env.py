# -*- coding: utf-8 -*-
import os

def get(keys, default=None):
    for key in keys:
        if key in os.environ:
            return os.environ[key]
    return default
