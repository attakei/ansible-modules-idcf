# -*- coding:utf8 -*-
from setuptools import setup
import sys
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))
sys.path.append(here)

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


import idcf


setup(
    name="ansible-modules-idcf-dns",
    version=idcf.__version__,

    description=idcf.__doc__,
    long_description=long_description,
    license="GPLv3",
    url="https://github.com/attakei/ansible-modules-idcf",

    author="kAZUYA tAKEI",
    author_email="attakei@gmail.com",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],

    package_dir={
        'ansible.modules.idcf': './modules/idcf',
        'ansible.module_utils': './module_utils'
    },
    packages=[
        'ansible.modules.idcf',
        'ansible.module_utils'
    ],
    install_requires=["ansible", ],
)
