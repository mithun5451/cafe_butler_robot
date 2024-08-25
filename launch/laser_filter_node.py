import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class LaserFilterNode(Node):
    def __init__(self):
        super().__init__('laser_filter_node')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',  # Update this if your scan topic is different
            self.laser_callback,
            10)
        self.publisher = self.create_publisher(LaserScan, '/filtered_scan', 10)

    def laser_callback(self, msg):
        # Filter the scan data to only include angles from -45 to 45 degrees
        min_angle = -0.785398  # -45 degrees in radians
        max_angle = 0.785398   # 45 degrees in radians
        angle_increment = msg.angle_increment

        start_index = int((min_angle - msg.angle_min) / angle_increment)
        end_index = int((max_angle - msg.angle_min) / angle_increment)

        filtered_ranges = msg.ranges[start_index:end_index]

        filtered_scan = LaserScan()
        filtered_scan.header = msg.header
        filtered_scan.angle_min = min_angle
        filtered_scan.angle_max = max_angle
        filtered_scan.angle_increment = angle_increment
        filtered_scan.time_increment = msg.time_increment
        filtered_scan.scan_time = msg.scan_time
        filtered_scan.range_min = msg.range_min
        filtered_scan.range_max = msg.range_max
        filtered_scan.ranges = filtered_ranges

        self.publisher.publish(filtered_scan)

def main(args=None):
    rclpy.init(args=args)
    node = LaserFilterNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
