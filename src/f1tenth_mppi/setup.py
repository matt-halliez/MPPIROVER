import os
from glob import glob
from setuptools import setup

package_name = 'f1tenth_mppi'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='MATT',
    maintainer_email='',
    description='f1tenth mppi',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mppi_node = f1tenth_mppi.mppi_node:main',
            'stl_svpio_node = f1tenth_mppi.stl_svpio_node:main',
        ],
    },
)