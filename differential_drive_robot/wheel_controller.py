import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import Twist


class DifferentialDriveController(Node):

    def __init__(self):
        super().__init__('differential_drive_controller')

        # Publishers
        self.joint_publisher = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        self.cmd_subscriber = self.create_subscription(
            Twist,
            '/cmd_vel_safe',
            self.cmd_vel_callback,
            10
        )

        self.odom_publisher = self.create_publisher(
            Odometry,
            '/odom',
            10
        )
        self.gazebo_cmd_publisher = self.create_publisher(
            Twist,
            '/cmd_vel_gazebo',
            10
        )

        # TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        # Timer
        self.timer = self.create_timer(
            0.1,
            self.update
        )

        # Robot parameters
        self.declare_parameter('wheel_radius', 0.075)
        self.declare_parameter('wheel_separation', 0.4)
        self.declare_parameter('cmd_timeout', 0.5)

        self.wheel_radius = self.get_parameter(
            'wheel_radius'
        ).value

        self.wheel_separation = self.get_parameter(
            'wheel_separation'
        ).value

        self.cmd_timeout = self.get_parameter(
            'cmd_timeout'
        ).value


        # Desired robot velocity
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0

        self.last_cmd_time = self.get_clock().now()
        
        # Wheel positions
        self.left_angle = 0.0
        self.right_angle = 0.0

        # Robot pose
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        # Timing
        self.last_time = self.get_clock().now()

    def cmd_vel_callback(self, msg):

        self.linear_velocity = msg.linear.x
        self.angular_velocity = msg.angular.z
        self.last_cmd_time = self.get_clock().now()

    def update(self):

        current_time = self.get_clock().now()

        time_since_cmd = (
            current_time - self.last_cmd_time
        ).nanoseconds / 1e9

        if time_since_cmd > self.cmd_timeout:

            self.linear_velocity = 0.0
            self.angular_velocity = 0.0
        gazebo_cmd = Twist()

        gazebo_cmd.linear.x = self.linear_velocity
        gazebo_cmd.angular.z = self.angular_velocity

        self.gazebo_cmd_publisher.publish(gazebo_cmd)

        
        
        dt = (
            current_time - self.last_time
        ).nanoseconds / 1e9

        self.last_time = current_time

        # --------------------------------
        # Differential-drive inverse kinematics
        # --------------------------------

        left_velocity = (
            self.linear_velocity
            - (self.angular_velocity * self.wheel_separation / 2.0)
        ) / self.wheel_radius

        right_velocity = (
            self.linear_velocity
            + (self.angular_velocity * self.wheel_separation / 2.0)
        ) / self.wheel_radius

        # --------------------------------
        # Wheel angle integration
        # --------------------------------

        self.left_angle += left_velocity * dt
        self.right_angle += right_velocity * dt

        # --------------------------------
        # Convert wheel angular velocity
        # to linear velocity
        # --------------------------------

        v_left = left_velocity * self.wheel_radius
        v_right = right_velocity * self.wheel_radius

        # --------------------------------
        # Robot velocity
        # --------------------------------

        v = (v_right + v_left) / 2.0

        omega = (
            (v_right - v_left)
            / self.wheel_separation
        )

        # --------------------------------
        # Odometry integration
        # --------------------------------

        self.x += v * math.cos(self.theta) * dt
        self.y += v * math.sin(self.theta) * dt
        self.theta += omega * dt

        # --------------------------------
        # Publish JointState
        # --------------------------------

        joint_msg = JointState()

        joint_msg.header.stamp = current_time.to_msg()

        joint_msg.name = [
            'left_wheel_joint',
            'right_wheel_joint'
        ]

        joint_msg.position = [
            self.left_angle,
            self.right_angle
        ]

        joint_msg.velocity = [
            left_velocity,
            right_velocity
        ]

        self.joint_publisher.publish(joint_msg)

        # --------------------------------
        # Publish Odometry
        # --------------------------------

        odom_msg = Odometry()

        odom_msg.header.stamp = current_time.to_msg()
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_link'

        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        odom_msg.pose.pose.position.z = 0.0

        odom_msg.pose.pose.orientation.z = math.sin(
            self.theta / 2.0
        )

        odom_msg.pose.pose.orientation.w = math.cos(
            self.theta / 2.0
        )

        odom_msg.twist.twist.linear.x = v
        odom_msg.twist.twist.angular.z = omega

        self.odom_publisher.publish(odom_msg)

        # --------------------------------
        # Publish odom → base_link TF
        # --------------------------------

        transform = TransformStamped()

        transform.header.stamp = current_time.to_msg()
        transform.header.frame_id = 'odom'
        transform.child_frame_id = 'base_link'

        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.translation.z = 0.0

        transform.transform.rotation.z = math.sin(
            self.theta / 2.0
        )

        transform.transform.rotation.w = math.cos(
            self.theta / 2.0
        )

        self.tf_broadcaster.sendTransform(transform)


def main(args=None):

    rclpy.init(args=args)

    node = DifferentialDriveController()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()