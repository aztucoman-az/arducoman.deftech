#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function

from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil  # Needed for command message definitions
import time
import math


# Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(
    description='Control Copter and send commands in GUIDED mode ')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = 'tcp:127.0.0.1:14550'
sitl = None


# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Trigger just below target alt.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude*0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


# Arm and take of to altitude of 5 meters
arm_and_takeoff(5)


def condition_yaw(heading, relative=False):

    if relative:
        is_relative = 1  # yaw relative to direction of travel
    else:
        is_relative = 0  # yaw is an absolute angle
    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,  # command
        0,  # confirmation
        heading,    # param 1, yaw in degrees
        0,          # param 2, yaw speed deg/s
        1,          # param 3, direction -1 ccw, 1 cw
        is_relative,  # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used
    # send command to vehicle
    vehicle.send_mavlink(msg)


def set_roi(location):

    # create the MAV_CMD_DO_SET_ROI command
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_DO_SET_ROI,  # command
        0,  # confirmation
        0, 0, 0, 0,  # params 1-4
        location.lat,
        location.lon,
        location.alt
    )
    # send command to vehicle
    vehicle.send_mavlink(msg)


def get_location_metres(original_location, dNorth, dEast):

    earth_radius = 6378137.0  # Radius of "spherical" earth
    # Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    # New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    if type(original_location) is LocationGlobal:
        targetlocation = LocationGlobal(newlat, newlon, original_location.alt)
    elif type(original_location) is LocationGlobalRelative:
        targetlocation = LocationGlobalRelative(
            newlat, newlon, original_location.alt)
    else:
        raise Exception("Invalid Location object passed")

    return targetlocation


def get_distance_metres(aLocation1, aLocation2):

    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


def get_bearing(aLocation1, aLocation2):

    off_x = aLocation2.lon - aLocation1.lon
    off_y = aLocation2.lat - aLocation1.lat
    bearing = 90.00 + math.atan2(-off_y, off_x) * 57.2957795
    if bearing < 0:
        bearing += 360.00
    return bearing





def goto_position_target_global_int(aLocation):

    msg = vehicle.message_factory.set_position_target_global_int_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,  # frame
        0b0000111111111000,  # type_mask (only speeds enabled)
        aLocation.lat*1e7,  # lat_int - X Position in WGS84 frame in 1e7 * meters
        aLocation.lon*1e7,  # lon_int - Y Position in WGS84 frame in 1e7 * meters
        aLocation.alt,  # alt - Altitude in meters in AMSL altitude, not WGS84 if absolute or relative, above terrain if GLOBAL_TERRAIN_ALT_INT
        0,  # X velocity in NED frame in m/s
        0,  # Y velocity in NED frame in m/s
        0,  # Z velocity in NED frame in m/s
        # afx, afy, afz acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0, 0,
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
    # send command to vehicle
    vehicle.send_mavlink(msg)


def goto_position_target_local_ned(north, east, down):

    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
        0b0000111111111000,  # type_mask (only positions enabled)
        # x, y, z positions (or North, East, Down in the MAV_FRAME_BODY_NED frame
        north, east, down,
        0, 0, 0,  # x, y, z velocity in m/s  (not used)
        # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0, 0,
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
    # send command to vehicle
    vehicle.send_mavlink(msg)


def goto(dNorth, dEast, gotoFunction=vehicle.simple_goto):


    currentLocation = vehicle.location.global_relative_frame
    targetLocation = get_location_metres(currentLocation, dNorth, dEast)
    targetDistance = get_distance_metres(currentLocation, targetLocation)
    gotoFunction(targetLocation)

    # print "DEBUG: targetLocation: %s" % targetLocation
    # print "DEBUG: targetLocation: %s" % targetDistance

    # Stop action if we are no longer in guided mode.
    while vehicle.mode.name == "GUIDED":
        # print "DEBUG: mode: %s" % vehicle.mode.name
        remainingDistance = get_distance_metres(
            vehicle.location.global_relative_frame, targetLocation)
        print("Distance to target: ", remainingDistance)
        # Just below target, in case of undershoot.
        if remainingDistance <= targetDistance*0.01:
            print("Reached target")
            break
        time.sleep(2)



def send_ned_velocity(velocity_x, velocity_y, velocity_z, duration):

    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
        0b0000111111000111,  # type_mask (only speeds enabled)
        0, 0, 0,  # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z,  # x, y, z velocity in m/s
        # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0, 0,
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    # send command to vehicle on 1 Hz cycle
    for x in range(0, duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)


def send_global_velocity(velocity_x, velocity_y, velocity_z, duration):

    msg = vehicle.message_factory.set_position_target_global_int_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,  # frame
        0b0000111111000111,  # type_mask (only speeds enabled)
        0,  # lat_int - X Position in WGS84 frame in 1e7 * meters
        0,  # lon_int - Y Position in WGS84 frame in 1e7 * meters
        # alt - Altitude in meters in AMSL altitude(not WGS84 if absolute or relative)
        0,
        # altitude above terrain if GLOBAL_TERRAIN_ALT_INT
        velocity_x,  # X velocity in NED frame in m/s
        velocity_y,  # Y velocity in NED frame in m/s
        velocity_z,  # Z velocity in NED frame in m/s
        # afx, afy, afz acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0, 0,
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    # send command to vehicle on 1 Hz cycle
    for x in range(0, duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)


print("TRIANGLE path using standard Vehicle.simple_goto()")

print("Set groundspeed to 5m/s.")
vehicle.groundspeed = 5

print("Position North 80 West 50")
goto(80, -50)

print("Position North 0 East 100")
goto(0, 100)

print("Position North -80 West 50")
goto(-80, -50)



print("TRIANGLE path using standard SET_POSITION_TARGET_GLOBAL_INT message and with varying speed.")
print("Position South 100 West 130")

print("Set groundspeed to 5m/s.")
vehicle.groundspeed = 5
goto(-100, -130, goto_position_target_global_int)

print("Set groundspeed to 15m/s (max).")
vehicle.groundspeed = 15
print("Position South 0 East 200")
goto(0, 260, goto_position_target_global_int)

print("Set airspeed to 10m/s (max).")
vehicle.airspeed = 10

print("Position North 100 West 130")
goto(100, -130, goto_position_target_global_int)




print("SQUARE path using SET_POSITION_TARGET_LOCAL_NED and position parameters")
DURATION = 20  # Set duration for each segment.

print("North 50m, East 0m, 10m altitude for %s seconds" % DURATION)
goto_position_target_local_ned(50, 0, -10)
print("Point ROI at current location (home position)")
# NOTE that this has to be called after the goto command as first "move" command of a particular type
# "resets" ROI/YAW commands
set_roi(vehicle.location.global_relative_frame)
time.sleep(DURATION)

print("North 50m, East 50m, 10m altitude")
goto_position_target_local_ned(50, 50, -10)
time.sleep(DURATION)

print("Point ROI at current location")
set_roi(vehicle.location.global_relative_frame)

print("North 0m, East 50m, 10m altitude")
goto_position_target_local_ned(0, 50, -10)
time.sleep(DURATION)

print("North 0m, East 0m, 10m altitude")
goto_position_target_local_ned(0, 0, -10)
time.sleep(DURATION)


# Set up velocity vector to map to each direction.
# vx > 0 => fly North
# vx < 0 => fly South
NORTH = 2
SOUTH = -2

# Note for vy:
# vy > 0 => fly East
# vy < 0 => fly West
EAST = 2
WEST = -2

# Note for vz:
# vz < 0 => ascend
# vz > 0 => descend
UP = -0.5
DOWN = 0.5


# Square path using velocity
print("SQUARE path using SET_POSITION_TARGET_LOCAL_NED and velocity parameters")

print("Yaw 180 absolute (South)")
condition_yaw(180)

print("Velocity South & up")
send_ned_velocity(SOUTH, 0, UP, DURATION)
send_ned_velocity(0, 0, 0, 1)


print("Yaw 270 absolute (West)")
condition_yaw(270)

print("Velocity West & down")
send_ned_velocity(0, WEST, DOWN, DURATION)
send_ned_velocity(0, 0, 0, 1)


print("Yaw 0 absolute (North)")
condition_yaw(0)

print("Velocity North")
send_ned_velocity(NORTH, 0, 0, DURATION)
send_ned_velocity(0, 0, 0, 1)


print("Yaw 90 absolute (East)")
condition_yaw(90)

print("Velocity East")
send_ned_velocity(0, EAST, 0, DURATION)
send_ned_velocity(0, 0, 0, 1)


print("DIAMOND path using SET_POSITION_TARGET_GLOBAL_INT and velocity parameters")
# vx, vy are parallel to North and East (independent of the vehicle orientation)

print("Yaw 225 absolute")
condition_yaw(225)

print("Velocity South, West and Up")
send_global_velocity(SOUTH, WEST, UP, DURATION)
send_global_velocity(0, 0, 0, 1)


print("Yaw 90 relative (to previous yaw heading)")
condition_yaw(90, relative=True)

print("Velocity North, West and Down")
send_global_velocity(NORTH, WEST, DOWN, DURATION)
send_global_velocity(0, 0, 0, 1)

print("Set new home location to current location")
vehicle.home_location = vehicle.location.global_frame
print("Get new home location")
# This reloads the home location in DroneKit and GCSs
cmds = vehicle.commands
cmds.download()
cmds.wait_ready()
print(" Home Location: %s" % vehicle.home_location)


print("Yaw 90 relative (to previous yaw heading)")
condition_yaw(90, relative=True)

print("Velocity North and East")
send_global_velocity(NORTH, EAST, 0, DURATION)
send_global_velocity(0, 0, 0, 1)


print("Yaw 90 relative (to previous yaw heading)")
condition_yaw(90, relative=True)

print("Velocity South and East")
send_global_velocity(SOUTH, EAST, 0, DURATION)
send_global_velocity(0, 0, 0, 1)


print("Setting LAND mode...")
vehicle.mode = VehicleMode("LAND")


# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl is not None:
    sitl.stop()

print("Completed")

