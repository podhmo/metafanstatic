# -*- coding:utf-8 -*-

import os
import sys

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.rst')) as f:
        README = f.read()
    with open(os.path.join(here, 'CHANGES.txt')) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ''

install_requires=[
    'setuptools',
    'requests', 
    'fanstatic', 
    "korpokkur"
    ]

docs_extras = [
    ]

tests_require = [
    "nose"
    ]

testing_extras = tests_require + [
    ]

setup(name='metafanstatic',
      version='0.0',
      description='fanstatic package generator',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: CPython",
        ],
      keywords='',
      author="",
      author_email="",
      url="",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = install_requires,
      extras_require = {
          'testing':testing_extras,
          'docs':docs_extras,
          },
      tests_require = tests_require,
      test_suite='nose.collector',
      entry_points = """
      [console_scripts]
      metafanstatic = metafanstatic.command:main
      [korpokkur.scaffold]
      metafanstatic = metafanstatic.scaffolds:Package
      """
      )


