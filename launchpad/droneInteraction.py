#!/usr/bin/env python

# CODE FROM:
# https://github.com/Parrot-Developers/dronekit-python/blob/master/examples/guided_set_speed_yaw/guided_set_speed_yaw.py

import time
from droneapi.lib import VehicleMode, Location, local_connect
from pymavlink import mavutil

api             = local_connect()
vehicle         = api.get_vehicles()[0]
ready           = False

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print "Basic pre-arm checks"
    # Don't let the user try to fly autopilot is booting
    if vehicle.mode.name == "INITIALISING":
        print "Waiting for vehicle to initialise"
        time.sleep(1)
    while vehicle.gps_0.fix_type < 2:
        print "Waiting for GPS...:", vehicle.gps_0.fix_type
        time.sleep(1)

    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode    = VehicleMode("GUIDED")
    vehicle.armed   = True
    vehicle.flush()

    while not vehicle.armed and not api.exit:
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.commands.takeoff(aTargetAltitude) # Take off to target altitude
    vehicle.flush()

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
    #  after Vehicle.commands.takeoff will execute immediately).
    while not api.exit:
        print " Altitude: ", vehicle.location.alt
        if vehicle.location.alt>=aTargetAltitude*0.95: #Just below target, in case of undershoot.
            print "Reached target altitude"
            ready = True
            break;
        time.sleep(1)

# send_nav_velocity - send nav_velocity command to vehicle to request it fly in specified direction
def send_nav_velocity(velocity_x, velocity_y, velocity_z):
    # create the SET_POSITION_TARGET_LOCAL_NED command
    # Check https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_LOCAL_NED
    # for info on the type_mask (0=enable, 1=ignore).
    # Accelerations and yaw are ignored in GCS_Mavlink.pde at the
    # time of writing.
    if ready:
        msg = vehicle.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_BODY_NED, # frame
            0b0000111111000111, # type_mask (only speeds enabled)
            0, 0, 0, # x, y, z positions (not used)
            velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
            0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink.pde)
            0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink.pde)
        # send command to vehicle
        vehicle.send_mavlink(msg)
        vehicle.flush()

# condition_yaw - send condition_yaw mavlink command to vehicle so it points at specified heading (in degrees)
def condition_yaw(heading):
    # create the CONDITION_YAW command
    if ready:
        msg = vehicle.message_factory.mission_item_encode(0, 0,  # target system, target component
                0,     # sequence
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # frame
                mavutil.mavlink.MAV_CMD_CONDITION_YAW,         # command
                2, # current - set to 2 to make it a guided command
                0, # auto continue
                heading,    # param 1, yaw in degrees
                0,          # param 2, yaw speed deg/s
                1,          # param 3, direction -1 ccw, 1 cw
                0,          # param 4, relative offset 1, absolute angle 0
                0, 0, 0)    # param 5 ~ 7 not used
        # send command to vehicle
        vehicle.send_mavlink(msg)
        vehicle.flush()
