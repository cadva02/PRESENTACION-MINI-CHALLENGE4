import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import cv2 as cv
from cv_bridge import CvBridge
import numpy as np

class ColorDetectionNode(Node):
    def __init__(self):
        super().__init__('color_detection_node')
        self.wait_for_ros_time()

        # --- Conversión ROS↔OpenCV
        self.bridge = CvBridge()
        self.img = None

        # --- Rangos HSV para rojo (2 rangos), verde y amarillo
        self.red_lower1   = np.array([  0, 100, 100], np.uint8)
        self.red_upper1   = np.array([ 10, 255, 255], np.uint8)
        self.red_lower2   = np.array([160, 100, 100], np.uint8)
        self.red_upper2   = np.array([179, 255, 255], np.uint8)

        self.green_lower = np.array([45, 80, 120], np.uint8)
        self.green_upper = np.array([75, 250, 255], np.uint8)

        self.yellow_lower = np.array([25, 15, 140], np.uint8)
        self.yellow_upper = np.array([45, 250, 255], np.uint8)
        
 
        # --- Subscripción a cámara cruda (tema: '/video_source/raw')
        self.subscription = self.create_subscription(
            Image, '/video_source/raw', self.camera_callback, 10
        )

        # --- Publicador de imágenes procesadas (tema: '/image_processing/image')
        self.image_pub = self.create_publisher(
            Image, '/image_processing/image', 10
        )

        # --- Publicador de comandos de velocidad (tema: '/cmd_vel')
        self.cmd_pub = self.create_publisher(
            Twist, '/cmd_vel', 10
        )

        # --- Parámetros de velocidad y tiempo
        self.max_velocity  = 0.7       # [m/s]
        self.v_half        = self.max_velocity / 2.0
        self.v_eighth      = self.max_velocity / 8.0
        self.ramp_duration = 2.0       # [s] aceleración/desaceleración

        # --- Máquina de estados basada en tiempo
        self.state            = 'stopped'  # 'stopped', 'accelerating', 'cruising', 'decelerating', 'waiting'
        self.last_color       = None
        self.state_start_time = self.get_clock().now()

        # --- Timer de 10 Hz para control y detección
        self.create_timer(0.1, self.control_loop)
        self.get_logger().info('Color Detection Node up and running!')

    def wait_for_ros_time(self):
        self.get_logger().info('Waiting for ROS time...')
        while rclpy.ok():
            if self.get_clock().now().nanoseconds > 0:
                self.get_logger().info('ROS time active!')
                return
            rclpy.spin_once(self, timeout_sec=0.1)

    def camera_callback(self, msg: Image):
        try:
            self.img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'Image conversion failed: {e}')

    def control_loop(self):
        if self.img is None:
            return

        # --- Procesamiento de imagen ---
        blurred = cv.GaussianBlur(self.img, (9, 9), 2)
        hsv     = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)
        r1 = cv.inRange(hsv, self.red_lower1, self.red_upper1)
        r2 = cv.inRange(hsv, self.red_lower2, self.red_upper2)
        red    = cv.bitwise_or(r1, r2)
        green  = cv.inRange(hsv, self.green_lower, self.green_upper)
        yellow = cv.inRange(hsv, self.yellow_lower, self.yellow_upper)
        kernel = np.ones((3,3), np.uint8)
        red    = cv.dilate(cv.erode(red,    kernel, iterations=8), kernel, iterations=8)
        green  = cv.dilate(cv.erode(green,  kernel, iterations=8), kernel, iterations=8)
        yellow = cv.dilate(cv.erode(yellow, kernel, iterations=8), kernel, iterations=8)

        # Publicar imágenes binarias
        self.image_pub.publish(self.bridge.cv2_to_imgmsg(red,    encoding='mono8'))
        self.image_pub.publish(self.bridge.cv2_to_imgmsg(green,  encoding='mono8'))
        self.image_pub.publish(self.bridge.cv2_to_imgmsg(yellow, encoding='mono8'))

        # --- Detección de color con prioridad ---
        if   np.count_nonzero(red)    > 0: color = 'red'
        elif np.count_nonzero(yellow) > 0: color = 'yellow'
        elif np.count_nonzero(green)  > 0: color = 'green'
        else:                              color = None

        now = self.get_clock().now()

        # --- Cambio de estado solo si cambia el color ---
        if color != self.last_color:
            self.last_color       = color
            self.state_start_time = now

            if color == 'red':
                self.state = 'stopped'
            elif color == 'green':
                self.state = 'accelerating'
            elif color == 'yellow':
                self.state = 'decelerating'

        # --- Cálculo de tiempo en estado actual ---
        elapsed = (now - self.state_start_time).nanoseconds * 1e-9

        # --- Máquina de estados temporal para rampa ---
        if self.state == 'stopped':
            vel = 0.0

        elif self.state == 'accelerating':
            vel = min(self.v_half, elapsed / self.ramp_duration * self.v_half)
            if elapsed >= self.ramp_duration:
                self.state = 'cruising'
                self.state_start_time = now

        elif self.state == 'cruising':
            vel = self.v_half

        elif self.state == 'decelerating':
            vel = max(self.v_eighth,
                      self.v_half + (elapsed / self.ramp_duration) * (self.v_eighth - self.v_half))
            if elapsed >= self.ramp_duration:
                self.state = 'waiting'
                self.state_start_time = now

        elif self.state == 'waiting':
            vel = self.v_eighth

        else:
            vel = 0.0

        # --- Publicar comando de velocidad en '/cmd_vel' ---
        twist = Twist()
        twist.linear.x  = float(vel)
        twist.angular.z = 0.0
        self.cmd_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = ColorDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()