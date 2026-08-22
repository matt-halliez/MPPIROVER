import os
from setuptools import find_packages, setup

package_name = 'realsense'

# Helper function to collect all nested files in a directory
def generate_data_files(share_path, dir_path):
    data_files = []
    for root, _, files in os.walk(dir_path):
        if files:
            # Map source directory structure to install directory structure
            relative_path = os.path.relpath(root, dir_path)
            target_path = os.path.join(share_path, relative_path) if relative_path != '.' else share_path
            source_files = [os.path.join(root, f) for f in files]
            data_files.append((target_path, source_files))
    return data_files

# Standard ROS 2 data files
data_files = [
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
]

# Dynamically attach all files inside the config folder
data_files.extend(generate_data_files(f'share/{package_name}/config', 'config'))

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sdc6',
    maintainer_email='user@todo.todo',
    description='Realsense YOLO detection package',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'stopsign_node = realsense.stopsign:main',
        ],
    },
)
