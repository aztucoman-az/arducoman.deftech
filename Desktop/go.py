
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import math
import sys
import os
import threading
import argparse


# ---- Connecting to Vehicle ----

connection_string= "127.0.0.1:14551"
drone = connect(connection_string, wait_ready=True, timeout=100)

if not connection_string:
	import dronekit_sitl
	sitl = dronekit_sitl.start_default()
	connection_string=sitl.connection_string()



print("Loading:")

#animation2 = ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", >
#animation = ["[■□□□□□□□□□]","[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]", ]
animation = ["[■□□□□□□□□□]","[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]", "[■■■■■□□□□□]", "[■■■■■■□□□□]", "[■■■■■■■□□□]", "[■■■■■■■■□□]", "[■■■■■■■■■□]", "[■■■■■■■■■■]"]
for i in range(len(animation)):
    time.sleep(0.2)
    sys.stdout.write("\r" + animation[i % len(animation)])
    sys.stdout.flush()

print("\n")




print("				DEVELOPED BY ARDUCOMAN			")


print("\n")
print("Connecting to wehicle on: %s" % connection_string)


print("Drone connected and armed")
def arm_and_takeoff(aTargetAltitude):
	print("Basic pre-arm checks")
	while not drone.is_armable:
		print("Waiting for drone to initialise....")
		time.sleep(0.4)
	print("Arming motors")
	drone.mode=VehicleMode("GUIDED")
	drone.armed=True
	while not  drone.armed:
		print("Waiting for armed")
		time.sleep(0.5)
	print("Taking off")
	drone.simple_takeoff(aTargetAltitude)
	while True:
		print("Altitude:", drone.location.global_relative_frame.alt)
		if drone.location.global_relative_frame.alt>=aTargetAltitude *0.95:
			print("Reached target altitude")
			break
		time.sleep(1)
arm_and_takeoff(0.5)



print("Setting speed:")

animation = ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]
for i in range(len(animation)):
    time.sleep(0.2)
    sys.stdout.write("\r" + animation[i % len(animation)])
    sys.stdout.flush()

print("\n")



drone.airspeed=4
print("Air speed setted {}".format(drone.airspeed))

print("Going towards first point for 30 seconds...")


point1=LocationGlobalRelative(-35.36317720, 149.16530269,0.5)
drone.simple_goto(point1)
time.sleep(5)
point2=LocationGlobalRelative( -35.36317387, 149.16525119,0.5)
drone.simple_goto(point2)
time.sleep(15)
point3=LocationGlobalRelative(-35.36317587, 149.16513921,0.5)
drone.simple_goto(point3)
time.sleep(15)
point4=LocationGlobalRelative(-35.36316387 ,149.16514003,0.5)
drone.simple_goto(point4)
time.sleep(15)
point5=LocationGlobalRelative(-35.36315521, 149.16515556,0.5)
drone.simple_goto(point5)
time.sleep(15)
point6=LocationGlobalRelative(-35.36315521, 149.16520951,0.5)
drone.simple_goto(point6)
time.sleep(15)
point7=LocationGlobalRelative(-35.36315187, 149.16525528,0.5)
drone.simple_goto(point7)
time.sleep(15)
point8=LocationGlobalRelative(-35.36313921, 149.16530432,0.5)
drone.simple_goto(point8)
time.sleep(15)


#print("Current position",drone.location.global_relative.frame)

#print("Going to second point for 25 sec (groundspeed set to 10 m/s)...")
#point2=LocationGlobalRelative(-35.36323255, 149.16531280,20)
#drone.simple_goto(point2,groundspeed=10)
#time.sleep(20)

#print("Drone going to third point")
#point3=LocationGlobalRelative(-35.36323159,149.16527901,20)
#drone.simple_goto(point3)
#time.sleep(30)


#point4=LocationGlobalRelative(-35.36322917,149.16526419,20)
#drone.simple_goto(point4)
#time.sleep(20)

#point5=LocationGlobalRelative(-35.36322675,149.16525352,20)
#drone.simple_goto(point5)
#time.sleep(15)

#point6=LocationGlobalRelative(-35.36323062,149.16524403,20)
#drone.simple_goto(point6)
#time.sleep(15)

#point7=LocationGlobalRelative(-35.36322869,149.16523277,20)
#drone.simple_goto(point7)
#time.sleep(15)

#point8=LocationGlobalRelative(-35.36322724,149.16521676,20)
#drone.simple_goto(point8)
#time.sleep(15)

#point9=LocationGlobalRelative(-35.36322675,149.16520668,20)
#drone.simple_goto(point9)
#time.sleep(15)

#point10=LocationGlobalRelative(-35.3536322579,149.16514087,20)
#drone.simple_goto(point10)
#time.sleep(15)

#print("Drone detect mine radius of 25 sm")
#point11=LocationGlobalRelative(-35.36320645,149.16514265,20)
#drone.simple_goto(point11)
#time.sleep(15)






print("Drone return to lunch")
drone.mode = VehicleMode("RTL")
time.sleep(30)

##############################################################

print("   Supports COMMAND_INT message type: %s" % drone.capabilities.command_int)
print("   Supports PARAM_UNION message type: %s" % drone.capabilities.param_union)
print("   Supports ftp for file transfers: %s" % drone.capabilities.ftp)
print("   Supports commanding attitude offboard: %s" % drone.capabilities.set_attitude_target)
print("   Supports commanding position and velocity targets in local NED frame: %s" % drone.capabilities.set_attitude_target_local_ned)
print("   Supports set position + velocity targets in global scaled integers: %s" % drone.capabilities.set_altitude_target_global_int)
print("   Supports terrain protocol / data handling: %s" % drone.capabilities.terrain)
print("   Supports direct actuator control: %s" % drone.capabilities.set_actuator_target)
print("   Supports the flight termination command: %s" % drone.capabilities.flight_termination)
print("   Supports mission_float message type: %s" % drone.capabilities.mission_float)
print("   Supports onboard compass calibration: %s" % drone.capabilities.compass_calibration)
print(" Global Location: %s" % drone.location.global_frame)
print(" Global Location (relative altitude): %s" % drone.location.global_relative_frame)
print(" Local Location: %s" % drone.location.local_frame)
print(" Attitude: %s" % drone.attitude)
print(" Velocity: %s" % drone.velocity)
print(" GPS: %s" % drone.gps_0)
print(" Gimbal status: %s" % drone.gimbal)
print(" Battery: %s" % drone.battery)
print(" EKF OK?: %s" % drone.ekf_ok)
print(" Last Heartbeat: %s" % drone.last_heartbeat)
print(" Rangefinder: %s" % drone.rangefinder)
print(" Rangefinder distance: %s" % drone.rangefinder.distance)
print(" Rangefinder voltage: %s" % drone.rangefinder.voltage)
print(" Heading: %s" % drone.heading)
print(" Is Armable?: %s" % drone.is_armable)
print(" System status: %s" % drone.system_status.state)
print(" Groundspeed: %s" % drone.groundspeed)    # settable
print(" Airspeed: %s" % drone.airspeed)    # settable
print(" Mode: %s" % drone.mode.name)    # settable
print(" Armed: %s" % drone.armed)    # settable
print("\nSet new home location")
# Home location must be within 50km of EKF home location (or setting will fail silently)


print("Complete")

print("Drone complete first task")

print("Thanks for a ride")
print("Powered by ARDUCOMAN")





