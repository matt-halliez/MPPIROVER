from setuptools import find_packages, setup

package_name = 'optitrack'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sdc6',
    maintainer_email='mahk28@lehigh.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'optitrack_car1_node = optitrack.optitrack_car1_node:main',
            'optitrack_car2_node = optitrack.optitrack_car2_node:main',
        ],
    },
)
