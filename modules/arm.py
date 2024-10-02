from robomaster import robotic_arm

""" 机械臂绝对位置移动 absolute position of robotic arm

        :param x: float, x-axis, forwards (positive), mm
        :param y: float, y-axis, upwards (positive), mm
        """


def moveabout(robot):
    arm = robot.robotic_arm
    arm.moveto(x=180, y=0).wait_for_completed()

def high(robot):
    arm = robot.robotic_arm
    arm.moveto(x=0, y=180).wait_for_completed()

def lowtograb(robot):
    arm = robot.robotic_arm
    arm.moveto(x=180, y=-50).wait_for_completed()
