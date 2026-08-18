#!/usr/bin/env python3 
import os
os.environ["JAX_PLATFORMS"] = "cpu"
import jax
import jax.numpy as jnp
import numpy as np
import rclpy
from ackermann_msgs.msg import AckermannDrive, AckermannDriveStamped
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data

from std_msgs.msg import Float32 
from std_msgs.msg import Bool 
import threading
import math 

from numba import njit

from functools import partial



# TODO CHECK: include needed ROS msg type headers and libraries
import math
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Vector3
from geometry_msgs.msg import Point
from std_msgs.msg import Float32MultiArray
from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray
import time



import yaml
from pathlib import Path

from mppi import MPPI

class ConfigYAML():
    """
    Config class for yaml file
    Able to load and save yaml file to and from python object
    """
    def __init__(self) -> None:
        pass
    
    def load_file(self, filename):
        d = yaml.safe_load(Path(filename).read_text())
        for key in d: 
            setattr(self, key, d[key]) 

class Config(ConfigYAML):
    sim_time_step = 0.1
    render = 1
    kmonitor_enable = 1

    max_lap = 300
    random_seed = None    

    n_steps = 10
    n_samples = 1024
    # n_samples = 128
    n_iterations = 1
    control_dim = 2
    control_sample_noise = [1.0, 1.0]
    state_predictor = 'ks'   
    adaptive_covariance = False

    # init_noise = [5e-3, 5e-3, 5e-3] # control_vel, control_steering, state 
    init_noise = [0, 0, 0] # control_vel, control_steering, state
    
    
class oneLineJaxRNG:
    def __init__(self, init_num=0) -> None:
        self.rng = jax.random.PRNGKey(init_num)
        
    def new_key(self):
        self.rng, key = jax.random.split(self.rng)
        return key


class MPPIEnv():
    def __init__(self, waypoints, norm_param, n_steps, mode='st', DT=0.1) -> None:
        self.a_shape = 2

        self.waypoints = np.array(waypoints)
        # self.frenet_coord = FrenetCoord(jnp.array(waypoints))
        # self.diff = self.waypoints[1:, 1:3] - self.waypoints[:-1, 1:3]
        self.waypoints_distances = np.linalg.norm(self.waypoints[1:, (1, 2)] - self.waypoints[:-1, (1, 2)], axis=1)
        # print(self.waypoints_distances)
        self.n_steps = n_steps
        self.reference = None
        self.DT = DT
        self.dlk = self.waypoints[1,0] - self.waypoints[0, 0]

        self.params = {
                "mu": 1.0489,  # Friction coefficient
                "C_Sf": 4.718,  # Cornering stiffness coefficient, front
                "C_Sr": 5.4562,  # Cornering stiffness coefficient, rear
                "lf": 0.15875,  # Distance from the center of gravity to the front axle [m]
                "lr": 0.17145,  # Distance from the center of gravity to the rear axle [m]
                "h": 0.074,  # Height of the center of gravity [m]
                "m": 3.74,  # Total vehicle mass [kg]
                "I": 0.04712,  # Moment of inertia [kg.m^2]
                "s_min": -0.4189,  # Minimum steering angle [rad]
                "s_max": 0.4189,  # Maximum steering angle [rad]
                "sv_min": -3.2,  # Minimum steering velocity [rad/s]
                "sv_max": 3.2,  # Maximum steering velocity [rad/s]
                "v_switch": 7.319,  # Switching velocity [m/s]
                #"a_max": 9.51,  # Maximum acceleration [m/s^2]
                "a_max": 0.5,
                #"v_min": -5.0,  # Minimum velocity [m/s]
                "v_min": 0.0,
                #"v_max": 20.0,  # Maximum velocity [m/s]
                "v_max": 0.8,
                "width": 0.31,  # Vehicle width [m]
                "length": 0.58,  # Vehicle length [m]
            }
        
        # config.load_file(config.savedir + 'config.json')
        self.normalization_param = norm_param
        self.mode = mode
        # self.mb_dyna_pre = None
        if mode == 'ks':
            def update_fn(x, u):
                x1 = x.copy()
                Ddt = 0.05
                def step_fn(i, x0):
                    # # Forward euler
                    # return x0 + vehicle_dynamics_st_trap([x0, u]) * Ddt

                    # RK45
                    k1 = self.vehicle_dynamics_ks(x0, u)
                    k2 = self.vehicle_dynamics_ks(x0 + k1 * 0.5 * Ddt, u)
                    k3 = self.vehicle_dynamics_ks(x0 + k2 * 0.5 * Ddt, u)
                    k4 = self.vehicle_dynamics_ks(x0 + k3 * Ddt, u)
                    return x0 + (k1 + 2 * k2 + 2 * k3 + k4) / 6 * Ddt
                    
                x1 = jax.lax.fori_loop(0, int(self.DT/Ddt), step_fn, x1)
                return (x1, 0, x1-x)
            self.update_fn = update_fn

        if mode == 'st':
            def update_fn(x, u):
                x1 = x.copy()
                Ddt = 0.05
                def step_fn(i, x0):
                    # # Forward euler
                    # return x0 + vehicle_dynamics_st_trap([x0, u]) * Ddt

                    # RK45
                    k1 = self.vehicle_dynamics_st(x0, u)
                    k2 = self.vehicle_dynamics_st(x0 + k1 * 0.5 * Ddt, u)
                    k3 = self.vehicle_dynamics_st(x0 + k2 * 0.5 * Ddt, u)
                    k4 = self.vehicle_dynamics_st(x0 + k3 * Ddt, u)
                    return x0 + (k1 + 2 * k2 + 2 * k3 + k4) / 6 * Ddt
                    
                x1 = jax.lax.fori_loop(0, int(self.DT/Ddt), step_fn, x1)
                return (x1, 0, x1-x)
            self.update_fn = update_fn
    
    ## Constraints handling
    def accl_constraints(self, vel, accl, v_switch, a_max, v_min, v_max):
        """
        Acceleration constraints, adjusts the acceleration based on constraints

            Args:
                vel (float): current velocity of the vehicle
                accl (float): unconstraint desired acceleration
                v_switch (float): switching velocity (velocity at which the acceleration is no longer able to create wheel spin)
                a_max (float): maximum allowed acceleration
                v_min (float): minimum allowed velocity
                v_max (float): maximum allowed velocity

            Returns:
                accl (float): adjusted acceleration
        """

        # positive accl limit
        # if vel > v_switch:
        #     pos_limit = a_max*v_switch/vel
        # else:
        #     pos_limit = a_max
        pos_limit = jax.lax.select(vel > v_switch, a_max*v_switch/vel, a_max)

        # accl limit reached?
        # accl = jax.lax.select(vel <= v_min and accl <= 0, 0., accl)
        # accl = jax.lax.select(vel >= v_max and accl >= 0, 0., accl)
        accl = jax.lax.select(jnp.all(jnp.asarray([vel <= v_min, accl <= 0])), 0., accl)
        accl = jax.lax.select(jnp.all(jnp.asarray([vel >= v_max, accl >= 0])), 0., accl)
        
        accl = jax.lax.select(accl <= -a_max, -a_max, accl)
        accl = jax.lax.select(accl >= pos_limit, pos_limit, accl)

        return accl
    
    def steering_constraint(self, steering_angle, steering_velocity, s_min, s_max, sv_min, sv_max):
        """
        Steering constraints, adjusts the steering velocity based on constraints

            Args:
                steering_angle (float): current steering_angle of the vehicle
                steering_velocity (float): unconstraint desired steering_velocity
                s_min (float): minimum steering angle
                s_max (float): maximum steering angle
                sv_min (float): minimum steering velocity
                sv_max (float): maximum steering velocity

            Returns:
                steering_velocity (float): adjusted steering velocity
        """

        # constraint steering velocity
        steering_velocity = jax.lax.select(jnp.all(jnp.asarray([steering_angle <= s_min, steering_velocity <= 0])), 0., steering_velocity)
        steering_velocity = jax.lax.select(jnp.all(jnp.asarray([steering_angle >= s_max, steering_velocity >= 0])), 0., steering_velocity)
        # steering_velocity = jax.lax.select(steering_angle >= s_max and steering_velocity >= 0, 0., steering_velocity)
        steering_velocity = jax.lax.select(steering_velocity <= sv_min, sv_min, steering_velocity)
        steering_velocity = jax.lax.select(steering_velocity >= sv_max, sv_max, steering_velocity)
        # if (steering_angle <= s_min and steering_velocity <= 0) or (steering_angle >= s_max and steering_velocity >= 0):
        #     steering_velocity = 0.
        # elif steering_velocity <= sv_min:
        #     steering_velocity = sv_min
        # elif steering_velocity >= sv_max:
        #     steering_velocity = sv_max

        return steering_velocity
    
    ##Vehicle Dynamics models
    @partial(jax.jit, static_argnums=(0))
    def vehicle_dynamics_ks(self, x, u_init):
        """
        Single Track Kinematic Vehicle Dynamics.

            Args:
                x (numpy.ndarray (3, )): vehicle state vector (x1, x2, x3, x4, x5)
                    x1: x position in global coordinates
                    x2: y position in global coordinates
                    x3: steering angle of front wheels
                    x4: velocity in x direction
                    x5: yaw angle
                u (numpy.ndarray (2, )): control input vector (u1, u2)
                    u1: steering angle velocity of front wheels
                    u2: longitudinal acceleration

            Returns:
                f (numpy.ndarray): right hand side of differential equations
        """
        # wheelbase
        lf = self.params["lf"]
        lr = self.params["lr"]
        lwb = lf + lr
        # constraints
        s_min = self.params["s_min"]  # minimum steering angle [rad]
        s_max = self.params["s_max"]  # maximum steering angle [rad]
        # longitudinal constraints
        v_min = self.params["v_min"]  # minimum velocity [m/s]
        v_max = self.params["v_max"] # minimum velocity [m/s]
        sv_min = self.params["sv_min"] # minimum steering velocity [rad/s]
        sv_max = self.params["sv_max"] # maximum steering velocity [rad/s]
        v_switch = self.params["v_switch"]  # switching velocity [m/s]
        a_max = self.params["a_max"] # maximum absolute acceleration [m/s^2]

        # constraints
        u = jnp.array([self.steering_constraint(x[2], u_init[0], s_min, s_max, sv_min, sv_max), self.accl_constraints(x[3], u_init[1], v_switch, a_max, v_min, v_max)])

        # system dynamics
        f = jnp.array([x[3]*jnp.cos(x[4]),
            x[3]*jnp.sin(x[4]), 
            u[0],
            u[1],
            x[3]/lwb*jnp.tan(x[2])])
        return f
    
    # @partial(jax.jit, static_argnums=(0))
    def vehicle_dynamics_st(self, x, u_init):
        """
        Single Track Dynamic Vehicle Dynamics.

            Args:
                x (numpy.ndarray (3, )): vehicle state vector (x1, x2, x3, x4, x5, x6, x7)
                    x1: x position in global coordinates
                    x2: y position in global coordinates
                    x3: steering angle of front wheels
                    x4: velocity in x direction
                    x5: yaw angle
                    x6: yaw rate
                    x7: slip angle at vehicle center
                u (numpy.ndarray (2, )): control input vector (u1, u2)
                    u1: steering angle velocity of front wheels
                    u2: longitudinal acceleration

            Returns:
                f (numpy.ndarray): right hand side of differential equations
        """
        # gravity constant m/s^2
        g = 9.81

        
        # wheelbase
        lf = self.params["lf"]
        lr = self.params["lr"]
        lwb = lf + lr
        # constraints
        s_min = self.params["s_min"]  # minimum steering angle [rad]
        s_max = self.params["s_max"]  # maximum steering angle [rad]
        # longitudinal constraints
        v_min = self.params["v_min"]  # minimum velocity [m/s]
        v_max = self.params["v_max"] # minimum velocity [m/s]
        sv_min = self.params["sv_min"] # minimum steering velocity [rad/s]
        sv_max = self.params["sv_max"] # maximum steering velocity [rad/s]
        v_switch = self.params["v_switch"]  # switching velocity [m/s]
        a_max = self.params["a_max"] # maximum absolute acceleration [m/s^2]

        m = self.params["m"]
        mu = self.params["mu"]
        h = self.params["h"]
        I = self.params["I"]
        C_Sr = self.params["C_Sr"]
        C_Sf = self.params["C_Sf"]


        # constraints
        u = jnp.array([self.steering_constraint(x[2], u_init[0], s_min, s_max, sv_min, sv_max), self.accl_constraints(x[3], u_init[1], v_switch, a_max, v_min, v_max)])

        # system dynamics
        f = jnp.array([x[3]*jnp.cos(x[6] + x[4]),
            x[3]*jnp.sin(x[6] + x[4]),
            u[0],
            u[1],
            x[5],
            -mu*m/(x[3]*I*(lr+lf))*(lf**2*C_Sf*(g*lr-u[1]*h) + lr**2*C_Sr*(g*lf + u[1]*h))*x[5] \
                +mu*m/(I*(lr+lf))*(lr*C_Sr*(g*lf + u[1]*h) - lf*C_Sf*(g*lr - u[1]*h))*x[6] \
                +mu*m/(I*(lr+lf))*lf*C_Sf*(g*lr - u[1]*h)*x[2],
            (mu/(x[3]**2*(lr+lf))*(C_Sr*(g*lf + u[1]*h)*lr - C_Sf*(g*lr - u[1]*h)*lf)-1)*x[5] \
                -mu/(x[3]*(lr+lf))*(C_Sr*(g*lf + u[1]*h) + C_Sf*(g*lr-u[1]*h))*x[6] \
                +mu/(x[3]*(lr+lf))*(C_Sf*(g*lr-u[1]*h))*x[2]])

        return f
                
    # @partial(jax.jit, static_argnums=(0,))
    def step(self, x, u):
        return self.update_fn(x, u * self.normalization_param)
        # return self.update_fn(x, u)
    
    
    @partial(jax.jit, static_argnums=(0,))
    def reward_fn(self, s, reference):
        

        xy_cost = -jnp.linalg.norm(reference[1:, :2] - s[:, :2], ord=1, axis=1)
        # vel_cost = -jnp.linalg.norm(reference[1:, 5] - s[:, 3])
        yaw_cost = -jnp.abs(jnp.sin(reference[1:, 3]) - jnp.sin(s[:, 4])) - \
            jnp.abs(jnp.cos(reference[1:, 3]) - jnp.cos(s[:, 4]))
        
        # adding terminal cost( useful sometimes)
        terminal_cost = -jnp.linalg.norm(reference[-1, :2] - s[-1, :2])
        return 15*xy_cost + 20*yaw_cost  
            
    
    # @partial(jax.jit, static_argnums=(0,))
    def reward(self, x):
        return 0
    
    def get_refernece_traj(self, state, target_speed=None, vind=5, speed_factor=1.0):
        _, dist, _, _, ind = nearest_point(np.array([state[0], state[1]]), 
                                           self.waypoints[:, (1, 2)].copy())
        
        if target_speed is None:
            # speed = self.waypoints[ind, vind] * speed_factor
            speed = np.minimum(self.waypoints[ind, vind] * speed_factor, 20)
            # speed = state[3]
        else:
            speed = target_speed
        
        # if ind < self.waypoints.shape[0] - self.n_steps:
        #     speeds = self.waypoints[ind:ind+self.n_steps, vind]
        # else:
        speeds = np.ones(self.n_steps) * speed
        
        reference = self.get_reference_trajectory(speeds, dist, ind, 
                                            self.waypoints.copy(), int(self.n_steps),
                                            self.waypoints_distances.copy(), DT=self.DT)
        orientation = state[4]
        angle_thres = 5.0
        reference[3, :][reference[3, :] - orientation > angle_thres] = np.abs(
            reference[3, :][reference[3, :] - orientation > angle_thres] - (2 * np.pi))
        reference[3, :][reference[3, :] - orientation < -angle_thres] = np.abs(
            reference[3, :][reference[3, :] - orientation < -angle_thres] + (2 * np.pi))
        
        # reference[2] = np.where(reference[2] - speed > 5.0, speed + 5.0, reference[2])
        self.reference = reference.T
        return reference.T, ind
    
    def get_reference_trajectory(self, predicted_speeds, dist_from_segment_start, idx, 
                                waypoints, n_steps, waypoints_distances, DT):
        s_relative = np.zeros((n_steps + 1,))
        s_relative[0] = dist_from_segment_start
        s_relative[1:] = predicted_speeds * DT
        s_relative = np.cumsum(s_relative)

        waypoints_distances_relative = np.cumsum(np.roll(waypoints_distances, -idx))

        index_relative = np.int_(np.ones((n_steps + 1,)))
        for i in range(n_steps + 1):
            index_relative[i] = (waypoints_distances_relative <= s_relative[i]).sum()
        index_absolute = np.mod(idx + index_relative, waypoints.shape[0] - 1)

        segment_part = s_relative - (
                waypoints_distances_relative[index_relative] - waypoints_distances[index_absolute])

        t = (segment_part / waypoints_distances[index_absolute])
        # print(np.all(np.logical_and((t < 1.0), (t > 0.0))))

        position_diffs = (waypoints[np.mod(index_absolute + 1, waypoints.shape[0] - 1)][:, (1, 2)] -
                            waypoints[index_absolute][:, (1, 2)])
        orientation_diffs = (waypoints[np.mod(index_absolute + 1, waypoints.shape[0] - 1)][:, 3] -
                                waypoints[index_absolute][:, 3])
        speed_diffs = (waypoints[np.mod(index_absolute + 1, waypoints.shape[0] - 1)][:, 5] -
                        waypoints[index_absolute][:, 5])

        interpolated_positions = waypoints[index_absolute][:, (1, 2)] + (t * position_diffs.T).T
        interpolated_orientations = waypoints[index_absolute][:, 3] + (t * orientation_diffs)
        interpolated_orientations = (interpolated_orientations + np.pi) % (2 * np.pi) - np.pi
        interpolated_speeds = waypoints[index_absolute][:, 5] + (t * speed_diffs)
        
        reference = np.array([
            # Sort reference trajectory so the order of reference match the order of the states
            interpolated_positions[:, 0],
            interpolated_positions[:, 1],
            interpolated_speeds,
            interpolated_orientations,
            # Fill zeros to the rest so number of references mathc number of states (x[k] - ref[k])
            np.zeros(len(interpolated_speeds)),
            np.zeros(len(interpolated_speeds)),
            np.zeros(len(interpolated_speeds))
        ])
        return reference

class MPPIPlanner(Node):
    def __init__(self):
        super().__init__('mppi_node')
        #self.waypoint_path = "/home/juan/sim_ws/src/f1tenth_mppi/trajectories/levine_1.csv"
        #self.waypoint_path = "/home/juan/sim_ws/src/f1tenth_mppi/trajectories/siccs_first_floor_dyn.csv"
        #self.waypoint_path = "/home/sdc6/f1tenth_ws/src/f1tenth_mppi/trajectories/siccs_first_floor_dyn.csv"
        self.waypoint_path = "/home/sdc6/gsts.csv"
        self.control_debug = True
        
        self.enable_drive = True 

        self.waypoints = self.load_waypoints(self.waypoint_path)

        #self.drive_pub = self.create_publisher(AckermannDriveStamped, '/drive', 10)
        self.drive_pub = self.create_publisher(AckermannDriveStamped,"/ackermann_cmd",1)
        self.timing_pub_ = self.create_publisher(Float32MultiArray, '/mppi/timing', 10)
        self.drive_msg_ = AckermannDriveStamped()


        self.ref_goal_points_ = self.create_publisher(MarkerArray, 'ref_goal_points', 1)
        self.ref_trajectory_ = self.create_publisher(Marker,'ref_trajectory', 1)
        self.opt_trajectory_ = self.create_publisher(Marker,'opt_trajectory', 1)
        self.sampled_trajectory_ = self.create_publisher(Marker,'sampled_trajectory', 1)

        
        # self.pose_sub_ = self.create_subscription(Odometry, 'ego_racecar/odom', self.pose_callback, 1)
        

        self.config = Config()
        #self.config.load_file("/home/juan/sim_ws/src/f1tenth_mppi/config/config.yaml")
        self.config.load_file("/home/sdc6/f1tenth_ws/src/f1tenth_mppi/config/config.yaml")


        # MPPI params
        self.n_iterations = self.config.n_iterations
        self.n_steps = self.config.n_steps
        self.n_samples = self.config.n_samples
        self.jRNG = oneLineJaxRNG(1337)
        self.DT = 0.1
        self.on_car = False
        #pose_topic = "/pf/viz/inferred_pose" if self.on_car else "/ego_racecar/odom"
        #pose_topic = "/odom"
        
        #self.pose_sub_ = self.create_subscription(PoseStamped if self.on_car else Odometry, pose_topic, self.pose_callback, 1)
        self.normalization_param = np.array(self.config.normalization_param).T
        norm_param = self.normalization_param[0, 7:9]/2
        self.norm_param = norm_param

        self.declare_parameter('self_object_id', 560)
        self.declare_parameter('other_object_id',561)
        self.SELF_ID = int(self.get_parameter('self_object_id').value)
        self.OTHER_ID = int(self.get_parameter('other_object_id').value)

        pose_topic = f"/optitrack/object_{self.SELF_ID}/pose"

        
        self.mppi_env = MPPIEnv(self.waypoints, norm_param, self.n_steps, mode = 'ks', DT= self.DT)
        self.mppi = MPPI(self.config,jRNG=self.jRNG, a_noise = 1.0, scan = False)
        
        self.a_opt = None
        self.a_cov = None
        self.mppi_distrib = None
        
        self.target_vel = 0.8
        
        self.init_state()
        self.ref_goal_points_data = self.viz_ref_points()
        self.detect_lock = threading.Lock()
        self.speed_lock = threading.Lock()
        self.pose_lock = threading.Lock()
        self.traffic_lock = threading.Lock()
        self.car_should_stop = False
        self.is_stopping_maneuver_active = False 
        self.DETECTION_TRIGGER_DISTANCE = 10.0
        self.TARGET_STOP_DISTANCE = 0.3
        self.planned_stop_time = 0.0
        self.cooldown_until = 0.0
        self.stop_start_time = None 
        self.current_estimated_speed = 0.0
        self.MAX_ACCEL = 1.0
        self.brake_trigger_time = None 
        self.brake_trigger_speed = None 
        self.own_pose = None 
        self.other_car_pose = None 
        self.CLEAR_DISTANCE_THRESHOLD = 1.25
        self.MIN_STOP_TIME = 1.0

        self.status_lock = threading.Lock()
        self.other_stopped = None 
        self.other_stopped_observed_time = None
        

        self.stop_sign_sub = self.create_subscription(Float32,'/sdc6/stop_sign/distance',self.stop_sign_distance_callback,1)
        self.pose_sub = self.create_subscription(PoseStamped,pose_topic,self.pose_callback,qos_profile_sensor_data)
        #self.pose_sub = self.create_subscription(Odometry,pose_topic,self.pose_callback,qos_profile_sensor_data)
        self.odom_sub = self.create_subscription(Odometry,f'/optitrack/object_{self.SELF_ID}/odom',self.odom_callback,qos_profile_sensor_data)
        self.traffic_sub = self.create_subscription(PoseStamped, f'optitrack/object_{self.OTHER_ID}/pose', self.traffic_pose_callback , qos_profile_sensor_data)
        self.we_stopped_pub = self.create_publisher(Bool, '/sdc6/stop_sign/we_stopped', 1)
        self.we_stopped_sub = self.create_subscription(Bool, '/sdc2/stop_sign/we_stopped',self.other_status_callback,1)
        self.ref_speed = 0.8
    
    def traffic_pose_callback(self, pose_msg):
        x = pose_msg.pose.position.x
        y = pose_msg.pose.position.y 
        with self.traffic_lock:
            self.other_car_pose = (x,y)
    
        
    def is_intersection_clear(self):    
        with self.pose_lock:
            own = self.own_pose
        with self.traffic_lock:
            other = self.other_car_pose
        if own is None or other is None:
            return False 
        dist = math.hypot(own[0] - other[0], own[1] - other[1])
        return dist > self.CLEAR_DISTANCE_THRESHOLD

    def other_status_callback(self,msg):
        value = msg.data
        with self.status_lock:
            if value and not self.other_stopped:
                self.other_stopped_observed_time = time.time()
            elif not value:
                self.other_stopped_observed_time = None 
            self.other_stopped = value

    def publish_stop_status(self,is_stopped):
        msg = Bool()
        msg.data = bool(is_stopped)
        self.we_stopped_pub.publish(msg)

    def has_priority(self):
        with self.status_lock:
            other_stopped = self.other_stopped
            other_ts = self.other_stopped_observed_time
        if not other_stopped or other_ts is None or self.stop_start_time is None:
            return True
        if abs(self.stop_start_time-other_ts) < 0.05:
            return self.SELF_ID < self.OTHER_ID
        return self.stop_start_time < other_ts


    def odom_callback(self,msg):
        vx = msg.twist.twist.linear.x 
        vy = msg.twist.twist.linear.y 
        speed = math.sqrt(vx**2 + vy**2)
        with self.speed_lock:
            self.current_estimated_speed = speed 

    
    def stop_sign_distance_callback(self,msg):
        distance_m = msg.data
        current_time = time.time()
        with self.detect_lock:
            if self.car_should_stop:
                if self.stop_start_time is None:
                    self.stop_start_time = current_time 
                    self.get_logger().info("STOP SIGN WHAT STOP SIGN")
                elapsed = current_time - self.stop_start_time
                with self.pose_lock:
                    own = self.own_pose
                with self.traffic_lock:
                    other = self.other_car_pose
                clear = self.is_intersection_clear()
                priority = self.has_priority()
                dist_str = "n/a"
                if own is not None and other is not None:
                    dist_str = f"{math.hypot(own[0]-other[0],own[1]-other[1]):.3f}"
                with self.status_lock:
                    other_stopped = self.other_stopped
                    other_ts = self.other_stopped_observed_time
                self.get_logger().info(
                    f"[stop-check] elapsed={elapsed:.2f}s clear={clear} "
                    f"dist={dist_str} own={own} other={other}"
                )
                self.publish_stop_status(True)
                if clear and priority:
                    if elapsed >= self.MIN_STOP_TIME:
                        self.get_logger().info("okie we back")
                        self.car_should_stop = False 
                        self.is_stopping_maneuver_active = False 
                        self.stop_start_time = None 
                        self.planned_stop_time = None 
                        self.cooldown_until = current_time + 1.0
                        self.publish_stop_status(False)
                elif not clear:
                    self.get_logger().info("hooooooold")
                else:
                    self.get_logger().info("i wait")
                return 
            if current_time <= self.cooldown_until:
                return 
            self.publish_stop_status(False)
            if distance_m >0:
                self.get_logger().info(f"STOP SIGN IN {distance_m:.2f} eeeek")
                if (distance_m <= self.DETECTION_TRIGGER_DISTANCE and distance_m > self.TARGET_STOP_DISTANCE and current_time > self.cooldown_until):
                    distance_to_travel = distance_m - self.TARGET_STOP_DISTANCE
                    with self.speed_lock:
                        current_speed = max(0.2,self.current_estimated_speed)
                    dynamic_brake_lag = (current_speed * 0.5)
                    time_until_stop = 0.0
                    time_until_stop = (distance_to_travel/current_speed) - dynamic_brake_lag
                    time_until_stop = max(0.0, time_until_stop)
                    if not self.is_stopping_maneuver_active:
                        self.planned_stop_time = current_time + time_until_stop
                        self.is_stopping_maneuver_active = True 
                        #self.brake_trigger_time = current_time 
                        #self.brake_trigger_speed = current_speed 
                else:
                    self.planned_stop_time = current_time + 2.0
                    self.is_stopping_maneuver_active = True 
                if not self.is_stopping_maneuver_active and not self.car_should_stop:
                    self.is_stopping_maneuver_active = True 
                    self.planned_stop_time = current_time + 2.0
                    #self.stop_start_time = current_time
                    #self.brake_trigger_time = current_time 
            else:
                pass 
            if self.is_stopping_maneuver_active and current_time >= self.planned_stop_time:
                self.car_should_stop = True   
                #if hasattr(self,'brake_trigger_time') and self.brake_trigger_time is not None:
                #    elapsed_time = current_time - self.brake_trigger_time
                #    speedy = getattr(self,'brake_trigger_speed',0.0)
                #    self.get_logger().info(f"Time: {elapsed_time:.3f} seconds")
                #    self.get_logger().info(f"Speed: {speedy:.3f} m/s")
                #    self.brake_trigger_time = None  
                #    self.brake_trigger_speed = None          
    
    def load_waypoints(self, path):
        points = np.loadtxt(path, delimiter=';',skiprows=3, dtype=np.float64)
        #  points = np.loadtxt(path, delimiter=';', skiprows=3)
        #points[:, 3] += 0.5*math.pi
        # CONFIGURE DLK
        # self.config.dlk = points[1, 0] - points[0, 0]
        return points
    
    def init_state(self):
        self.mppi.init_state(self.mppi_env)
        self.a_opt = self.mppi.a_opt
        self.a_cov = self.mppi.a_cov

        self.mppi_distrib = (self.a_opt, self.a_cov)
    
    def pose_callback(self, pose_msg):
        
        start = time.time()
        current_time = time.time()
        with self.pose_lock:
            self.own_pose = (pose_msg.pose.position.x, pose_msg.pose.position.y)
        with self.detect_lock:
            if self.car_should_stop:
                self.drive_msg_.drive.speed = 0.0
                #self.drive_msg_.drive.steering_angle = 0.0
                if self.enable_drive:
                    self.drive_pub.publish(self.drive_msg_)
                return 
        with self.detect_lock:
            if self.is_stopping_maneuver_active and not self.car_should_stop:
                time_left = max(0.0,self.planned_stop_time - current_time)
                dist_remaining = time_left * max(0.1,self.current_estimated_speed)
                safe_v = math.sqrt(2.0*(self.MAX_ACCEL*0.7)*max(0.005,dist_remaining))
                local_ref_speed = np.minimum(self.ref_speed, safe_v)
            else:
                local_ref_speed = self.ref_speed
        
                


        x_state = pose_msg.pose.position.x 
        y_state = pose_msg.pose.position.y 
        curr_orien = pose_msg.pose.orientation 

        #x_state = pose_msg.pose.pose.position.x
        #y_state =  pose_msg.pose.pose.position.y
        #curr_orien = pose_msg.pose.pose.orientation

        vel_state = self.drive_msg_.drive.speed
        steer_angle = self.drive_msg_.drive.steering_angle
        with self.speed_lock:
            self.current_estimated_speed = vel_state

        
        q = [curr_orien.x, curr_orien.y, curr_orien.z, curr_orien.w]
        yaw_state = math.atan2(2 * (q[3] * q[2] + q[0] * q[1]), 1 - 2 * (q[1] ** 2 + q[2] ** 2))
        # print("current yaw", yawp)
        state = np.array([x_state, y_state, steer_angle, vel_state, yaw_state])
        # print(da.shape)

        #ref_traj,_ = self.mppi_env.get_refernece_traj(state, target_speed = self.target_vel,  vind = 5, speed_factor= 1)
        ref_traj,_ = self.mppi_env.get_refernece_traj(state,target_speed = local_ref_speed,vind = 5, speed_factor = 1)
        # print(ref_traj.shape) #[n_steps + 1, 7]

        self.mppi_distrib, sampled_traj, s_opt = self.mppi.update(self.mppi_env, state.copy(), self.jRNG.new_key())

        a_opt = self.mppi_distrib[0]
        control = a_opt[0]
        scaled_control = np.multiply(self.norm_param, control)
        # TODO: check the mppi outputs( its in steerv, accl), convert to vel and steering angle control ig and check mpc node what they do
        
        steerv = scaled_control[0]
        accl = scaled_control[1]
        cmd_steer_angle = self.drive_msg_.drive.steering_angle + steerv*self.DT
        cmd_drive = self.drive_msg_.drive.speed + accl*self.DT

        cmd_steer_angle = np.clip(cmd_steer_angle, -0.4189, 0.4189)
        cmd_drive = np.clip(cmd_drive, 0, 6)

        self.drive_msg_.drive.speed = cmd_drive
        self.drive_msg_.drive.steering_angle = cmd_steer_angle
        # self.drive_msg_.drive.steering_angle_velocity = steerv
        # self.drive_msg_.drive.acceleration = accl

        if self.control_debug:
            self.drive_pub.publish(self.drive_msg_)
            
            
        dt = time.time() - start
        # timing_msg = Float32MultiArray()
        # hz = 1.0 / dt if dt > 0 else float('inf')
        # timing_msg.data = [dt, hz]
        # self.timing_pub_.publish(timing_msg)
        # self.get_logger().info(f'Computation time: {dt:.4f} seconds')
        
        self.publish_computation_time(dt)

        self.viz_ref_traj(ref_traj)
        self.viz_opt_traj(s_opt)
        #self.viz_sampled_traj(sampled_traj)
        self.ref_goal_points_.publish(self.ref_goal_points_data)
        

    def publish_computation_time(self, dt):
        """
        Publish the computation time of the MPPI algorithm.
        """
        timing_msg = Float32MultiArray()
        hz = 1.0 / dt if dt > 0 else float('inf')
        timing_msg.data = [dt, hz]
        self.timing_pub_.publish(timing_msg)
        #self.get_logger().info(f'Computation time: {dt:.4f} seconds')
        
        


    #  Visualization MPPI
    def viz_ref_points(self):
        ref_points = MarkerArray()

        for i in range(self.waypoints.shape[0]):
            message = Marker()
            message.header.frame_id="map"
            message.header.stamp = self.get_clock().now().to_msg()
            message.type= Marker.SPHERE
            message.action = Marker.ADD
            message.id=i
            message.pose.orientation.x=0.0
            message.pose.orientation.y=0.0
            message.pose.orientation.z=0.0
            message.pose.orientation.w=1.0
            message.scale.x=0.2
            message.scale.y=0.2
            message.scale.z=0.2
            message.color.a=1.0
            message.color.r=1.0
            message.color.b=0.0
            message.color.g=0.0
            message.pose.position.x=float(self.waypoints[i,1])
            message.pose.position.y=float(self.waypoints[i,2])
            message.pose.position.z=0.0
            ref_points.markers.append(message)
        return ref_points
    
    def viz_ref_traj(self, ref_traj):

        traj = Marker(type=Marker.LINE_STRIP,
                        scale=Vector3(x=0.1, y=0.1, z=0.1))
        traj.header.frame_id = 'map'
        traj.color.r = 0.0
        traj.color.g = 0.0
        traj.color.b = 1.0
        traj.color.a = 1.0
        traj.id = 1

        for i in range(ref_traj.shape[0]):
            x, y = ref_traj[i, :2]
            # print(f'Publishing ref traj x={x}, y={y}')
            traj.points.append(Point(x=x, y=y, z=0.0))
        self.ref_trajectory_.publish(traj)

    def viz_opt_traj(self, opt_traj):
        

        traj = Marker(type=Marker.LINE_STRIP,
                        scale=Vector3(x=0.1, y=0.1, z=0.1))
        traj.header.frame_id = 'map'
        traj.color.r = 1.0
        traj.color.g = 0.0
        traj.color.b = 1.0
        traj.color.a = 1.0
        traj.id = 1
        for i in range(opt_traj.shape[0]):
            x, y = opt_traj[i,:2]
            # print(f'Publishing ref traj x={x}, y={y}')
            traj.points.append(Point(x=float(x), y=float(y), z=0.0))
        self.opt_trajectory_.publish(traj)

    
    def viz_sampled_traj(self, sampled_traj):

        traj = Marker(type=Marker.LINE_STRIP,
                        scale=Vector3(x=0.1, y=0.1, z=0.1))
        traj.header.frame_id = 'map'
        traj.color.r = 1.0
        traj.color.g = 0.5
        traj.color.b = 0.5
        traj.color.a = 0.2
        traj.id = 1
        for i in range(sampled_traj.shape[0]):
            for t in range(sampled_traj.shape[1]):
                x, y = sampled_traj[i,t,:2]
                # print(f'Publishing ref traj x={x}, y={y}')
                traj.points.append(Point(x=float(x), y=float(y), z=0.0))
        self.sampled_trajectory_.publish(traj)
    


@njit(cache=True)
def nearest_point(point, trajectory):
    """
    Return the nearest point along the given piecewise linear trajectory.
    Args:
        point (numpy.ndarray, (2, )): (x, y) of current pose
        trajectory (numpy.ndarray, (N, 2)): array of (x, y) trajectory waypoints
            NOTE: points in trajectory must be unique. If they are not unique, a divide by 0 error will destroy the world
    Returns:
        nearest_point (numpy.ndarray, (2, )): nearest point on the trajectory to the point
        nearest_dist (float): distance to the nearest point
        t (float): nearest point's location as a segment between 0 and 1 on the vector formed by the closest two points on the trajectory. (p_i---*-------p_i+1)
        i (int): index of nearest point in the array of trajectory waypoints
    """
    diffs = trajectory[1:, :] - trajectory[:-1, :]
    l2s = diffs[:, 0] ** 2 + diffs[:, 1] ** 2
    dots = np.empty((trajectory.shape[0] - 1,))
    for i in range(dots.shape[0]):
        dots[i] = np.dot((point - trajectory[i, :]), diffs[i, :])
    t = dots / l2s
    t[t < 0.0] = 0.0
    t[t > 1.0] = 1.0
    projections = trajectory[:-1, :] + (t * diffs.T).T
    dists = np.empty((projections.shape[0],))
    for i in range(dists.shape[0]):
        temp = point - projections[i]
        dists[i] = np.sqrt(np.sum(temp * temp))
    min_dist_segment = np.argmin(dists)
    dist_from_segment_start = np.linalg.norm(diffs[min_dist_segment] * t[min_dist_segment])
    return projections[min_dist_segment], dist_from_segment_start, dists[min_dist_segment], t[
        min_dist_segment], min_dist_segment

def main(args=None):

    rclpy.init(args=args)
    print("MPPI Initialized")
    mpc_node = MPPIPlanner()
    rclpy.spin(mpc_node)

    mpc_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()