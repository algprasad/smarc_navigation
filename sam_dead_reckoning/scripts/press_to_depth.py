#!/usr/bin/python

import rospy
import numpy as np
import tf
from sensor_msgs.msg import FluidPressure
from geometry_msgs.msg import PoseWithCovarianceStamped

class Press2Depth(object):

	def __init__(self):
		self.odom_frame = rospy.get_param(rospy.get_name() + '/odom_frame', '/odom')
		self.press_topic = rospy.get_param(rospy.get_name() + '/pressure_topic', '/pressure')
		self.depth_topic = rospy.get_param(rospy.get_name() + '/depth_topic', '/depth')

		self.subs = rospy.Subscriber(self.press_topic, FluidPressure, self.depthCB)
		self.pub = rospy.Publisher(self.depth_topic, PoseWithCovarianceStamped)

		self.depth_msg = PoseWithCovarianceStamped()
		self.depth_msg.header.frame_id = self.odom_frame
		self.depth_msg.pose.covariance = [1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01]
		self.depth_msg.pose.pose.orientation.w = 1.
		
		self.listener_odom = tf.TransformListener()
		self.listener_press = tf.TransformListener()

		# try:
			# (trans,quaternion) = listener_press.lookupTransform('sam_auv/depth_link', 'sam_auv/base_link', rospy.Time(10))
			# self.x_base_depth = abs(trans[0])
		self.x_base_depth = 477.0

		# except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
			# continue

		rospy.spin()


	def depthCB(self, press_msg):

		try:
            (trans,quaternion) = listener_odom.lookupTransform('sam_auv/base_link', self.odom_frame, rospy.Time(0))
            euler = tf.transformations.euler_from_quaternion(quaternion)
			pitch = euler[1]

			# depth_abs is positive, must be manually negated
			depth_abs = - self.pascal_pressure_to_depth(press_msg.fluid_pressure)
			# Check signs here
			depth_base_link = depth_abs + self.x_base_depth * np.sin(pitch)

			self.depth_msg.header.stamp = rospy.Time.now()
			self.depth_msg.pose.pose.position.z = -  # = [0., 0., 2.]
			self.pub.publish(self.depth_msg)

        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            continue



	def pascal_pressure_to_depth(self, pressure):

		return 10.*((pressure / 100000.) - 1.) # 117000 -> 1.7



if __name__ == "__main__":

	rospy.init_node('press_to_depth')
	try:
		pi = Press2Depth()
	except rospy.ROSInterruptException:
		pass