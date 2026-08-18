# How to run on car with "SDC-3" nameplate.
Connect to the car:
```
ssh -YC sdc2@123.456.7.89
```
In window 1, launch the camera:
```
ros2 launch realsense2_camera rs_launch.py depth_module.depth_profile:=640x480x15 rgb_camera.color_profile:=640x480x15 enable_depth:=true align_depth.enable:=true enable_infra1:=false enable_infra2:=false enable_gyro:=false enable_accel:=false
```
In window 2, connect to optitrack:
```
source env/bin/activate && python3 optitrack/optitrack_node.py
```
If you need to access the pose of the other car, in another window run:
```
source env/bin/activate && python3 optitrack/optitrack_other_node.py
```
In window 3, launch the sign detection:
```
source env/bin/activate && ros2 launch stopsignnode.py
```
In window 4, launch the MPPI, this will load and the car will follow the existing trajectory in gsts.csv:
```
source env/bin/activate && cd f1tenth_ws && source install/setup.bash && cd && ros2 launch mpc_car.py
```
If you need to update the trajectory: 
```
nano f1tenth_ws/src/f1tenth_mpc/kinematic_mpc/trajectory_creator.py
```
then
```
python3 f1tenth_ws/src/f1tenth_mpc/kinematic_mpc/trajectory_creator.py && python3 f1tenth_ws/src/f1tenth_mppi/trajectories/convert_csv.py
```