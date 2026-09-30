import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class ScanFrameCorrector(Node):

    def __init__(self):
        super().__init__('scan_frame_corrector')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.publisher = self.create_publisher(
            LaserScan,
            '/scan_corrected',
            10
        )

    def scan_callback(self, msg):
        corrected_msg = msg
        corrected_msg.header.frame_id = 'lidar_link'

        self.publisher.publish(corrected_msg)


def main(args=None):
    rclpy.init(args=args)

    node = ScanFrameCorrector()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
