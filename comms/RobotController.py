from CommsThread import CommsThread

class RobotController(CommsThread):

	def __init__(self):
		self.grabbed = True

	def move(self, angle_to_face, angle_to_move, distance_to_target, grab_target):
		""" Overriding move function
			
		angle_to_move: Absolute magnetic angle towards which to move
		angle_to_face: Absolute magnetic angle towards which to face (while moving) 
		distance_to_target: Distance to target which we're moving towards
		grab_target: whether we want to grab the target(e.g. the ball)
		"""
		current_heading = self.get_mag_heading()

		if abs(angle_to_face - current_heading) > 90:
			self.rot_move(angle_to_face, 0)

		if distance_to_target < 40 and grab_target and self.grabbed:
			self.ungrab(True)
			self.grabbed = False

		if distance_to_target < 20 and abs(angle_to_face - current_heading) < 10 and not self.grabbed and grab_target:
			self.grab(True)
			self.grabbed = True

		if distance_to_target < 5 and abs(angle_to_face - current_heading) < 5:
			self.stop_robot()
		else:
			self.holo(angle_to_move, angle_to_face)


if __name__ == "__main__":
	r = RobotController()
	r.move(100, 100, 50, 1)