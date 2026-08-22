import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource

def generate_launch_description():
    ld = LaunchDescription()

    mppi_node = Node(
        package='f1tenth_mppi',
        namespace='f1tenth_mppi1',
        executable='stl_svpio_node.py', #stl_svpio_node, mppi_node
        name='mppi',
        output='screen'
    ),

    mppi_node = Node(
        package='f1tenth_mppi',
        namespace='f1tenth_mppi1',
        executable='stl_svpio_node.py', #stl_svpio_node, mppi_node
        name='mppi',
        output='screen'
    )


    ld.add_action(mppi_node)
    ld.add_action()
    return ld