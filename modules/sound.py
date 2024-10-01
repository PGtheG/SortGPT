from robomaster import robot as sound

def test_sound(robot):
    robot.play_sound(sound.SOUND_ID_1F).wait_for_completed()
