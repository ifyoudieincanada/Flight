import random
import launchpad
from pygame import time
import time
import struct
import json

def handleButton(but):
	scale = 128
	strengthX = (but[0] - 4)*scale/4
	strengthY = (but[1] - 4)*scale/4

def stabalizeParrot():
	pass
	#stabalize the drone (probably make a parrot object)

def main():

	LP = launchpad.Launchpad()  # creates a Launchpad instance (first Launchpad found)
	LP.Open()                   # start it

	f = open(r'\\.\pipe\wrist', 'r+b', 0) # opens FIFO for reading

	#LP.LedCtrlString( 'g', 0, 3, -1 )
	#LP.LedCtrlString( 'g', 3, 0, 1 )

	#controller, sequencer, stable
	mode = "controller"

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
						handleButton(but)
					else:
						stabalizeParrot()
					prevBut = but
				if but[2] == False:
					LP.LedCtrlXY( but[0], but[1], 0, 0 )

				LP.LedCtrlXY(5, 0, 3, 0)
			if mode == "sequencer":
				#record, sequence

				LP.LedCtrlXY(6, 0, 3, 0)
			if mode == "stable":
				#stabalize

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
