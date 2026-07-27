#!/usr/bin/env python3
import math
import numpy as np
from dataclasses import dataclass, field
import cvxpy
from scipy.linalg import block_diag
from scipy.sparse import block_diag, csc_matrix, diags
from scipy.spatial import transform
import os
import sys
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from ackermann_msgs.msg import AckermannDrive, AckermannDriveStamped
from geometry_msgs.msg import Point, PoseStamped
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image
from visualization_msgs.msg import Marker, MarkerArray
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO
from rclpy.qos import QoSProfile,HistoryPolicy,ReliabilityPolicy,qos_profile_sensor_data
import threading
import time 
import multiprocessing as mp 
from message_filters import Subscriber, ApproximateTimeSynchronizer
import traceback
import torch
import queue
from std_msgs.msg import Float32


from utils import nearest_point


from scipy.interpolate import CubicSpline


@dataclass
class mpc_config:
    NXK: int = 4  # length of kinematic state vector: z = [x, y, v, yaw]
    NU: int = 2  # length of input vector: u = [steering speed, acceleration]
    TK: int = 8 # finite time horizon length - kinematic

    # ---------------------------------------------------
    # TODO: you may need to tune the following matrices
    Rk: list = field(
        #default_factory=lambda: np.diag([0.01, 100.0])
        default_factory=lambda: np.diag([10.0, 60.0])
    )  # input cost matrix, penalty for inputs - [accel, steering_speed]
    Rdk: list = field(
        #default_factory=lambda: np.diag([0.01, 100.0])
        default_factory=lambda: np.diag([10.0, 60.0])
    )  # input difference cost matrix, penalty for change of inputs - [accel, steering_speed]
    Qk: list = field(
        default_factory=lambda: np.diag([33.5, 30.0, 30.0, 15.0])  # levine sim
        #default_factory=lambda: np.diag([60., 50., 5.5, 15.0])
    )  # state error cost matrix, for the the next (T) prediction time steps [x, y, delta, v, yaw, yaw-rate, beta]
    Qfk: list = field(
        default_factory=lambda: np.diag([33.5, 30.0, 30.0, 15.1])  # levine sim
        #default_factory=lambda: np.diag([60., 50., 5.5, 15.0])
    )  # final state error matrix, penalty  for the final state constraints: [x, y, delta, v, yaw, yaw-rate, beta]
    # ---------------------------------------------------

    # N_IND_SEARCH: int = 20  # Search index number
    # DTK: float = 0.1  # time step [s] kinematic
    # dlk: float = 0.03  # dist step [m] kinematic
    # LENGTH: float = 0.58  # Length of the vehicle [m]
    # WIDTH: float = 0.31  # Width of the vehicle [m]
    # WB: float = 0.33 #0.3240  # Wheelbase [m]
    # MIN_STEER: float = -0.4189 #$-0.4236  # maximum steering angle [rad]
    # MAX_STEER: float = 0.4189 #0.4236  # maximum steering angle [rad]
    # MAX_DSTEER: float = np.deg2rad(180.0)  # maximum steering speed [rad/s]    
    # MAX_SPEED: float = 3.5  # maximum speed [m/s]
    # MIN_SPEED: float = 0.0  # minimum backward speed [m/s]
    # MAX_ACCEL: float = 1.0  # maximum acceleration [m/ss]


    N_IND_SEARCH: int = 20  # Search index number
    DTK: float = 0.1  # time step [s] kinematic
    dlk: float = 0.03  # dist step [m] kinematic
    LENGTH: float = 0.50  # Length of the vehicle [m]
    WIDTH: float = 0.2700  # Width of the vehicle [m]
    WB: float = 0.3240  # Wheelbase [m]
    MIN_STEER: float = -0.5236 #$-0.4236  # maximum steering angle [rad]
    MAX_STEER: float = 0.5236 #0.4236  # maximum steering angle [rad]
    MAX_DSTEER: float = np.deg2rad(180.0)  # maximum steering speed [rad/s]    
    MAX_SPEED: float = 1.0  # maximum speed [m/s]
    MIN_SPEED: float = 0.0  # minimum backward speed [m/s]
    MAX_ACCEL: float = 1.0  # maximum acceleration [m/ss]



@dataclass
class State:
    x: float = 0.0
    y: float = 0.0
    delta: float = 0.0
    v: float = 0.0
    yaw: float = 0.0
    yawrate: float = 0.0
    beta: float = 0.0


class MPC(Node):
    """ 
    Implement Kinematic MPC on the car
    This is just a template, you are free to implement your own node!
    """
    def __init__(self):
    #def __init__(self,image_queue):
        super().__init__('mpc_node')
        # use the MPC as a tracker (similar to pure pursuit)
        self.is_real = True
        #self.map_name = 'levine_2nd'
        #self.map_name = 'Spielberg_raceline'
        #self.map_name = 'map_2_f1tenth'
        #self.map_name = 'levine_centerline'
        # self.map_name = 'siccs_first_floor_1'
        self.map_name = 'generated_square_trajectory_small'
        
        self.enable_drive = True  # enable drive message publishing

        #YOLO setup from stopsign
        #self.get_logger().info("Loading YOLO...")
        #self.model = YOLO("yolo26n.pt")
        #if torch.cuda.is_available():
        #    self.model.to('cuda')
        #    self.get_logger().info("YOLO Model loaded. Driving...")
        #else:
        #    self.get_logger().info("uh oh")
        #self.get_logger().info("Warming up")
        #dummy_frame = np.zeros((480,640,3),dtype=np.uint8)
        #_ = self.model(dummy_frame,device = 'cuda', stream = False, verbose = False)
        #self.get_logger().info("Ok lets go now")
        #image sharing threads from stopsign
        self.image_lock = threading.Lock()
        self.latest_cv_image = None
        self.latest_depth_image = None
        self.bridge = CvBridge()
        self.car_should_stop = False 
        self.is_stopping_maneuver_active = False
        self.DETECTION_TRIGGER_DISTANCE = 10.0
        #self.image_queue = image_queue
        self.detect_lock = threading.Lock()
        self.planned_stop_time = 0.0
        self.cooldown_until = 0.0
        self.TARGET_STOP_DISTANCE = 0.30
        self.current_estimated_speed = 0.0
        self.speed_lock = threading.Lock()
        self.latest_pose_msg = None
        self.state_lock = threading.Lock()
        img_qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,history=HistoryPolicy.KEEP_LAST,depth=1)

        # create ROS subscribers and publishers
        # pose_topic = "/pf/viz/inferred_pose" if self.is_real else "/ego_racecar/odom"
        #pose_topic = "/optitrack/object_532/pose" if self.is_real else "/ego_racecar/odom"
        pose_topic = "/odom"
        #drive_topic = "/drive" #simtogg
        drive_topic = "/ackermann_cmd"
        vis_ref_traj_topic = "/ref_traj_marker"
        vis_waypoints_topic = "/waypoints_marker"
        vis_pred_path_topic = "/pred_path_marker"

        #image subscribers from stopsign
        self.stop_sign_sub = self.create_subscription(Float32, '/stop_sign/distance',self.stop_sign_distance_callback,1)
        #self.rgb_sub = Subscriber(self,Image,'/camera/camera/color/image_raw',qos_profile = img_qos)
        #self.depth_sub = Subscriber(self,Image,'/camera/camera/aligned_depth_to_color/image_raw',qos_profile=img_qos)
        #self.ts = ApproximateTimeSynchronizer([self.rgb_sub,self.depth_sub], queue_size=1, slop = 0.05)
        #self.ts.registerCallback(self.synchronized_image_callback)

        #self.pose_sub = self.create_subscription(PoseStamped if self.is_real else Odometry, pose_topic, self.pose_callback, 1)
        self.pose_sub = self.create_subscription(Odometry,pose_topic,self.pose_callback,qos_profile_sensor_data)
        self.pose_sub  # prevent unused variable warning

        self.control_timer = self.create_timer(0.025,self.control_loop_callback)
               

        self.obs_1 = self.create_subscription(Odometry, "/optitrack/object_530/odom", self.obs_1_callback, 10)
        self.obs_2 = self.create_subscription(Odometry, "/optitrack/object_531/odom", self.obs_2_callback, 10)

        self.drive_pub = self.create_publisher(AckermannDriveStamped, drive_topic, 1)
        self.drive_msg = AckermannDriveStamped()

        self.vis_waypoints_pub = self.create_publisher(Marker, vis_waypoints_topic, 1)
        self.vis_waypoints_msg = Marker()
        self.vis_ref_traj_pub = self.create_publisher(Marker, vis_ref_traj_topic, 1)
        self.vis_ref_traj_msg = Marker()
        self.vis_pred_path_pub = self.create_publisher(Marker, vis_pred_path_topic, 1)
        self.vis_pred_path_msg = Marker()

        #map_path = os.path.abspath(os.path.join('src', 'f1tenth-software-stack','csv_data'))

        #print("[DEBUG] :", map_path)
        
        #self.waypoints = np.loadtxt(map_path + '/' + self.map_name + '.csv', delimiter=';', skiprows=0)  # csv data
        #self.waypoints = np.loadtxt(map_path + '/' + self.map_name + '_centerline.csv', delimiter=',', skiprows=1)  # csv data F1tenth centerline
        self.waypoints = np.loadtxt(self.map_name + '.csv', delimiter=',', skiprows=1)  # csv data F1tenth 
        #self.waypoints = np.loadtxt(map_path + '/' + self.map_name + '.csv', delimiter=';', skiprows=3)
        
        self.ref_pos_x = self.waypoints[:, 0]  # x position
        self.ref_pos_y = self.waypoints[:, 1]  # y position
        #self.ref_speed = self.waypoints[:, 5] * 1.5  # speed profile
        
        # for those who do not have speed profile in the csv file
        self.ref_speed = np.ones(len(self.waypoints)) * 1.0  # speed profile
        
        dx = np.gradient(self.ref_pos_x) # for levine is 1 colunm ahead [1]
        dy = np.gradient(self.ref_pos_y) # for levine is 1 colunm ahead [2]
        yaw = np.arctan2(dy, dx)
        self.heading_yaw = np.unwrap(yaw)
        

        
        
        if self.map_name == 'levine_2nd':
            self.heading_yaw += math.pi / 2
        self.visualize_waypoints_in_rviz()

        self.config = mpc_config()
        self.odelta_v = None
        self.odelta = None
        self.oa = None
        self.init_flag = 0

        # initialize MPC problem
        self.mpc_prob_init()

        # init state - avoid unknown variables for scan callback
        self.curr_pos = np.array([0.0, 0.0, 0.0])
        self.rot_mat = np.identity(3)
    
        self.obs_1_x = 0.0
        self.obs_1_y = 0.0
        self.obs_2_x = 0.0
        self.obs_2_y = 0.0

        #start da yolo thread from stopsign
        #self.yolo_thread = threading.Thread(target=self.yolo_worker_loop, daemon = True)
        #self.yolo_thread.start()
        self.get_logger().info("initalized lets go now")
    #from stopsign
    def synchronized_image_callback(self, rgb_msg, depth_msg):
        try:
            with self.image_lock:
                if self.latest_cv_image is not None:
                    return 
            cv_img = self.bridge.imgmsg_to_cv2(rgb_msg,desired_encoding="bgr8")
            depth_img = self.bridge.imgmsg_to_cv2(depth_msg,desired_encoding="16UC1")
            with self.image_lock:
                self.latest_cv_image = cv_img
                self.latest_depth_image = depth_img
        except Exception as e:
            self.get_logger().error(f"It aint synching {e}")
        
    #from stopsign
    def yolo_worker_loop(self):
        while rclpy.ok():
            img_to_process = None
            depth_to_process = None 
            with self.image_lock:
                if self.latest_cv_image is not None and self.latest_depth_image is not None:
                    img_to_process = self.latest_cv_image.copy()
                    depth_to_process = self.latest_depth_image.copy()
                    self.latest_cv_image = None
                    self.latest_depth_image = None 
            if img_to_process is None or depth_to_process is None:
                time.sleep(0.01)
                continue
            current_time = time.time()
            results = self.model(img_to_process,device = 'cuda', imgsz=640,stream=False,verbose=False)
            closest_sign_distance = float('inf')
            sign_detected = False 
            annotated_img = img_to_process.copy()
          
            for r in results:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    label = self.model.names[class_id]
                    confidence = float(box.conf[0])
                    if label == 'stop sign' and confidence > 0.2:
                        sign_detected = True
                        x1,y1,x2,y2 = map(int,box.xyxy[0].cpu().numpy())           
                        y1,y2 = max(0,y1), min(depth_to_process.shape[0],y2)
                        x1,x2 = max(0,x1), min(depth_to_process.shape[1],x2)
                        #depth_crop = depth_to_process[ny1:ny2,nx1:nx2]
                        distance_m = float('inf')
                        if depth_crop.size > 0:
                            valid_depths = depth_crop[depth_crop > 0]
                            if valid_depths.size > 0:
                                median_mm = np.percentile(valid_depths)
                                distance_m = median_mm/1000.0
                                if (distance_m <= self.DETECTION_TRIGGER_DISTANCE and distance_m > self.TARGET_STOP_DISTANCE and current_time > self.cooldown_until):
                                    distance_to_travel = distance_m - self.TARGET_STOP_DISTANCE
                                    with self.speed_lock:
                                        current_speed = max(0.2,self.current_estimated_speed)
                                    #current_speed = max(0.2,self.drive_msg.drive.speed)
                                    dynamic_brake_lag = (current_speed*0.268) + 0.0175
                                    #time_until_stop = (distance_to_travel / current_speed) - dynamic_brake_lag
                                    time_until_stop = 0.0
                                    time_until_stop = max(0.0,time_until_stop)
                                    
                                    if not self.is_stopping_maneuver_active:
                                        self.planned_stop_time = current_time + time_until_stop
                                        self.is_stopping_maneuver_active = True 
                        box_color = (0,0,255) if distance_m <= self.DETECTION_TRIGGER_DISTANCE else (0,255,0)
                        cv2.rectangle(annotated_img,(x1,y1),(x2,y2),box_color,3)
                        if distance_m < closest_sign_distance:
                            closest_sign_distance = distance_m
            if sign_detected:
                if not self.is_stopping_maneuver_active and not self.car_should_stop:
                    self.is_stopping_maneuver_active = True 
                    self.planned_stop_time = current_time + 2.5
            else:
                if self.is_stopping_maneuver_active or self.car_should_stop:
                    self.is_stopping_maneuver_active = False 
                    self.car_should_stop = False 
                    self.planned_stop_time = 0.0

            if self.is_stopping_maneuver_active and current_time >= self.planned_stop_time:
                self.car_should_stop = True 
            status_text = "STOOOOOP" if sign_detected else ("okay lets stop now" if self.is_stopping_maneuver_active else "GOGOGOGOGOGO")
            status_color = (0,0,255) if (self.car_should_stop or self.is_stopping_maneuver_active) else (0,255,0)
            cv2.rectangle(annotated_img,(10,10),(290,75),(0,0,0),-1)
            cv2.putText(annotated_img,status_text,(20,35),cv2.FONT_HERSHEY_SIMPLEX,0.7,status_color,2)
            dist_str = f"{closest_sign_distance:.2f}m away" if sign_detected else "No sign :("
            cv2.putText(annotated_img,dist_str,(20,65),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),1)
            #if self.image_queue.full():
            #    try:
            #        self.image_queue.get_nowait()
            #    except Exception:
            #        pass 
            #try:
            #    self.image_queue.put(annotated_img)
            #except Exception:
            #    pass 
            time.sleep(0.01)
    def stop_sign_distance_callback(self,msg):
        distance_m = msg.data 
        current_time = time.time()
        with self.detect_lock:
            if self.car_should_stop:
                if not hasattr(self,'stop_start_time') or self.stop_start_time is None:
                    self.stop_start_time = current_time
                    self.get_logger().info("STOP THE CAR AHHHHH")
                elif current_time - self.stop_start_time >= 3.0:
                    self.get_logger().info("Everythings fine :) <3")
                    self.car_should_stop = False
                    self.is_stopping_maneuver_active = False 
                    self.stop_start_time = None 
                    self.cooldown_until = current_time + 5.0
                return 
            if distance_m > 0:  
                self.get_logger().warn(f"STOP SIGN AHHHHH ITS SOOO CLOSE LIKE {distance_m:.2f} AWAY AHHHHH")
                if (distance_m <= self.DETECTION_TRIGGER_DISTANCE and distance_m > self.TARGET_STOP_DISTANCE and current_time > self.cooldown_until):
                    distance_to_travel = distance_m - self.TARGET_STOP_DISTANCE
                    with self.speed_lock:
                        current_speed = max(0.2, self.current_estimated_speed)
                    
                    dynamic_brake_lag = (current_speed * 0.268) + 0.0175
                    time_until_stop = (distance_to_travel / current_speed) - dynamic_brake_lag
                    time_until_stop = max(0.0, time_until_stop)
                    
                    if not self.is_stopping_maneuver_active:
                        self.planned_stop_time = current_time + time_until_stop
                        self.is_stopping_maneuver_active = True 
                
                if not self.is_stopping_maneuver_active and not self.car_should_stop:
                    self.is_stopping_maneuver_active = True 
                    self.planned_stop_time = current_time + 2.5
                    self.stop_start_time = current_time
            else:  
                if self.is_stopping_maneuver_active or self.car_should_stop:
                    #self.is_stopping_maneuver_active = False 
                    #self.car_should_stop = False 
                    #self.planned_stop_time = 0.0
                    pass 

            if self.is_stopping_maneuver_active and current_time >= self.planned_stop_time:
                self.car_should_stop = True


    def obs_1_callback(self, msg):
        self.obs_1_x = msg.pose.pose.position.x
        self.obs_1_y = msg.pose.pose.position.y

    def obs_2_callback(self, msg):
        self.obs_2_x = msg.pose.pose.position.x
        self.obs_2_y = msg.pose.pose.position.y
    def pose_callback(self,pose_msg):
        with self.state_lock:
            self.latest_pose_msg = pose_msg

    def control_loop_callback(self):
        with self.state_lock:
            pose_msg = self.latest_pose_msg
        if pose_msg is None:
            return 
        current_time = time.time()
        with self.detect_lock:
            if self.car_should_stop:
                self.drive_msg.drive.speed = 0.0
                self.drive_msg.drive.steering_angle = 0.0
                if self.enable_drive:
                    self.drive_pub.publish(self.drive_msg)
                return
        vehicle_state = self.update_vehicle_state(pose_msg)
        with self.speed_lock:
            self.current_estimated_speed = vehicle_state.v
        with self.detect_lock:
            if self.is_stopping_maneuver_active and not self.car_should_stop:
                time_left = max(0.0,self.planned_stop_time - current_time)
                dist_remaining = time_left*max(0.1,vehicle_state.v)
                safe_v = math.sqrt(2.0*(self.config.MAX_ACCEL*0.7)*max(0.05,dist_remaining))
                local_ref_speed = np.minimum(self.ref_speed, safe_v)
            else:
                local_ref_speed = self.ref_speed
        
        # extract pose from ROS msg
        self.update_rotation_matrix(pose_msg)
        vehicle_state = self.update_vehicle_state(pose_msg)

        if self.is_real:
            # vehicle_state.v = -1 * vehicle_state.v  # negate the monitoring speed
            #vehicle_state.v = 1 * vehicle_state.v  # negate the monitoring speed
            vehicle_state.v = self.drive_msg.drive.speed

        # TODO: Calculate the next reference trajectory for the next T steps with current vehicle pose.
        # ref_x, ref_y, ref_yaw, ref_v are columns of self.waypoints
        ref_path = self.calc_ref_trajectory(vehicle_state, self.ref_pos_x, self.ref_pos_y, self.heading_yaw, self.ref_speed)
        #ref_path = self.calc_ref_trajectory(vehicle_state, self.waypoints[:, 0], self.waypoints[:, 1], self.waypoints[:, 2], self.waypoints[:, 3]) # f1tenth AutoDrive
        # print(ref_path)
        self.visualize_ref_traj_in_rviz(ref_path)
        
        x0 = [vehicle_state.x, vehicle_state.y, vehicle_state.v, vehicle_state.yaw]
        # print(vehicle_state.v)

        # solve the MPC control problem
        (
            self.oa,
            self.odelta_v,
            ox,
            oy,
            oyaw,
            ov,
            state_predict,
        ) = self.linear_mpc_control(ref_path, x0, self.oa, self.odelta_v)

        # publish drive message.
        if self.odelta_v is not None and self.oa is not None:
            steer_output = self.odelta_v[0]
            speed_output = vehicle_state.v + self.oa[0] * self.config.DTK

            self.drive_msg.drive.steering_angle = steer_output
            self.drive_msg.drive.speed = 1.0 * speed_output
            #self.drive_msg.drive.speed = (-1.0 if self.is_real else 1.0) * speed_output
        
            ######## PUBLISH DRIVE FOR CAR ##############################
            if self.enable_drive:
                self.drive_pub.publish(self.drive_msg)
        #"statistics" - timmy chalamet
        #print("steering ={}, speed ={}".format(self.drive_msg.drive.steering_angle, self.drive_msg.drive.speed))

        self.vis_waypoints_pub.publish(self.vis_waypoints_msg)

    # toolkits
    def update_rotation_matrix(self, pose_msg):
        # get rotation matrix from the car frame to the world frame
     #   curr_orien = pose_msg.pose.orientation if self.is_real else pose_msg.pose.pose.orientation
        curr_orien = pose_msg.pose.pose.orientation
     
        quat = [curr_orien.x, curr_orien.y, curr_orien.z, curr_orien.w]
        self.rot_mat = (transform.Rotation.from_quat(quat)).as_matrix()
        # print("rotation matrix = {}".format(self.rot_mat))

    def update_vehicle_state(self, pose_msg):
        """
        written by Derek, not from the template, != update state
        """
        vehicle_state = State()
#        vehicle_state.x = pose_msg.pose.position.x if self.is_real else pose_msg.pose.pose.position.x
        vehicle_state.x =  pose_msg.pose.pose.position.x

      #  vehicle_state.y = pose_msg.pose.position.y if self.is_real else pose_msg.pose.pose.position.y
        vehicle_state.y = pose_msg.pose.pose.position.y

        vehicle_state.v = self.drive_msg.drive.speed

    #    curr_orien = pose_msg.pose.orientation if self.is_real else pose_msg.pose.pose.orientation
        curr_orien =  pose_msg.pose.pose.orientation
        q = [curr_orien.x, curr_orien.y, curr_orien.z, curr_orien.w]
        vehicle_state.yaw = math.atan2(2 * (q[3] * q[2] + q[0] * q[1]), 1 - 2 * (q[1] ** 2 + q[2] ** 2))
        # https://en.wikipedia.org/wiki/Rotation_formalisms_in_three_dimensions#Quaternion_%E2%86%92_Euler_angles_(z-y%E2%80%B2-x%E2%80%B3_intrinsic)
        # print("yaw =", vehicle_state.yaw)

        return vehicle_state

    # mpc functions
    def mpc_prob_init(self):
        """
        Create MPC quadratic optimization problem using cvxpy, solver: OSQP
        Will be solved every iteration for control.
        More MPC problem information here: https://osqp.org/docs/examples/mpc.html
        More QP example in CVXPY here: https://www.cvxpy.org/examples/basic/quadratic_program.html
        """
        # Initialize and create vectors for the optimization problem
        # Vehicle State Vector
        self.xk = cvxpy.Variable(
            (self.config.NXK, self.config.TK + 1)  # 4 x 9
        )
        # Control Input vector
        self.uk = cvxpy.Variable(
            (self.config.NU, self.config.TK)  # 2 x 8
        )
        objective = 0.0  # Objective value of the optimization problem
        constraints = []  # Create constraints array

        # Initialize reference vectors
        self.x0k = cvxpy.Parameter((self.config.NXK,))  # 4
        self.x0k.value = np.zeros((self.config.NXK,))

        # Initialize reference trajectory parameter
        self.ref_traj_k = cvxpy.Parameter((self.config.NXK, self.config.TK + 1))  # 4 x 9
        self.ref_traj_k.value = np.zeros((self.config.NXK, self.config.TK + 1))

        # Initializes block diagonal form of R = [R, R, ..., R] (NU*T, NU*T)
        R_block = block_diag(tuple([self.config.Rk] * self.config.TK))  # (2 * 8) x (2 * 8)

        # Initializes block diagonal form of Rd = [Rd, ..., Rd] (NU*(T-1), NU*(T-1))
        Rd_block = block_diag(tuple([self.config.Rdk] * (self.config.TK - 1)))  # (2 * 7) x (2 * 7)

        # Initializes block diagonal form of Q = [Q, Q, ..., Qf] (NX*T, NX*T)
        Q_block = [self.config.Qk] * (self.config.TK)  # (4 * 8) x (4 * 8)
        Q_block.append(self.config.Qfk)
        Q_block = block_diag(tuple(Q_block))  # (4 * 9) x (4 * 9), Qk + Qfk

        # Formulate and create the finite-horizon optimal control problem (objective function)
        # The FTOCP has the horizon of T timesteps

        # --------------------------------------------------------
        # TODO: fill in the objectives here, you should be using cvxpy.quad_form() somehwhere
        
        # Objective part 1: Influence of the control inputs: Inputs u multiplied by the penalty R
        objective += cvxpy.quad_form(cvxpy.vec(self.uk, order='F'), R_block)  # # cvxpy.vec() - Flattens the matrix X into a vector in column-major order

        # Objective part 2: Deviation of the vehicle from the reference trajectory weighted by Q, including final Timestep T weighted by Qf
        objective += cvxpy.quad_form(cvxpy.vec(self.xk - self.ref_traj_k,order='F'), Q_block)

        # Objective part 3: Difference from one control input to the next control input weighted by Rd
        objective += cvxpy.quad_form(cvxpy.vec(cvxpy.diff(self.uk, axis=1),order='F'), Rd_block)
        # --------------------------------------------------------

        # Constraints 1: Calculate the future vehicle behavior/states based on the vehicle dynamics model matrices
        # Evaluate vehicle Dynamics for next T timesteps
        A_block = []
        B_block = []
        C_block = []
        # init path to zeros
        path_predict = np.zeros((self.config.NXK, self.config.TK + 1))  # 4 x 9
        for t in range(self.config.TK):  # 8
            A, B, C = self.get_model_matrix(
                path_predict[2, t], path_predict[3, t], 0.0  # reference steering angle is zero
            )
            A_block.append(A)
            B_block.append(B)
            C_block.extend(C)

        A_block = block_diag(tuple(A_block))  # 32 x 32
        B_block = block_diag(tuple(B_block))  # 32 x 16
        C_block = np.array(C_block)  # 32 x 1
        # creating the format of matrices

        # [AA] Sparse matrix to CVX parameter for proper stuffing
        # Reference: https://github.com/cvxpy/cvxpy/issues/1159#issuecomment-718925710
        m, n = A_block.shape  # 32, 32
        self.Annz_k = cvxpy.Parameter(A_block.nnz)  # nnz: number of nonzero elements, nnz = 128
        data = np.ones(self.Annz_k.size)  # 128 x 1, size = 128, all elements are 1
        rows = A_block.row * n + A_block.col  # No. ? element in 32 x 32 matrix
        cols = np.arange(self.Annz_k.size)  # 128 elements that need to be care - diagonal & nonzero, 4 x 4 x 8
        Indexer = csc_matrix((data, (rows, cols)), shape=(m * n, self.Annz_k.size))	 # (rows, cols)	data

        # Setting sparse matrix data
        self.Annz_k.value = A_block.data

        # Now we use this sparse version instead of the old A_block matrix
        self.Ak_ = cvxpy.reshape(Indexer @ self.Annz_k, (m, n), order="C")
        # https://www.cvxpy.org/api_reference/cvxpy.atoms.affine.html#cvxpy.reshape

        # Same as A
        m, n = B_block.shape  # 32, 16 = 4 x 8, 2 x 8
        self.Bnnz_k = cvxpy.Parameter(B_block.nnz)  # nnz = 64
        data = np.ones(self.Bnnz_k.size)  # 64 = (4 x 2) x 8
        rows = B_block.row * n + B_block.col  # No. ? element in 32 x 16 matrix
        cols = np.arange(self.Bnnz_k.size)  # 0, 1, ... 63
        Indexer = csc_matrix((data, (rows, cols)), shape=(m * n, self.Bnnz_k.size))  # (rows, cols)	data
        
        # sparse version instead of the old B_block
        self.Bk_ = cvxpy.reshape(Indexer @ self.Bnnz_k, (m, n), order="C")
        
        # real data
        self.Bnnz_k.value = B_block.data

        # No need for sparse matrices for C as most values are parameters
        self.Ck_ = cvxpy.Parameter(C_block.shape)
        self.Ck_.value = C_block

        # -------------------------------------------------------------
        # TODO: Constraint part 1:
        #       Add dynamics constraints to the optimization problem
        #       This constraint should be based on a few variables:
        #       self.xk, self.Ak_, self.Bk_, self.uk, and self.Ck_
        
        flatten_prev_xk = cvxpy.vec(self.xk[:, :-1],order='F')
        flatten_next_xk = cvxpy.vec(self.xk[:, 1:],order='F')
        # flatten_uk = cvxpy.diag(self.uk[:, :-1].flatten())
        # import pdb; pdb.set_trace()
        c1 = flatten_next_xk == self.Ak_ @ flatten_prev_xk + self.Bk_ @ cvxpy.vec(self.uk,order='F') + self.Ck_
        constraints.append(c1)
        
        # TODO: Constraint part 2:
        #       Add constraints on steering, change in steering angle
        #       cannot exceed steering angle speed limit. Should be based on:
        #       self.uk, self.config.MAX_DSTEER, self.config.DTK
        
        dsteering = cvxpy.diff(self.uk[1, :])
        c2_lower = -self.config.MAX_DSTEER * self.config.DTK <= dsteering
        c2_upper = dsteering <= self.config.MAX_DSTEER * self.config.DTK
        constraints.append(c2_lower)
        constraints.append(c2_upper)
        
        # TODO: Constraint part 3:
        #       Add constraints on upper and lower bounds of states and inputs
        #       and initial state constraint, should be based on:
        #       self.xk, self.x0k, self.config.MAX_SPEED, self.config.MIN_SPEED,
        #       self.uk, self.config.MAX_ACCEL, self.config.MAX_STEER
        
        # init state constraint
        c3 = self.xk[:, 0] == self.x0k
        constraints.append(c3)

        # state consraints
        speed = self.xk[2, :]
        c4_lower = self.config.MIN_SPEED <= speed
        c4_upper = speed <= self.config.MAX_SPEED
        constraints.append(c4_lower)
        constraints.append(c4_upper)

        # input constraints
        steering = self.uk[1, :]
        c5_lower = self.config.MIN_STEER <= steering
        c5_upper = steering <= self.config.MAX_STEER
        constraints.append(c5_lower)
        constraints.append(c5_upper)

        acc = self.uk[0, :]
        c6 = acc <= self.config.MAX_ACCEL
        constraints.append(c6)

        # -------------------------------------------------------------



        # Create the optimization problem in CVXPY and setup the workspace
        # Optimization goal: minimize the objective function
        self.MPC_prob = cvxpy.Problem(cvxpy.Minimize(objective), constraints)

    def calc_ref_trajectory(self, state, cx, cy, cyaw, sp):
        """
        calc referent trajectory ref_traj in T steps: [x, y, v, yaw]
        using the current velocity, calc the T points along the reference path
        :param cx: Course X-Position
        :param cy: Course y-Position
        :param cyaw: Course Heading
        :param sp: speed profile
        :dl: distance step
        :pind: Setpoint Index
        :return: reference trajectory ref_traj, reference steering angle
        """

        # Create placeholder Arrays for the reference trajectory for T steps
        ref_traj = np.zeros((self.config.NXK, self.config.TK + 1))
        ncourse = len(cx)

        # Find nearest index/setpoint from where the trajectories are calculated
        _, _, _, ind = nearest_point(np.array([state.x, state.y]), np.array([cx, cy]).T)

        # Load the initial parameters from the setpoint into the trajectory
        ref_traj[0, 0] = cx[ind]
        ref_traj[1, 0] = cy[ind]
        ref_traj[2, 0] = sp[ind]
        ref_traj[3, 0] = cyaw[ind]

        # based on current velocity, distance traveled on the ref line between time steps
        travel = abs(state.v) * self.config.DTK
        dind = travel / self.config.dlk
        #dind = 2
        ind_list = int(ind) + np.insert(
            np.cumsum(np.repeat(dind, self.config.TK)), 0, 0
        ).astype(int)
        ind_list[ind_list >= ncourse] -= ncourse
        ref_traj[0, :] = cx[ind_list]
        ref_traj[1, :] = cy[ind_list]
        ref_traj[2, :] = sp[ind_list]

        angle_thres = 4.5
        # https://edstem.org/us/courses/34340/discussion/2817574

        for i in range(len(cyaw)):
            if cyaw[i] - state.yaw > angle_thres:
                cyaw[i] -= 2*np.pi
            if state.yaw - cyaw[i] > angle_thres:
                cyaw[i] += 2*np.pi

        # cyaw[cyaw - state.yaw > angle_thres] = np.abs(
        #     cyaw[cyaw - state.yaw > angle_thres] - (2 * np.pi)
        # )
        # cyaw[cyaw - state.yaw < -angle_thres] = np.abs(
        #     cyaw[cyaw - state.yaw < -angle_thres] + (2 * np.pi)
        # )
        ref_traj[3, :] = cyaw[ind_list]
        #"more statistics" - timmy chalamet
        #print("ref_yaw ={}, cur_yaw ={}".format(cyaw[ind], state.yaw))
        #print(" ")

        return ref_traj

    def predict_motion(self, x0, oa, od, xref):
        path_predict = xref * 0.0
        for i, _ in enumerate(x0):
            path_predict[i, 0] = x0[i]

        state = State(x=x0[0], y=x0[1], yaw=x0[3], v=x0[2])
        for (ai, di, i) in zip(oa, od, range(1, self.config.TK + 1)):
            state = self.update_state(state, ai, di)
            path_predict[0, i] = state.x
            path_predict[1, i] = state.y
            path_predict[2, i] = state.v
            path_predict[3, i] = state.yaw

        return path_predict

    def update_state(self, state, a, delta):

        # input check
        if delta >= self.config.MAX_STEER:
            delta = self.config.MAX_STEER
        elif delta <= -self.config.MAX_STEER:
            delta = -self.config.MAX_STEER

        state.x = state.x + state.v * math.cos(state.yaw) * self.config.DTK
        state.y = state.y + state.v * math.sin(state.yaw) * self.config.DTK
        state.yaw = (
            state.yaw + (state.v / self.config.WB) * math.tan(delta) * self.config.DTK
        )
        state.v = state.v + a * self.config.DTK

        if state.v > self.config.MAX_SPEED:
            state.v = self.config.MAX_SPEED
        elif state.v < self.config.MIN_SPEED:
            state.v = self.config.MIN_SPEED

        return state

    def get_model_matrix(self, v, phi, delta):
        """
        Calc linear and discrete time dynamic model-> Explicit discrete time-invariant
        Linear System: Xdot = Ax +Bu + C
        State vector: x=[x, y, v, yaw]
        :param v: speed
        :param phi: heading angle of the vehicle
        :param delta: steering angle: delta_bar
        :return: A, B, C
        """

        # State (or system) matrix A, 4x4
        A = np.zeros((self.config.NXK, self.config.NXK))
        A[0, 0] = 1.0
        A[1, 1] = 1.0
        A[2, 2] = 1.0
        A[3, 3] = 1.0
        A[0, 2] = self.config.DTK * math.cos(phi)
        A[0, 3] = -self.config.DTK * v * math.sin(phi)
        A[1, 2] = self.config.DTK * math.sin(phi)
        A[1, 3] = self.config.DTK * v * math.cos(phi)
        A[3, 2] = self.config.DTK * math.tan(delta) / self.config.WB

        # Input Matrix B; 4x2
        B = np.zeros((self.config.NXK, self.config.NU))
        B[2, 0] = self.config.DTK
        B[3, 1] = self.config.DTK * v / (self.config.WB * math.cos(delta) ** 2)

        C = np.zeros(self.config.NXK)
        C[0] = self.config.DTK * v * math.sin(phi) * phi
        C[1] = -self.config.DTK * v * math.cos(phi) * phi
        C[3] = -self.config.DTK * v * delta / (self.config.WB * math.cos(delta) ** 2)

        return A, B, C  # 4 x 4, 4 x 2, 4 x 1



    def mpc_prob_solve(self, ref_traj, path_predict, x0):
        self.x0k.value = x0

        A_block = []
        B_block = []
        C_block = []
        for t in range(self.config.TK):
            A, B, C = self.get_model_matrix(
                path_predict[2, t], path_predict[3, t], 0.0
            )
            A_block.append(A)
            B_block.append(B)
            C_block.extend(C)

        A_block = block_diag(tuple(A_block))
        B_block = block_diag(tuple(B_block))
        C_block = np.array(C_block)

        self.Annz_k.value = A_block.data
        self.Bnnz_k.value = B_block.data
        self.Ck_.value = C_block

        self.ref_traj_k.value = ref_traj

        # Solve the optimization problem in CVXPY
        # Solver selections: cvxpy.OSQP; cvxpy.GUROBI
        self.MPC_prob.solve(solver=cvxpy.OSQP, verbose=False, warm_start=True)

        if (
            self.MPC_prob.status == cvxpy.OPTIMAL
            or self.MPC_prob.status == cvxpy.OPTIMAL_INACCURATE
        ):
            ox = np.array(self.xk.value[0, :]).flatten()
            oy = np.array(self.xk.value[1, :]).flatten()
            ov = np.array(self.xk.value[2, :]).flatten()
            oyaw = np.array(self.xk.value[3, :]).flatten()
            oa = np.array(self.uk.value[0, :]).flatten()
            odelta = np.array(self.uk.value[1, :]).flatten()

        else:
            print("Error: Cannot solve mpc..")
            oa, odelta, ox, oy, oyaw, ov = None, None, None, None, None, None

        return oa, odelta, ox, oy, oyaw, ov


    def linear_mpc_control(self, ref_path, x0, oa, od):
        """
        MPC control with updating operational point iteraitvely
        :param ref_path: reference trajectory in T steps
        :param x0: initial state vector
        :param oa: acceleration of T steps of last time
        :param od: delta of T steps of last time
        """

        if oa is None or od is None:
            oa = [0.0] * self.config.TK
            od = [0.0] * self.config.TK

        # Call the Motion Prediction function: Predict the vehicle motion for x-steps
        path_predict = self.predict_motion(x0, oa, od, ref_path)
        # sth to be done to fix the path?
        self.visualize_pred_path_in_rviz(path_predict)

        poa, pod = oa[:], od[:]

        # Run the MPC optimization: Create and solve the optimization problem
        mpc_a, mpc_delta, mpc_x, mpc_y, mpc_yaw, mpc_v = self.mpc_prob_solve(
            ref_path, path_predict, x0
        )
        
        # mpc_a, mpc_delta, mpc_x, mpc_y, mpc_yaw, mpc_v = self.mpc_prob_solve(
        #     ref_path, path_predict, x0, oa, od
        # )

        return mpc_a, mpc_delta, mpc_x, mpc_y, mpc_yaw, mpc_v, path_predict

    # visualization
    def visualize_waypoints_in_rviz(self):
        self.vis_waypoints_msg.points = []
        #self.vis_waypoints_msg.header.frame_id = '/map' #simtogg
        self.vis_waypoints_msg.header.frame_id = '/odom'
        self.vis_waypoints_msg.type = Marker.POINTS
        self.vis_waypoints_msg.color.g = 0.75
        self.vis_waypoints_msg.color.a = 1.0
        self.vis_waypoints_msg.scale.x = 0.05
        self.vis_waypoints_msg.scale.y = 0.05
        self.vis_waypoints_msg.id = 0
        for i in range(self.waypoints.shape[0]):
            #point = Point(x = self.waypoints[i, 1], y = self.waypoints[i, 2], z = 0.1)
            point = Point(x = self.ref_pos_x[i], y = self.ref_pos_y[i], z = 0.1)
            #point = Point(x = self.waypoints[i, 0], y = self.waypoints[i, 1], z = 0.1) # f1tenth AutoDrive
            self.vis_waypoints_msg.points.append(point)
        
        # self.vis_waypoints_pub.publish(self.vis_waypoints_msg)

    def visualize_ref_traj_in_rviz(self, ref_traj):
        # visualize the path data in the world frame
        self.vis_ref_traj_msg.points = []
        #self.vis_ref_traj_msg.header.frame_id = '/map' #simtogg
        self.vis_ref_traj_msg.header.frame_id = '/odom'
        self.vis_ref_traj_msg.type = Marker.LINE_STRIP
        self.vis_ref_traj_msg.color.b = 0.75
        self.vis_ref_traj_msg.color.a = 1.0
        self.vis_ref_traj_msg.scale.x = 0.08
        self.vis_ref_traj_msg.scale.y = 0.08
        self.vis_ref_traj_msg.id = 0
        for i in range(ref_traj.shape[1]):
            point = Point(x = ref_traj[0, i], y = ref_traj[1, i], z = 0.2)
            self.vis_ref_traj_msg.points.append(point)
        
        self.vis_ref_traj_pub.publish(self.vis_ref_traj_msg)

    def visualize_pred_path_in_rviz(self, path_predict):
        # visualize the path data in the world frame
        self.vis_pred_path_msg.points = []
        #self.vis_pred_path_msg.header.frame_id = '/map' #simtogg
        self.vis_pred_path_msg.header.frame_id = '/odom'
        self.vis_pred_path_msg.type = Marker.LINE_STRIP
        self.vis_pred_path_msg.color.r = 0.75
        self.vis_pred_path_msg.color.a = 1.0
        self.vis_pred_path_msg.scale.x = 0.08
        self.vis_pred_path_msg.scale.y = 0.08
        self.vis_pred_path_msg.id = 0
        for i in range(path_predict.shape[1]):
            point = Point(x = path_predict[0, i], y = path_predict[1, i], z = 0.2)
            self.vis_pred_path_msg.points.append(point)
        
        self.vis_pred_path_pub.publish(self.vis_pred_path_msg)

def visualizer_process(image_queue,display_env,xauth_env):
    if display_env:
        os.environ["DISPLAY"] = display_env
    if xauth_env:
        os.environ["XAUTHORITY"] = xauth_env 
    window_name = "POV Rover"
    window_initialized = False
    while True:
        try:
            img_to_show = image_queue.get_nowait()
            if img_to_show is None:
                break
            if not window_initialized:
                cv2.namedWindow(window_name,cv2.WINDOW_AUTOSIZE)
                window_initialized = True 
                
            cv2.imshow(window_name, img_to_show)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except queue.Empty:
            time.sleep(0.01)
            continue
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            print(f"errm: {e}", file=sys.stderr)
            traceback.print_exc()
            time.sleep(0.01)
    cv2.destroyAllWindows()


def main(args=None):
    #try:
    #    mp.set_start_method('spawn')
    #except RuntimeError:
    #    pass 
    
    rclpy.init(args=args)
    #image_queue = mp.Queue(maxsize = 2)
    #current_display = os.environ.get("DISPLAY","")
    #current_xauth = os.environ.get("XAUTHORITY","")
    print("MPC Initialized")
    #ui_process = mp.Process(target=visualizer_process,args=(image_queue,current_display,current_xauth),daemon=True)
    #ui_process.start()
    #mpc_node = MPC(image_queue)
    mpc_node = MPC()
    #executor = rclpy.executors.MultiThreadedExecutor()
    #executor.add_node(mpc_node)
    try:
        rclpy.spin(mpc_node)
    except KeyboardInterrupt:
        pass
    finally:
        #image_queue.put(None)
        mpc_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
