#!/usr/bin/env python
import sys
from setuptools import setup, Extension


tests_require = []
PY2 = sys.version_info[0] == 2
if PY2:
    tests_require.append('mock')


setup(
    name="scielo.forest",
    version='0.1',
    description="Foundations for clients of RESTful APIs.",
    author="SciELO & contributors",
    author_email="scielo-dev@googlegroups.com",
    license="BSD",
    py_modules=["forest"],
    package_data={'': ['README.md', 'LICENSE']},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    tests_require=tests_require,
    test_suite='tests',
)
