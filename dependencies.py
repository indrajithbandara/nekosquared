#!/usr/bin/env python3.6
"""
This script acts as a resource to be imported by setup.py, and as a standalone
runnable. If you are installing nekosquared directly as a python package with
dependencies, then use pip to fetch this from GitHub. If you are running in
an existing development environment to work on this project, then you can just
make a venv and invoke this script directly to install the other dependencies.
"""
import os

DEPENDENCIES_FILE = os.path.join(os.curdir, 'dependencies.txt')
NON_PYPI_DEPENDENCIES_FILE = os.path.join(os.curdir, 'nppdeps.txt')


with open(DEPENDENCIES_FILE) as fp:
    pypi_deps = filter(bool, fp.read().split('\n'))

with open(NON_PYPI_DEPENDENCIES_FILE) as non_pypi_deps:
    non_pypi_deps = non_pypi_deps.read().split('\n')
    non_pypi_deps = filter(bool, non_pypi_deps)


dependencies = [*pypi_deps, *non_pypi_deps]


if __name__ == '__main__':
    import pip
    pip.main(['install', *dependencies])
