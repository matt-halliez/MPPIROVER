from setuptools import find_packages
from setuptools import setup

setup(
    name='f1tenth_mppi',
    version='0.0.0',
    packages=find_packages(
        include=('f1tenth_mppi', 'f1tenth_mppi.*')),
)
