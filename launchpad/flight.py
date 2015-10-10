#!/usr/bin/env python2

import launchpad
from pygame import time
# import json
import libardrone
# import socket

def handleButton(but, drone, currentV, currentY):
	scale = 0.2 #what scale is this (from example)
	vert = 0.05 #what scale is this (from example)

        # print 'navdata: ', drone.navdata

	if (but[1] > 0 and but[0] < 8):
		if (but[0] < 4):
			sX = (but[0] - 4)*scale
		else:
			sX = (but[0] - 3)*scale
		if (but[1] < 5):
			sY = (but[1] - 5)*scale
		else:
			sY = (but[1] - 4)*scale
		if (sX == currentV[0] and sY == currentV[1]):
			currentV[0] = 0
			currentV[1] = 0
		else:
			currentV[0] = sX
			currentV[1] = sY
                print 'change XY'
	elif (but[0] < 2 and but[1] == 0):
		sZ = -(but[0]*2-1)*vert
		if (sZ == currentV[2]):
			currentV[2] = 0
		else:
			currentV[2] = sZ
                print 'change height'
	elif ((but[0] == 2 or but[0] == 3) and but[1] == 0):
		currentY = ((but[0]-2)*2-1) + currentY
                print 'change yaw'
	elif (but == [4, 0, True]):
		currentV, currentY = stabilizeParrot(drone)
                print 'stabilize'
	elif (but == [8, 8, True]):
                while drone.navdata['drone_state']['fly_mask'] == 0:
                        print('taking off')
		        drone.takeoff() # REPEAT UNTIL TAKEOFF
                        time.wait(16)
                print 'takeoff successful'
	elif (but == [8, 5, True]):
                while drone.navdata['drone_state']['fly_mask'] == 1:
                        print('landing')
		        drone.land() # REPEAT UNTIL LANDING
                        time.wait(16)
                print 'landing successful'

	drone.at(libardrone.at_pcmd, True, currentV[0], currentV[1], currentV[2], currentY)
	return currentV, currentY

def stabilizeParrot(drone):
	drone.hover()
        print 'stabilize'
	return [0, 0, 0], 0

def readFromSocket(s):
        MSGLEN = 4
	chunks = []
	bytes_recd = 0
	while bytes_recd < MSGLEN:
		chunk = s.recv(min(MSGLEN - bytes_recd, 2048))
		if chunk == '':
			raise RuntimeError('socket connection broken')
		chunks.append(chunk)
		bytes_recd = bytes_recd + len(chunk)
	return ''.join(chunks)

def main():
        print 'main started'

        print 'connecting to launchpad'
	LP = launchpad.Launchpad()  # creates a Launchpad instance (first Launchpad found)
        print 'connected, opening launchpad'
	LP.Open()                   # start it
        print 'opened, reset launchpad'
        LP.Reset()
        print 'reset'

        print 'connecting to drone'
	drone = libardrone.ARDrone("192.168.1.1")
        print 'connected'

        print 'asking for navdata'
        print drone.navdata

        while not drone.navdata:
            time.wait(33)
            print drone.navdata

	LP.LedCtrlString( 'UB', 0, 3, -1 )

        if 'emergency_mask' in drone.navdata['drone_state']:
                while drone.navdata['drone_state']['emergency_mask'] == 1:
                        print 'resetting'
                        drone.reset()
                        time.wait(16)
                print 'reset'

	LP.LedCtrlString( 'RY', 3, 0, 1 )


	#controller, sequencer, stable
	mode = "controller"

	currentV = [0, 0, 0]
	currentY = 0

	print "Checking for presses. 'arm' to end."
	while True:
		time.wait(10)

		but = LP.ButtonStateXY()
		if but != []:

			if mode == "controller":
				#big controller :^)
				LP.LedCtrlXY( but[0], but[1], 0, 3 )
				print( but )
				if but[2]:
					current, currentY = handleButton(but, drone, currentV, currentY)
				if but[2] == False:
					LP.LedCtrlXY( but[0], but[1], 0, 0 )

				LP.LedCtrlXY(5, 0, 3, 0)
			if mode == "sequencer":
				#record, sequence

				LP.LedCtrlXY(6, 0, 3, 0)
			if mode == "stable":
				currentV = stabilizeParrot(drone)

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
			if but == [8, 2, True]:
                                print 'breaking'
				break



        drone.halt()
	LP.Reset() # turn all LEDs off
	LP.Close() # close the Launchpad


if __name__ == '__main__':
	main()
