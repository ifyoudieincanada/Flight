import random
import launchpad
from pygame import time
import time
import struct
import json

# provides arm_and_takeoff(), send_nav_velocity(), and condition_yaw()
import droneInteraction


def handleButton(but, current):
	scale = 128
	if (but[1] > 0 && but[0] < 8):
		current[0] = (but[0] - 4)*scale/4
		current[1] = (but[1] - 4)*scale/4
	elif (but[0] < 2 && but[1] == 0):
		current[2] = -(but[0]*2-1)*scale/4
	elif (but == (4, 0, True)):
		current = stabilizeParrot()

	send_nav_velocity(current[0], current[1], current[2])
	return current

def stabilizeParrot():
	send_nav_velocity(0, 0, 0)
	return [0, 0, 0]

def stabilizePrev(but, current):
	if (but[1] == 0):
		send_nav_velocity(current[0], current[1], 0)
		return [current[0], current[1], 0]
	else:
		send_nav_velocity(0, 0, current[2])
		return [0, 0, current[2]]

def main():

	LP = launchpad.Launchpad()  # creates a Launchpad instance (first Launchpad found)
	LP.Open()                   # start it

	f = open(r'\\.\pipe\wrist', 'r+b', 0) # opens FIFO for reading

	#LP.LedCtrlString( 'g', 0, 3, -1 )
	#LP.LedCtrlString( 'g', 3, 0, 1 )

	#controller, sequencer, stable
	mode = "controller"

	current = [0, 0, 0]

	prevBut = LP.ButtonStateXY()

	print "Checking for presses. 'arm' to end."
	while True:
		time.wait( 10 )

		# Read from the fifo
		n = struct.unpack('I', f.read(4))[0]    # Read str length
		j = json.loads(f.read(n))               # Read str as JSON
		f.seek(0)                               # Important!!!

		but = LP.ButtonStateXY()
		if but != []:

			if mode == "controller":
				#big controller :^)
				LP.LedCtrlXY( but[0], but[1], 0, 3 )
				print( but )
				if but[2]:
					if but != prevBut:
						current = handleButton(but, current)
					else:
						if ((but[0] < 8 and but[1] > 0) or (but[0] < 2 and but[1] == 0)):
							current = stabilizePrev(but, current)
					prevBut = but
				if but[2] == False:
					LP.LedCtrlXY( but[0], but[1], 0, 0 )

				LP.LedCtrlXY(5, 0, 3, 0)
			if mode == "sequencer":
				#record, sequence

				LP.LedCtrlXY(6, 0, 3, 0)
			if mode == "stable":
				#stabilize

				LP.LedCtrlXY(4, 0, 3, 0)


			if but == [5,0,True]:
				LP.LedCtrlXY(4, 0, 0, 0)
				LP.LedCtrlXY(6, 0, 0, 0)
				mode = "controller"
			if but == [6,0,True]:
				LP.LedCtrlXY(4, 0, 0, 0)
				LP.LedCtrlXY(5, 0, 0, 0)
				mode = "sequencer"
			if but == [4,0,True]:
				LP.LedCtrlXY(5, 0, 0, 0)
				LP.LedCtrlXY(6, 0, 0, 0)
				mode = "stable"
			if but == [ 8, 8, True ]:
				break



	LP.Reset() # turn all LEDs off
	LP.Close() # close the Launchpad


if __name__ == '__main__':
	main()
