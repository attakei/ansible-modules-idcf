# -*- coding:utf8 -*-
from setuptools import setup
import sys
import os

here = os.path.dirname(__file__)

install_requires = [
    "ansible",
]


setup(
    name="ansible-modules-idcf",
    version="0.0.1",

    description="Ansible modules for IDCF-cloud",
    long_description=open(os.path.join(here, "README.rst")).read(),
    license="GPLv3",
    url="https://github.com/attakei/ansible-modules-idcf",

    author="kAZUYA tAKEI",

    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],

    package_dir={'ansible.modules.idcf': 'idcf'},
    packages=['ansible.modules.idcf'],
    install_requires=install_requires,
)
