import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class ObstacleAvoidance(Node):

    def __init__(self):
        super().__init__('obstacle_avoidance')

        self.safe_distance = 0.5
        self.turn_speed = 0.5

        self.latest_scan = None
        self.latest_cmd = Twist()

        # Robot starts in forward state
        self.state = 'FORWARD'
        self.turn_direction = 1.0

        self.cmd_subscriber = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10
        )

        self.scan_subscriber = self.create_subscription(
            LaserScan,
            '/scan_corrected',
            self.scan_callback,
            10
        )

        self.cmd_publisher = self.create_publisher(
            Twist,
            '/cmd_vel_safe',
            10
        )

        # Run the decision loop at 10 Hz
        self.timer = self.create_timer(
            0.1,
            self.control_loop
        )

    def scan_callback(self, msg):
        self.latest_scan = msg

    def cmd_callback(self, msg):
        # Remember the latest command from teleoperation
        self.latest_cmd = msg

    def get_min_distance(self, min_angle, max_angle):

        min_distance = float('inf')

        for i, distance in enumerate(self.latest_scan.ranges):

            angle = (
                self.latest_scan.angle_min
                + i * self.latest_scan.angle_increment
            )

            if min_angle <= angle <= max_angle:

                if math.isfinite(distance):
                    min_distance = min(
                        min_distance,
                        distance
                    )

        return min_distance

    def control_loop(self):

        safe_cmd = Twist()

        # No LiDAR data → stop
        if self.latest_scan is None:
            self.cmd_publisher.publish(safe_cmd)
            return

        # Measure front, left and right
        front_distance = self.get_min_distance(
            -math.radians(30),
            math.radians(30)
        )

        left_distance = self.get_min_distance(
            math.radians(30),
            math.radians(90)
        )

        right_distance = self.get_min_distance(
            -math.radians(90),
            -math.radians(30)
        )

        # --------------------------------
        # STATE 1: FORWARD
        # --------------------------------

        if self.state == 'FORWARD':

            if front_distance < self.safe_distance:

                # Obstacle found
                safe_cmd.linear.x = 0.0

                # Choose the more open side
                if left_distance > right_distance:
                    self.turn_direction = 1.0
                    self.get_logger().warn(
                        'Obstacle detected → turning LEFT'
                    )
                else:
                    self.turn_direction = -1.0
                    self.get_logger().warn(
                        'Obstacle detected → turning RIGHT'
                    )

                self.state = 'TURNING'

            else:

                # No obstacle → follow teleop
                safe_cmd.linear.x = self.latest_cmd.linear.x
                safe_cmd.angular.z = self.latest_cmd.angular.z

        # --------------------------------
        # STATE 2: TURNING
        # --------------------------------

        elif self.state == 'TURNING':

            # Keep rotating
            safe_cmd.linear.x = 0.0
            safe_cmd.angular.z = (
                self.turn_speed * self.turn_direction
            )

            # When front becomes clear → go forward
            if front_distance >= self.safe_distance:

                self.state = 'FORWARD'

                self.get_logger().info(
                    'Path clear → moving forward'
                )

                safe_cmd.linear.x = self.latest_cmd.linear.x
                safe_cmd.angular.z = 0.0

        self.cmd_publisher.publish(safe_cmd)


def main(args=None):

    rclpy.init(args=args)

    node = ObstacleAvoidance()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()