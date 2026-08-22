#!/usr/bin/env python3
import os
os.environ.setdefault("XLA_PYTHON_CLIENT_PREALLOCATE", "false")

import math
import time
from pathlib import Path
from typing import NamedTuple

import jax
import jax.numpy as jnp
import numpy as np
import rclpy
import yaml
from ackermann_msgs.msg import AckermannDriveStamped
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Point, PoseStamped, Vector3
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Bool, Float32, Float32MultiArray
from visualization_msgs.msg import Marker

from stl_svpio import STLSVPIO


class TrafficContext(NamedTuple):
    other_xy: jax.Array
    other_valid: jax.Array
    stop_point: jax.Array
    stop_tangent: jax.Array
    stop_active: jax.Array
    must_yield: jax.Array


class F1TenthSTLEnv:
    """Differentiable F1TENTH model and STL robustness for traffic driving."""

    def __init__(self, dt, horizon, control_scale, config):
        self.dt = float(dt)
        self.horizon = int(horizon)
        self.control_scale = jnp.asarray(control_scale, dtype=jnp.float32)
        self.beta = float(config["smooth_beta"])
        self.lane_half_width = float(config["lane_half_width"])
        self.heading_tolerance = float(config["heading_tolerance"])
        self.speed_limit = float(config["speed_limit"])
        self.collision_distance = float(config["collision_distance"])
        self.goal_radius = float(config["goal_radius"])
        self.stop_zone = float(config["stop_zone"])
        self.stop_speed = float(config["stop_speed"])
        self.cross_margin = float(config["cross_margin"])
        self.hold_samples = min(
            self.horizon + 1,
            max(2, int(math.ceil(config["stop_hold_time"] / self.dt)) + 1),
        )

        self.lf = 0.15875
        self.lr = 0.17145
        self.steer_min = -0.4189
        self.steer_max = 0.4189
        self.steer_rate_min = -3.2
        self.steer_rate_max = 3.2
        self.accel_max = float(config["model_accel_limit"])
        self.velocity_min = 0.0
        self.velocity_max = self.speed_limit
        self.integration_dt = 0.05
        self.integration_steps = max(1, int(round(self.dt / self.integration_dt)))
        self.integration_dt = self.dt / self.integration_steps

    def _smooth_min(self, values, axis=None):
        return -jax.scipy.special.logsumexp(-self.beta * values, axis=axis) / self.beta

    def _smooth_max(self, values, axis=None):
        return jax.scipy.special.logsumexp(self.beta * values, axis=axis) / self.beta

    def _dynamics(self, state, normalized_control):
        steer_rate, accel = normalized_control * self.control_scale
        steer_rate = jnp.clip(steer_rate, self.steer_rate_min, self.steer_rate_max)
        accel = jnp.clip(accel, -self.accel_max, self.accel_max)
        steer_rate = jnp.where(
            ((state[2] <= self.steer_min) & (steer_rate < 0.0))
            | ((state[2] >= self.steer_max) & (steer_rate > 0.0)),
            0.0,
            steer_rate,
        )
        accel = jnp.where(
            ((state[3] <= self.velocity_min) & (accel < 0.0))
            | ((state[3] >= self.velocity_max) & (accel > 0.0)),
            0.0,
            accel,
        )
        wheelbase = self.lf + self.lr
        return jnp.array(
            [
                state[3] * jnp.cos(state[4]),
                state[3] * jnp.sin(state[4]),
                steer_rate,
                accel,
                state[3] * jnp.tan(state[2]) / wheelbase,
            ],
            dtype=jnp.float32,
        )

    def _integrate(self, state, control):
        dt = self.integration_dt

        def rk4_step(_, x):
            k1 = self._dynamics(x, control)
            k2 = self._dynamics(x + 0.5 * dt * k1, control)
            k3 = self._dynamics(x + 0.5 * dt * k2, control)
            k4 = self._dynamics(x + dt * k3, control)
            x_next = x + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
            x_next = x_next.at[2].set(jnp.clip(x_next[2], self.steer_min, self.steer_max))
            x_next = x_next.at[3].set(jnp.clip(x_next[3], self.velocity_min, self.velocity_max))
            return x_next

        return jax.lax.fori_loop(0, self.integration_steps, rk4_step, state)

    def rollout(self, initial_state, controls):
        def rollout_step(state, control):
            next_state = self._integrate(state, control)
            return next_state, next_state

        _, states = jax.lax.scan(rollout_step, initial_state, controls)
        return jnp.concatenate((initial_state[None, :], states), axis=0)

    def stl_robustness(self, states, reference, traffic):
        position = states[:, :2]
        speed = states[:, 3]
        ref_position = reference[:, :2]
        ref_yaw = reference[:, 2]

        position_error = position - ref_position
        lateral_error = (
            -jnp.sin(ref_yaw) * position_error[:, 0]
            + jnp.cos(ref_yaw) * position_error[:, 1]
        )
        rho_lane = self._smooth_min(self.lane_half_width - jnp.abs(lateral_error))
        heading_error = jnp.arctan2(
            jnp.sin(states[:, 4] - ref_yaw),
            jnp.cos(states[:, 4] - ref_yaw),
        )
        rho_heading = self._smooth_min(
            self.heading_tolerance - jnp.abs(heading_error)
        )
        rho_speed = self._smooth_min(self.speed_limit - speed)

        other_distance = jnp.linalg.norm(position - traffic.other_xy, axis=1)
        rho_collision = self._smooth_min(other_distance - self.collision_distance)
        rho_collision = jnp.where(traffic.other_valid > 0.5, rho_collision, 5.0)

        goal_predicate = self.goal_radius - jnp.linalg.norm(position - ref_position[-1], axis=1)
        rho_goal = self._smooth_max(goal_predicate)
        route_active = 1.0 - jnp.maximum(traffic.stop_active, traffic.must_yield)
        rho_goal = jnp.where(route_active > 0.5, rho_goal, 5.0)

        signed_stop_distance = (traffic.stop_point - position) @ traffic.stop_tangent
        rho_not_crossed = signed_stop_distance + self.cross_margin
        rho_stopped = self._smooth_min(
            jnp.stack(
                (
                    self.stop_zone - jnp.abs(signed_stop_distance),
                    self.stop_speed - jnp.abs(speed),
                ),
                axis=1,
            ),
            axis=1,
        )

        def prefix_min(carry, value):
            new_carry = self._smooth_min(jnp.stack((carry, value)))
            return new_carry, new_carry

        _, prefix_tail = jax.lax.scan(prefix_min, rho_not_crossed[0], rho_not_crossed[1:])
        prefix_not_crossed = jnp.concatenate((rho_not_crossed[:1], prefix_tail))
        until_candidates = self._smooth_min(
            jnp.stack((rho_stopped, prefix_not_crossed), axis=1), axis=1
        )
        rho_until_stop = self._smooth_max(until_candidates)

        n_windows = states.shape[0] - self.hold_samples + 1
        starts = jnp.arange(n_windows, dtype=jnp.int32)
        hold_windows = jax.vmap(
            lambda start: jax.lax.dynamic_slice(
                rho_stopped, (start,), (self.hold_samples,)
            )
        )(starts)
        rho_stop_hold = self._smooth_max(
            self._smooth_min(hold_windows, axis=1)
        )
        rho_stop = self._smooth_min(jnp.stack((rho_until_stop, rho_stop_hold)))
        rho_stop = jnp.where(traffic.stop_active > 0.5, rho_stop, 5.0)

        rho_yield = self._smooth_min(
            jnp.stack(
                (
                    signed_stop_distance + self.cross_margin,
                    self.stop_speed - speed,
                ),
                axis=1,
            ),
            axis=1,
        )
        rho_yield = self._smooth_min(rho_yield)
        rho_yield = jnp.where(traffic.must_yield > 0.5, rho_yield, 5.0)

        return self._smooth_min(
            jnp.stack(
                (
                    rho_lane,
                    rho_heading,
                    rho_speed,
                    rho_collision,
                    rho_goal,
                    rho_stop,
                    rho_yield,
                )
            )
        )


class STLTrafficPlanner(Node):
    def __init__(self):
        super().__init__("stl_svpio_node")

        default_config = (
            Path(get_package_share_directory("f1tenth_mppi"))
            / "config"
            / "stl_svpio.yaml"
        )

        pkg_share = get_package_share_directory('f1tenth_mppi')
        csv_path = os.path.join(pkg_share, 'config', 'gsts.csv')

        self.declare_parameter("config_path", str(default_config))
        self.declare_parameter("waypoint_path", str(csv_path))
        self.declare_parameter("self_object_id", 560)
        self.declare_parameter("other_object_id", 561)
        self.declare_parameter("self_team", "sdc6")
        self.declare_parameter("other_team", "sdc2")
        self.declare_parameter("enable_drive", True)

        config_path = self.get_parameter("config_path").value
        self.config = yaml.safe_load(Path(config_path).read_text())
        self.dt = float(self.config["dt"])
        self.horizon = int(self.config["n_steps"])
        self.self_id = int(self.get_parameter("self_object_id").value)
        self.other_id = int(self.get_parameter("other_object_id").value)
        self.self_team = str(self.get_parameter("self_team").value)
        self.other_team = str(self.get_parameter("other_team").value)
        self.enable_drive = bool(self.get_parameter("enable_drive").value)

        waypoint_path = self.get_parameter("waypoint_path").value
        self.waypoints = np.loadtxt(waypoint_path, delimiter=";", skiprows=3, dtype=np.float64)
        self.path_xy = self.waypoints[:, 1:3]
        next_xy = np.roll(self.path_xy, -1, axis=0)
        self.segment_vectors = next_xy - self.path_xy
        self.segment_lengths = np.linalg.norm(self.segment_vectors, axis=1)
        self.path_cumulative = np.concatenate(([0.0], np.cumsum(self.segment_lengths)))
        self.path_length = self.path_cumulative[-1]

        self.env = F1TenthSTLEnv(
            self.dt,
            self.horizon,
            self.config["control_scale"],
            self.config,
        )
        self.planner = STLSVPIO(
            horizon=self.horizon,
            control_dim=2,
            n_particles=self.config["n_particles"],
            n_iterations=self.config["n_iterations"],
            step_size=self.config["step_size"],
            temperature=self.config["temperature"],
        )
        self.rng = jax.random.PRNGKey(int(self.config["random_seed"]))

        self.drive_msg = AckermannDriveStamped()
        self.current_pose = None
        self.current_yaw = 0.0
        self.current_speed = 0.0
        self.other_pose = None
        self.other_yaw = 0.0
        self.other_velocity = np.zeros(2, dtype=np.float64)
        self.other_stopped = False
        self.other_stop_observed_time = None

        self.stop_line_active = False
        self.stop_completed = False
        self.intersection_committed = False
        self.stop_point = np.zeros(2, dtype=np.float64)
        self.stop_tangent = np.array([1.0, 0.0], dtype=np.float64)
        self.stationary_since = None
        self.arrival_time = None
        self.cooldown_until = 0.0

        self.drive_pub = self.create_publisher(AckermannDriveStamped, "/ackermann_cmd", 1)
        self.stop_status_pub = self.create_publisher(Bool, f"/{self.self_team}/stop_sign/we_stopped", 1)
        self.timing_pub = self.create_publisher(Float32MultiArray, "/stl_svpio/timing", 10)
        self.robustness_pub = self.create_publisher(Float32, "/stl_svpio/robustness", 10)
        self.ref_pub = self.create_publisher(Marker, "/stl_svpio/reference", 1)
        self.opt_pub = self.create_publisher(Marker, "/stl_svpio/optimal_trajectory", 1)

        self.create_subscription(
            PoseStamped,
            f"/optitrack/object_{self.self_id}/pose",
            self.pose_callback,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            Odometry,
            f"/optitrack/object_{self.self_id}/odom",
            self.odom_callback,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            PoseStamped,
            f"/optitrack/object_{self.other_id}/pose",
            self.other_pose_callback,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            Odometry,
            f"/optitrack/object_{self.other_id}/odom",
            self.other_odom_callback,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            Float32,
            f"/{self.self_team}/stop_sign/distance",
            self.stop_sign_callback,
            1,
        )
        self.create_subscription(
            Bool,
            f"/{self.other_team}/stop_sign/we_stopped",
            self.other_status_callback,
            1,
        )

    def _nearest_progress(self, point):
        segment_length_sq = np.sum(self.segment_vectors * self.segment_vectors, axis=1)
        relative = point[None, :] - self.path_xy
        t = np.sum(relative * self.segment_vectors, axis=1) / np.maximum(segment_length_sq, 1e-12)
        t = np.clip(t, 0.0, 1.0)
        projections = self.path_xy + t[:, None] * self.segment_vectors
        index = int(np.argmin(np.linalg.norm(projections - point[None, :], axis=1)))
        return self.path_cumulative[index] + t[index] * self.segment_lengths[index]

    def _path_state(self, progress):
        progress = progress % self.path_length
        index = int(np.searchsorted(self.path_cumulative, progress, side="right") - 1)
        index = min(index, len(self.path_xy) - 1)
        segment_length = max(self.segment_lengths[index], 1e-12)
        ratio = (progress - self.path_cumulative[index]) / segment_length
        point = self.path_xy[index] + ratio * self.segment_vectors[index]
        tangent = self.segment_vectors[index] / segment_length
        yaw = math.atan2(tangent[1], tangent[0])
        return point, tangent, yaw

    def _reference(self, state):
        current_progress = self._nearest_progress(state[:2])
        distances = np.arange(self.horizon + 1, dtype=np.float64) * self.config["cruise_speed"] * self.dt
        reference = np.zeros((self.horizon + 1, 4), dtype=np.float32)
        for i, distance in enumerate(distances):
            point, _, yaw = self._path_state(current_progress + distance)
            reference[i] = (point[0], point[1], yaw, self.config["cruise_speed"])
        return reference

    def _traffic_context(self):
        times = np.arange(self.horizon + 1, dtype=np.float32) * self.dt
        if self.other_pose is None:
            other_xy = np.zeros((self.horizon + 1, 2), dtype=np.float32)
            other_valid = 0.0
        else:
            other_xy = self.other_pose[None, :] + times[:, None] * self.other_velocity[None, :]
            other_xy = other_xy.astype(np.float32)
            other_valid = 1.0

        signed_distance = float("inf")
        if self.stop_line_active and self.current_pose is not None:
            signed_distance = float(
                np.dot(self.stop_point - self.current_pose, self.stop_tangent)
            )

        stop_active = (
            self.stop_line_active
            and not self.stop_completed
            and signed_distance <= self.config["stl_stop_activation_distance"]
        )
        must_yield = (
            self.stop_line_active
            and self.stop_completed
            and not self.intersection_committed
        )
        return TrafficContext(
            other_xy=jnp.asarray(other_xy),
            other_valid=jnp.asarray(other_valid, dtype=jnp.float32),
            stop_point=jnp.asarray(self.stop_point, dtype=jnp.float32),
            stop_tangent=jnp.asarray(self.stop_tangent, dtype=jnp.float32),
            stop_active=jnp.asarray(float(stop_active), dtype=jnp.float32),
            must_yield=jnp.asarray(float(must_yield), dtype=jnp.float32),
        )

    def _publish_stop_status(self, value):
        msg = Bool()
        msg.data = bool(value)
        self.stop_status_pub.publish(msg)

    def _has_priority(self):
        if not self.other_stopped or self.other_stop_observed_time is None:
            return True
        if self.arrival_time is None:
            return False
        if abs(self.arrival_time - self.other_stop_observed_time) < 0.05:
            return self.self_id < self.other_id
        return self.arrival_time < self.other_stop_observed_time

    def _update_stop_state(self, now):
        if not self.stop_line_active or self.current_pose is None:
            self._publish_stop_status(False)
            return

        signed_distance = float(np.dot(self.stop_point - self.current_pose, self.stop_tangent))
        if not self.stop_completed:
            in_stop_zone = abs(signed_distance) <= self.config["stop_zone"]
            nearly_stopped = self.current_speed <= self.config["stop_speed"]
            if in_stop_zone and nearly_stopped:
                if self.stationary_since is None:
                    self.stationary_since = now
                elif now - self.stationary_since >= self.config["stop_hold_time"]:
                    self.stop_completed = True
                    self.arrival_time = now
                    self._publish_stop_status(True)
            else:
                self.stationary_since = None
            return

        self._publish_stop_status(True)
        if not self.intersection_committed and self._has_priority():
            self.intersection_committed = True

        if self.intersection_committed and signed_distance < -self.config["intersection_release_distance"]:
            self.stop_line_active = False
            self.stop_completed = False
            self.intersection_committed = False
            self.stationary_since = None
            self.arrival_time = None
            self.cooldown_until = now + self.config["stop_cooldown"]
            self._publish_stop_status(False)

    def stop_sign_callback(self, msg):
        if self.current_pose is None or self.stop_line_active or time.time() < self.cooldown_until:
            return
        distance = float(msg.data)
        if distance <= 0.0 or distance > self.config["stop_detection_distance"]:
            return

        current_progress = self._nearest_progress(self.current_pose)
        stop_progress = current_progress + max(distance - self.config["target_stop_offset"], 0.0)
        self.stop_point, self.stop_tangent, _ = self._path_state(stop_progress)
        self.stop_line_active = True
        self.stop_completed = False
        self.intersection_committed = False
        self.stationary_since = None
        self.arrival_time = None

    def other_status_callback(self, msg):
        stopped = bool(msg.data)
        if stopped and not self.other_stopped:
            self.other_stop_observed_time = time.time()
        elif not stopped:
            self.other_stop_observed_time = None
        self.other_stopped = stopped

    def odom_callback(self, msg):
        vx = float(msg.twist.twist.linear.x)
        vy = float(msg.twist.twist.linear.y)
        self.current_speed = math.hypot(vx, vy)

    def other_odom_callback(self, msg):
        speed = math.hypot(
            float(msg.twist.twist.linear.x),
            float(msg.twist.twist.linear.y),
        )
        self.other_velocity = speed * np.array(
            [math.cos(self.other_yaw), math.sin(self.other_yaw)],
            dtype=np.float64,
        )

    def other_pose_callback(self, msg):
        self.other_pose = np.array(
            [msg.pose.position.x, msg.pose.position.y], dtype=np.float64
        )
        q = msg.pose.orientation
        self.other_yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z),
        )

    def pose_callback(self, msg):
        start_time = time.perf_counter()
        now = time.time()
        self.current_pose = np.array([msg.pose.position.x, msg.pose.position.y], dtype=np.float64)
        q = msg.pose.orientation
        self.current_yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z),
        )
        self._update_stop_state(now)

        state = np.array(
            [
                self.current_pose[0],
                self.current_pose[1],
                self.drive_msg.drive.steering_angle,
                self.current_speed,
                self.current_yaw,
            ],
            dtype=np.float32,
        )
        reference = self._reference(state)
        traffic = self._traffic_context()
        self.rng, solve_key = jax.random.split(self.rng)

        best_controls, best_states, robustness = self.planner.update(
            self.env,
            jnp.asarray(state),
            jnp.asarray(reference),
            traffic,
            solve_key,
        )

        normalized_control = np.asarray(jax.device_get(best_controls[0]))
        steer_rate, accel = normalized_control * np.asarray(self.env.control_scale)
        command_steer = self.drive_msg.drive.steering_angle + float(steer_rate) * self.dt
        command_speed = self.current_speed + float(accel) * self.dt
        command_steer = float(np.clip(command_steer, self.env.steer_min, self.env.steer_max))
        command_speed = float(np.clip(command_speed, 0.0, self.config["speed_limit"]))

        if self.stop_line_active and self.current_pose is not None:
            signed_distance = float(np.dot(self.stop_point - self.current_pose, self.stop_tangent))
            waiting = (not self.stop_completed) or (
                self.stop_completed and not self.intersection_committed
            )
            if waiting and signed_distance <= self.config["emergency_stop_margin"]:
                command_speed = 0.0

        if self.other_pose is not None:
            current_separation = float(np.linalg.norm(self.current_pose - self.other_pose))
            if current_separation <= self.config["emergency_collision_distance"]:
                command_speed = 0.0

        self.drive_msg.drive.steering_angle = command_steer
        self.drive_msg.drive.speed = command_speed
        if self.enable_drive:
            self.drive_pub.publish(self.drive_msg)

        elapsed = time.perf_counter() - start_time
        timing_msg = Float32MultiArray()
        timing_msg.data = [elapsed, 1.0 / elapsed if elapsed > 0.0 else 0.0]
        self.timing_pub.publish(timing_msg)
        robustness_msg = Float32()
        robustness_msg.data = float(jax.device_get(robustness))
        self.robustness_pub.publish(robustness_msg)
        self._publish_trajectory(self.ref_pub, reference[:, :2], 0.0, 0.0, 1.0)
        self._publish_trajectory(
            self.opt_pub,
            np.asarray(jax.device_get(best_states[:, :2])),
            1.0,
            0.0,
            1.0,
        )

    def _publish_trajectory(self, publisher, points, red, green, blue):
        marker = Marker(type=Marker.LINE_STRIP, scale=Vector3(x=0.05, y=0.05, z=0.05))
        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.pose.orientation.w = 1.0
        marker.color.r = red
        marker.color.g = green
        marker.color.b = blue
        marker.color.a = 1.0
        marker.points = [Point(x=float(x), y=float(y), z=0.0) for x, y in points]
        publisher.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = STLTrafficPlanner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()