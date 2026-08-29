import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, LogInfo, RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    ld = LaunchDescription()

    # ANSI Green Color Formatting
    GREEN = '\033[92m'
    RESET = '\033[0m'

    # -------------------------------------------------------------------------
    # 1. RealSense Camera Launch (Starts Immediately)
    # -------------------------------------------------------------------------
    realsense_pkg = get_package_share_directory('realsense2_camera')
    realsense_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(realsense_pkg, 'launch', 'rs_launch.py')
        ),
        launch_arguments={
            'depth_module.depth_profile': '640x480x15',
            'rgb_camera.color_profile': '640x480x15',
            'enable_depth': 'true',
            'align_depth.enable': 'true',
            'enable_infra1': 'false',
            'enable_infra2': 'false',
            'enable_gyro': 'false',
            'enable_accel': 'false',
        }.items()
    )

    log_realsense = LogInfo(msg=f"{GREEN}[SUCCESS] Camera Launch Started!{RESET}")

    # -------------------------------------------------------------------------
    # 2. OptiTrack Nodes (Wait 4 seconds for camera initialization)
    # -------------------------------------------------------------------------
    optitrack_car1 = Node(
        package='optitrack',
        namespace='optitrack1',
        executable='optitrack_car1_node',
        name='optitrack',
        output='screen'
    )

    optitrack_car2 = Node(
        package='optitrack',
        namespace='optitrack2',
        executable='optitrack_car2_node',
        name='optitrack',
        output='screen'
    )

    log_optitrack = LogInfo(msg=f"{GREEN}[SUCCESS] OptiTrack Car Nodes Running!{RESET}")

    timer_optitrack = TimerAction(
        period=4.0,  # 4 second delay
        actions=[log_optitrack, optitrack_car1, optitrack_car2]
    )

    # -------------------------------------------------------------------------
    # 3. Stop Sign Detection Node (Triggers AFTER OptiTrack Car 1 Starts)
    # -------------------------------------------------------------------------
    detection_node = Node(
        package='realsense',
        executable='stopsign_node',
        name='camera_detection',
        output='screen'
    )

    log_detection = LogInfo(msg=f"{GREEN}[SUCCESS] Stop Sign Detection Running!{RESET}")

    event_detection = RegisterEventHandler(
        OnProcessStart(
            target_action=optitrack_car1,
            on_start=[
                TimerAction(
                    period=4.0,  # Wait 2 seconds after OptiTrack starts
                    actions=[log_detection, detection_node]
                )
            ]
        )
    )

    # -------------------------------------------------------------------------
    # 4. MPPI Controller Node (Triggers AFTER Detection Node Starts)
    # -------------------------------------------------------------------------
    mppi_node = Node(
        package='f1tenth_mppi',
        namespace='f1tenth_mppi1',
        executable='mppi_node.py', # stl_svpio_node.py, mppi_node.py
        name='mppi',
        output='screen'
    )

    log_mppi = LogInfo(msg=f"{GREEN}[SUCCESS] MPPI Node Running!{RESET}")

    event_mppi = RegisterEventHandler(
        OnProcessStart(
            target_action=detection_node,
            on_start=[
                TimerAction(
                    period=4.0,  # Wait 2 seconds after Detection starts
                    actions=[log_mppi, mppi_node]
                )
            ]
        )
    )

    # -------------------------------------------------------------------------
    # Add Sequence to Launch Description
    # -------------------------------------------------------------------------
    ld.add_action(log_realsense)
    ld.add_action(realsense_launch)
    ld.add_action(timer_optitrack)
    ld.add_action(event_detection)
    ld.add_action(event_mppi)

    return ld