import random
import launchpad
from pygame import time
import time
import struct
import json

# provides arm_and_takeoff(), send_nav_velocity(), and condition_yaw()
import droneInteraction


def handleButton(but, currentV, currentY):
	scale = 2 #what scale is this (from example)
	vert = 0.5 #what scale is this (from example)
	if (but[1] > 0 and but[0] < 8):
		sX = (but[0] - 4)*scale
		sY = (but[1] - 4)*scale
		if (sX == currentV[0] && sY == currentV[1]):
			currentV[0] = 0
			currentV[1] = 0
		else:
			currentV[0] = sX
			currentV[1] = sY
	elif (but[0] < 2 and but[1] == 0):
		sZ = -(but[0]*2-1)*vert
		if (sZ == currentV[2]):
			currentV[2] = 0
		else:
			currentV[2] = sZ
	elif ((but[0] == 2 or but[0] == 3) and but[1] == 0):
		currentY = ((but[0]-2)*2-1) + currentY
	elif (but == (4, 0, True)):
		currentV = stabilizeParrot()

    condition_yaw(currentY)
	send_nav_velocity(currentV[0], currentV[1], currentV[2])
	return currentV, currentY

def stabilizeParrot():
	send_nav_velocity(0, 0, 0)
	return [0, 0, 0]

def main():

	LP = launchpad.Launchpad()  # creates a Launchpad instance (first Launchpad found)
	LP.Open()                   # start it

	f = open(r'\\.\pipe\flightPipe', 'r+b', 0) # opens FIFO for reading

	#LP.LedCtrlString( 'g', 0, 3, -1 )
	#LP.LedCtrlString( 'g', 3, 0, 1 )

	#controller, sequencer, stable
	mode = "controller"

	currentV = [0, 0, 0]
	currentY = 0

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
					current, currentY = handleButton(but, currentV, currentY)
				if but[2] == False:
					LP.LedCtrlXY( but[0], but[1], 0, 0 )

				LP.LedCtrlXY(5, 0, 3, 0)
			if mode == "sequencer":
				#record, sequence

				LP.LedCtrlXY(6, 0, 3, 0)
			if mode == "stable":
				currentV = stabilizeParrot()

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
			if but == [ 5, 8, True ]:
				break



	LP.Reset() # turn all LEDs off
	LP.Close() # close the Launchpad


if __name__ == '__main__':
	main()
