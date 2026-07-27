
# f1tenth_mppi
This repository has a MPPI controller for the f1tenth car using f1tenth_gym_ros

Please refer to [INTRO.md](INTRO.md) for a brief overview of **Model Predictive Control (MPC)** and **Model Predictive Path Integral (MPPI)**, as well as the key distinctions between these two approaches.

## Running the Code

To run this code, you need a working ROS2 environment with the required dependencies installed (e.g., `jax`, `jaxlib`, `numpy`, `rclpy`). Follow these steps:

1. In a new terminal, navigate to the catkin workspace containing the source folder and build the environment: 
```bash
cd $HOME/sim_ws/src
colcon build
```
2. Launch the f1tenth ROS simulator:
```bash
cd $HOME/sim_ws/src
source install/setup.bash
ros2 launch f1tenth_gym_ros gym_bridge_launch.py
```
3. Source the workspace and run the MPPI node: 
```bash
cd $HOME/sim_ws/src
source install/setup.bash
ros2 run f1tenth_mppi mppi_node.py
```

The MPPI planner node will initialize, and once the robot's odometry data starts streaming (from simulation or a real robot), it will compute and publish control commands.

You can visualize the reference waypoints, trajectory, optimal trajectory, and sampled trajectories using tools like RViz or other visualization tools that subscribe to the corresponding ROS topics.

**Note:** The code assumes the availability of robot odometry data and predefined waypoints. You may need to modify the code or provide the required inputs (e.g., waypoints file path, odometry topic) based on your setup and requirements. Additionally, you can adjust various configuration parameters, such as the number of MPPI iterations, samples, prediction horizon, and other algorithm-specific parameters, based on your system dynamics, performance requirements, and desired behavior.
