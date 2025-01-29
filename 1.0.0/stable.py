#!/usr/bin/env micropython

# Import necessary libraries
import time
import math
from ev3dev2.motor import *
from ev3dev2.sound import Sound
from ev3dev2.button import Button
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *
from ev3dev2.motor import LargeMotor, MoveSteering, OUTPUT_A, OUTPUT_D

color_sensor_in1 = ColorSensor(INPUT_1)
color_sensor_in4 = ColorSensor(INPUT_4)
motor_left = LargeMotor(OUTPUT_A)
motor_right = LargeMotor(OUTPUT_D)
tank_drive = MoveTank(OUTPUT_D, OUTPUT_A)
steer_drive = MoveSteering(OUTPUT_D, OUTPUT_A)

# ------------------------------------------------------------------------------------------
#                               CONTROL PANEL VARIABLES

K = 20  # UNIVERSAL SPEED SETTING
black_black_wait_time = 0.6  # WAIT TIME FOR BLACK-BLACK SCENARIO
speed_reduction = 17  # SPEED REDUCTION FOR BLACK-BLACK CASE
speed_drop = 4
# If lastTurnLeft == False --> RIGHT
# If lastTurnLeft == True --> LEFT

K = K * (-1)
print("LINE FOLLOWER")

# Start of the main loop
lastTurnLeft = True
while True:
	# print("Right: ", color_sensor_in4.reflected_light_intensity)
	# print("Left: ", color_sensor_in1.reflected_light_intensity)

	is_black_right = not (color_sensor_in4.reflected_light_intensity > 28)
	is_black_left = not (color_sensor_in1.reflected_light_intensity > 20)
	velocity_right = ((color_sensor_in4.reflected_light_intensity / 42) + 1) * K - 20
	velocity_left = ((color_sensor_in1.reflected_light_intensity / 42) + 1) * K - 20
	is_gray_left = 20 <= color_sensor_in1.reflected_light_intensity <= 30
	is_gray_right = 20 <= color_sensor_in4.reflected_light_intensity <= 30

	if not is_black_right and not is_black_left and not is_gray_right and not is_gray_left:
		print("Moving forward")
		tank_drive.on(K, K)
	elif not is_black_right and is_gray_right:
		print("Gray towards right")
		tank_drive.on(0, velocity_right)
		lastTurnLeft = False
	elif is_black_right and not is_black_left:
		print("Sharp right turn")
		tank_drive.on(-K + 10, K - 20)
		lastTurnLeft = False
		print(lastTurnLeft)
	elif not is_black_right and is_black_left:
		print("Sharp left turn")
		tank_drive.on(K - 20, -K + 10)
		lastTurnLeft = True
	elif not is_black_right and is_gray_left:
		print("Gray towards left")
		tank_drive.on(velocity_left, 0)
		lastTurnLeft = True

	if is_black_right and is_black_left:
		if lastTurnLeft:
			tank_drive.on_for_seconds(K - speed_drop, K - speed_drop, black_black_wait_time)
			start = time.time()

			print("Black-Black to Left")
			while (color_sensor_in1.reflected_light_intensity > 10) and (time.time() - start < 1.7):
				tank_drive.on(-(K - speed_reduction), +(K - speed_reduction))
				lastTurnLeft = True
			while (color_sensor_in4.reflected_light_intensity > 10):
				tank_drive.on(+(K - speed_reduction), -(K - speed_reduction))
				lastTurnLeft = False
		else:
			start = time.time()
			print("Black-Black to Right")
			tank_drive.on_for_seconds(K - speed_drop, K - speed_drop, black_black_wait_time)

			while (color_sensor_in1.reflected_light_intensity > 10) and (time.time() - start < 1.7):
				tank_drive.on(-(K - speed_reduction), +(K - speed_reduction))
				lastTurnLeft = True
			while (color_sensor_in4.reflected_light_intensity > 10):
				tank_drive.on(+(K - speed_reduction), -(K - speed_reduction))
				lastTurnLeft = False
