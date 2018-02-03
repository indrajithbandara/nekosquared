#!/usr/bin/env python3.6

import importlib
ini = importlib.import_module('..nekosquared.engine.ini', '.')


with open('test.ini') as fp:
    data = ini.load(fp)

print(data)