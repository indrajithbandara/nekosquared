#!/usr/bin/env python3.6
"""
Installation script. Full of anger, hate and angry comments from where stuff
should have been simple, but wasn't.

Have a nice day :3
"""
import os           # OS path traversal, testing if inodes are dirs.
import pip          # Installs packages.
import re           # Regex for getting attrs from __init__.py
import setuptools   # My setuptools bindings.
import shutil       # Checking for executables in $PATH env.
import subprocess   # Invoking git to inspect the commits.
import sys          # Accessing the stderr stream.


import dependencies


PKG = 'nekosquared'
GIT_DIR = '.git'


###############################################################################
#                                                                             #
# Main setup.py script starts here.                                           #
#                                                                             #
###############################################################################


MAIN_INIT_FILE = os.path.join(PKG, '__init__.py')


with open(MAIN_INIT_FILE) as init:
    # noinspection PyTypeChecker
    attrs = {
        k: v for k, v in re.findall(
            r'__(\w+)__\s?=\s?\'([^\']*)\'',
            '\n'.join(filter(bool, init.read().split('\n')))
        )
    }
    
version = attrs.pop('version', None)
if not version:
    version = '0.0'
version += '.'

# If I forget to increment this number, we have a fallback. This number
# is the total number of commits made to the repo. Unfortunately this
# only works if `git` is installed, so I need to check for this one
# first. We also ensure '.git' is an existing directory before we do
# anything else, because we need that for `git log --oneline` to work.
# This is useful also because `git log` defaults to only checking the 
# current branch. This means I can work on a separate branch and this
# will only update the bot if it has had any new commits since then.
git_loc = shutil.which('git')
if git_loc and os.path.isdir(GIT_DIR):
    commits: str = subprocess.check_output(
        [git_loc, 'log', '--oneline'],
        universal_newlines=True
    )
    
    commit_number = str(commits.count('\n'))
    version += commit_number
else:
    print('You probably should consider installing Git on this machine.',
          file=sys.stderr)
    # If we have not got git installed, or the `.git` dir is missing, 
    # then we cannot get the commit count, so set the patch number to
    # 0.
    version += '0'

print(f'>Installing version {version} of Neko².',
      file=sys.stderr, end='\n\n')

attrs['version'] = version

###############################################################################
#                                                                             #
# Danny will not add a rewrite package to PyPi since Discord.py's rewrite is  #
# still "under development". This is a massive pain in the arse as pip is now #
# too retarded to be able to get dependencies from anywhere expect PyPi when  #
# a dependency with the same name already exists on PyPi (Discord.py v0.x).   #
#                                                                             #
# There is no solution to this, and no work around; no one seems to want to   #
# just provide a method that works for having discord.py's rewrite as a       #
# a dependency, which is a massive up-yours to anyone who is using this lib.  #
#                                                                             #
# But I digress.                                                              #
#                                                                             #
# My hacky work around is to manually install these annoying dependencies     #
# myself by hand by invoking pip. Sadly this adds a good dozen seconds to the #
# install for slow connections, and it also affects update time, but what     #
# can you do. Unless I manage the dependencies completely by hand, then it    #
# is just going to continue to be a pain in the arse.                         #
#                                                                             #
###############################################################################

# Have some citations to show that there is an issue with this.

# - https://github.com/Rapptz/discord.py/issues/946
#
# - https://python-packaging.readthedocs.io/en/latest/
#           dependencies.html#packages-not-on-pypi

#     Sometimes you’ll want to use packages that are properly arranged with 
#     setuptools, but aren’t published to PyPI.
#
# - https://github.com/pypa/pip/issues/3610
# 
# - http://setuptools.readthedocs.io/en/latest/setuptools.html
#           #dependencies-that-aren-t-in-pypi

#     Dependency links are still not deprecated. BUT WAIT. THE COMMAND FLAG
#     TO ENABLE THEM IS! O_O
#
# - https://github.com/pypa/pip/issues/4187
#     Devs telling people who wish to un-deprecate this feature where to stick
#     that suggestion.
#
# - https://github.com/Rapptz/discord.py/issues/629
#     People are being actively referred to use the rewrite. So why is there
#     not a proper way of installing it as the main dependency for this project
#     without having to revert to this crappy method to install it?
#
# I have done my homework. I have a good reason to be annoyed about this.


print('>Will get the following dependencies:',
      *dependencies.dependencies,
      sep='\n •  ',
      file=sys.stderr,
      end='\n\n')

# Causes less problems in the long run.
pip.main(['install', *dependencies.dependencies])


# Detect the packages to store
def recurse(p):
    results = [p]
    for parent, dirs, _ in os.walk(p):
        results.extend(os.path.join(parent, _dir) for _dir in dirs)
    return tuple(results)


# Calculate all packages to get.
attrs['name'] = PKG
attrs['packages'] = recurse(PKG)

print('>Installing the following packages:', 
      *attrs['packages'],
      sep='\n •  ',
      file=sys.stderr,
      end='\n\n')

setuptools.setup(**attrs)
