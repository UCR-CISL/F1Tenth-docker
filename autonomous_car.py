import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from ackermann_msgs.msg import AckermannDriveStamped
import math  # Needed for filtering out invalid LiDAR data

class AutonomousCar(Node):
    def __init__(self):
        """
        Initialize the AutonomousCar node.
        """
        super().__init__('autonomous_car')
        self.get_logger().info("AutonomousCar node started!") # output to the log

        # Parameters
        #self.min_speed_rpm = 3000.0  # Minimum angular speed in RPM
        #self.max_speed_rpm = 10000.0  # Maximum angular speed in RPM
        #self.min_speed_rads = (self.min_speed_rpm * 2 * 3.14159) / 60  # Convert to rad/s
        #self.max_speed_rads = (self.max_speed_rpm * 2 * 3.14159) / 60  # Convert to rad/s
        self.min_speed = 0.1  # Minimum speed in m/s
        self.max_speed = 6.0  # Maximum speed in m/s
        self.min_safe_distance = 1.0  # Minimum safe distance in meters to start slowing
        self.stop_distance = 0.5 #Distance to stop completely by
        self.front_fov = 30  # Field of view in degrees
        self.front_fov_rad = (self.front_fov / 2) * (3.14159 / 180)  # Convert to radians

        #Speed Smoothing Parameters
        self.last_speed = 0.0
        self.last_cmd_time = self.get_clock().now()
        self.max_accel = 2.0
        self.max_decel = 4.0

        # Subscriber to LiDAR data
        self.lidar_sub = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, 10)

        # Publisher to control the car's speed (angular velocity)
        self.drive_pub = self.create_publisher(AckermannDriveStamped, '/drive', 10)

    def lidar_callback(self, data):
        """
        Callback function to process LiDAR data and control the car's speed.
        """
        # Avoid division by zero error
        if data.angle_increment == 0:
            return

        # Extract LiDAR ranges
        ranges = data.ranges
        num_beams = len(ranges)

        # Calculate the indices for the front field of view
        middle_index = num_beams // 2
        start_index = max(0, middle_index - int(self.front_fov_rad / data.angle_increment))
        end_index = min(num_beams, middle_index + int(self.front_fov_rad / data.angle_increment))

        # Extract the front field of view data
        front_ranges = ranges[start_index:end_index]

        # Remove invalid LiDAR readings (NaN, Inf)
        front_ranges = [r for r in front_ranges if not math.isinf(r) and not math.isnan(r)]

        # Ensure we have valid measurements before calling min()
        if len(front_ranges) == 0:
            min_distance = float('inf')  # Default to a very large value
        else:
            min_distance = min(front_ranges)

        target_speed = 0.0

        # Compute speed based on distance
        if min_distance <= self.stop_distance:
            target_speed = 0.0
            self.get_logger().info("Object detected at less than 0.5m Stopping")
            #speed = self.max_speed * (min_distance / (self.min_safe_distance + 0.1))  # Smooth braking
            #speed = max(speed, self.min_speed)  # Prevent stopping completely
        elif min_distance < self.min_safe_distance:
            distance_range = self.min_safe_distance - self.stop_distance
            distance_ratio = (min_distance - self.stop_distance) / distance_range
            target_speed = self.max_speed * distance_ratio
            target_speed = max(target_speed, self.min_speed)  # Ensure minimum speed
            self.get_logger().info(f"Object at {min_distance:.2f}m - Slowing to {target_speed:.2f} m/s")
        else:
            #no close obstacle target max speed
            target_speed = self.max_speed
            self.get_logger().info(f"Clear path - {min_distance:.2f}m - Target speed {target_speed:.2f} m/s")

        ramped_speed = self.apply_speed_ramping(target_speed)

        # Publish speed command
        self.control_speed(ramped_speed)

    def apply_speed_ramping(self, target_speed):
        """
        Apply Speed ramping to avoid jerking when trying to speed up
        """
        #calculate time since last command
        current_time = self.get_clock().now()
        dt = (current_time - self.last_cmd_time).nanoseconds / 1e9  # Convert to seconds
        self.last_cmd_time = current_time

        if dt > 0.5 or dt <= 0:
            dt = 0.1

        max_speed_increase = self.max_accel * dt
        max_speed_decrease = self.max_decel * dt

        if target_speed > self.last_speed:
            new_speed = min(target_speed, self.last_speed + max_speed_increase)
        else:
            new_speed = max(target_speed, self.last_speed - max_speed_decrease)

        self.last_speed = new_speed

        return new_speed
        
    
    def control_speed(self, linear_speed):
        """
        Publish speed (angular velocity) AckermannDriveStamped to control the car.
        """
        
        drive_msg = AckermannDriveStamped()
        # Set header
        drive_msg.header.stamp = self.get_clock().now().to_msg()
        drive_msg.header.frame_id = "base_link"
        
        # Use angular velocity as the speed value
        # NOTE: This is non-standard but might be how your F1Tenth is configured
        if linear_speed > 6:
            linear_speed = 6
        elif linear_speed < 0:
            linear_speed = 0
        
        drive_msg.drive.speed = float(linear_speed)  # Angular speed in rad/s
        drive_msg.drive.steering_angle = 0.0  # No steering, go straight
        
        # Publish the command
        self.drive_pub.publish(drive_msg)
        self.get_logger().info(f"Setting Linear speed: {linear_speed:.2f} m/s")

def main(args=None):
    """
    Main function to initialize and run the AutonomousCar node.
    """
    rclpy.init(args=args)
    autonomous_car = AutonomousCar()
    
    try:
        rclpy.spin(autonomous_car)
    except KeyboardInterrupt:
        autonomous_car.get_logger().info("Shutting down...")

    # Ensure the car stops before shutting down
    autonomous_car.control_speed(0.0)
    autonomous_car.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()