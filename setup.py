# -*- coding:utf8 -*-
from setuptools import setup
import sys
import os
import codecs


here = os.path.dirname(__file__)
sys.path.append(here)


def readme(filename="README.rst"):
    fullpath = os.path.join(here, filename)
    readme_ = "" 
    with codecs.open(fullpath, encoding='utf-8') as fp:
        readme_ = fp.read()
    return readme_


install_requires = [
    "ansible",
]


import idcf


setup(
    name="ansible-modules-idcf",
    version=idcf.__version__,

    description=idcf.__doc__,
    long_description=readme(),
    license="GPLv3",
    url="https://github.com/attakei/ansible-modules-idcf",

    author="kAZUYA tAKEI",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],

    package_dir={'ansible.modules.idcf': 'idcf'},
    packages=['ansible.modules.idcf'],
    install_requires=install_requires,
)
