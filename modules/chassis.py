import time


# EXPLANATIONS OF VALUES USED IN .move()
# x=0.5: distance along the x-axis, 0.5m
# z=90: 90 degrees rotation
# xy_speed=0.5: 0.5m/second or 0.5degrees/second
#       :param x: float: [-5,5]，x轴向运动距离，单位 m
#       :param y: float: [-5,5]，y轴向运动距离，单位 m
#       :param z: float: [-1800,1800]，z轴向旋转角度，单位 °
#       :param xy_speed: float: [0.5,2]，xy轴向运动速度，单位 m/s
#       :param z_speed: float: [10,540]，z轴向旋转速度，单位 °/s

def chassis_test(robot):
    chassis = robot.chassis

    # set speed
    chassis.drive_speed(x=0, y=0, z=0)
    chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

    # forwards
    chassis.move(x=0, y=0, z=360, z_speed=540).wait_for_completed()
    chassis.stop()

    # # backwards
    # chassis.move(x=-0.5, y=0, z=0, xy_speed=0.5).wait_for_completed()
    #
    # # sideways to the right
    # chassis.move(x=0, y=0.5, z=0, xy_speed=0.5).wait_for_completed()
    #
    # # sideways to the left
    # chassis.move(x=0, y=-0.5, z=0, xy_speed=0.5).wait_for_completed()
    #
    # # rotate clockwise
    # chassis.move(x=0, y=0, z=90, xy_speed=0.5).wait_for_completed()
    #
    # # rotate counterclockwise
    # chassis.move(x=0, y=0, z=-90, xy_speed=0.5).wait_for_completed()
    #
    # # diagonally forward-right
    # chassis.move(x=0.5, y=0.5, z=0, xy_speed=0.5).wait_for_completed()
    #
    # # diagonally forward-left
    # chassis.move(x=0.5, y=-0.5, z=0, xy_speed=0.5).wait_for_completed()
    #


    robot.close()
