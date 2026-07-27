#!/usr/bin/env python3
import os
import sys
import time
import threading
import traceback
import numpy as np
import cv2
import torch
from ultralytics import YOLO

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
from cv_bridge import CvBridge
from rclpy.qos import QoSProfile, HistoryPolicy, ReliabilityPolicy
from message_filters import Subscriber, ApproximateTimeSynchronizer
import multiprocessing as mp

def visualizer_process(image_queue, display_env, xauth_env):
    if display_env:
        os.environ["DISPLAY"] = display_env
    if xauth_env:
        os.environ["XAUTHORITY"] = xauth_env 
    window_name = "POV Rover"
    window_initialized = False
    
    while True:
        try:
            if not image_queue.empty():
                img_to_show = image_queue.get_nowait()
                if img_to_show is None:
                    break
                if not window_initialized:
                    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
                    window_initialized = True 
                
                cv2.imshow(window_name, img_to_show)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except mp.queues.Empty:
            time.sleep(0.01)
            continue
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            print(f"no more pov rover: {e}", file=sys.stderr)
            time.sleep(0.01)
            
    cv2.destroyAllWindows()

class StopSignDetector(Node):
    def __init__(self, image_queue):
        super().__init__('stop_sign_detector_node')
        self.image_queue = image_queue
        self.bridge = CvBridge()
        
        self.get_logger().info("Loading YOLO...")
        self.model = YOLO("yolo26n.pt")
        if torch.cuda.is_available():
            self.model.to('cuda')
            self.get_logger().info("YOLO loaded :)")
        else:
            self.get_logger().warn("ahhhh cpu spooooky")

        # Warmup
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        _ = self.model(dummy_frame, device='cuda' if torch.cuda.is_available() else 'cpu', verbose=False)

        self.image_lock = threading.Lock()
        self.latest_cv_image = None
        self.latest_depth_image = None

        # Publisher for lightweight distance primitive
        self.distance_pub = self.create_publisher(Float32, '/stop_sign/distance', 1)

        # Image synchronizers
        img_qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, history=HistoryPolicy.KEEP_LAST, depth=1)
        self.rgb_sub = Subscriber(self, Image, '/camera/camera/color/image_raw', qos_profile=img_qos)
        self.depth_sub = Subscriber(self, Image, '/camera/camera/aligned_depth_to_color/image_raw', qos_profile=img_qos)
        self.ts = ApproximateTimeSynchronizer([self.rgb_sub, self.depth_sub], queue_size=1, slop=0.05)
        self.ts.registerCallback(self.synchronized_image_callback)

        self.yolo_thread = threading.Thread(target=self.yolo_worker_loop, daemon=True)
        self.yolo_thread.start()

    def synchronized_image_callback(self, rgb_msg, depth_msg):
        try:
            cv_img = self.bridge.imgmsg_to_cv2(rgb_msg, desired_encoding="bgr8")
            depth_img = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding="16UC1")
            with self.image_lock:
                self.latest_cv_image = cv_img
                self.latest_depth_image = depth_img
        except Exception as e:
            self.get_logger().error(f"errm: {e}")

    def yolo_worker_loop(self):
        device_str = 'cuda' if torch.cuda.is_available() else 'cpu'
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

            results = self.model(img_to_process, device=device_str, imgsz=640, stream=False, verbose=False)
            closest_sign_distance = float('inf')
            sign_detected = False 
            annotated_img = img_to_process.copy()
          
            for r in results:
                for box in r.boxes:
                    class_id = int(box.cls[0])
                    label = self.model.names[class_id]
                    confidence = float(box.conf[0])
                    
                    if label == 'stop sign' and confidence > 0.4:
                        sign_detected = True
                        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                        y1, y2 = max(0, y1), min(depth_to_process.shape[0], y2)
                        x1, x2 = max(0, x1), min(depth_to_process.shape[1], x2)
                        depth_crop = depth_to_process[y1:y2,x1:x2]
                       
                        distance_m = float('inf')
                        if depth_crop.size > 0:
                            valid_depths = depth_crop[depth_crop > 0]
                            if valid_depths.size > 0:
                                median_mm = np.percentile(valid_depths, 25)
                                distance_m = median_mm / 1000.0
                        
                        box_color = (0, 0, 255) if distance_m <= 10.0 else (0, 255, 0)
                        cv2.rectangle(annotated_img, (x1, y1), (x2, y2), box_color, 3)
                        if distance_m < closest_sign_distance:
                            closest_sign_distance = distance_m

            # Publish the message to the control node
            msg = Float32()
            msg.data = closest_sign_distance if sign_detected else -1.0
            self.distance_pub.publish(msg)

            # Draw visualizer text overlay
            status_text = "STOOOOOP" if sign_detected else "GOGOGOGOGOGO"
            status_color = (0, 0, 255) if sign_detected else (0, 255, 0)
            cv2.rectangle(annotated_img, (10, 10), (290, 75), (0, 0, 0), -1)
            cv2.putText(annotated_img, status_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            dist_str = f"{closest_sign_distance:.2f}m away" if sign_detected else "No sign :("
            cv2.putText(annotated_img, dist_str, (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            if self.image_queue.full():
                try:
                    self.image_queue.get_nowait()
                except Exception:
                    pass 
            try:
                self.image_queue.put(annotated_img)
            except Exception:
                pass 
            time.sleep(0.01)

def main(args=None):
    try:
        mp.set_start_method('spawn')
    except RuntimeError:
        pass 
    
    rclpy.init(args=args)
    image_queue = mp.Queue(maxsize=2)
    current_display = os.environ.get("DISPLAY", "")
    current_xauth = os.environ.get("XAUTHORITY", "")
    
    #ui_process = mp.Process(target=visualizer_process, args=(image_queue, current_display, current_xauth), daemon=True)
    #ui_process.start()
    
    node = StopSignDetector(image_queue)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        image_queue.put(None)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()