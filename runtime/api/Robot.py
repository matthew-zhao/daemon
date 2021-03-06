# ------
# Robot.py class
# This runs the robot.
# Copyright 2015. Pioneers in Engineering.
# ------
'''
This module contains functions for reading data from the robot, and for
manipulating the robot.

To use this module, you must first import it:

>>> from api import Robot
'''
import memcache

memcache_port = 12357
mc = memcache.Client(['127.0.0.1:%d' % memcache_port]) # connect to memcache
name_file = open('Tester.txt','r')
motor = {}

def get_motor(name):
    """Returns the current power value for a motor.

    :param name: A string that identifies the motor
    :returns: A value between -100 and 100, which is the power level of that motor.
    """
    name_to_value = mc.get('motor_values')
    if name in name_to_value:
        return name_to_value[name]
    return 'Error, motor with that name not found'

def set_motor(name, value):
    """Sets a motor to the specified power value.

    :param name: A string that identifies the motor
    :param value: A decimal value between -100 and 100, the power level you want to set
    """
    name_to_value = mc.get('motor_values')
    if name in name_to_value:
        name_to_value[name] = value
        mc.set('motor_values', name_to_value)
    else:
        print("No motor with that name")

# TODO: implement
def get_sensor(name):
    """Returns the value, or reading corresponding to the specified sensor.

    :param name: A string that identifies the sensor.
    :returns: The reading of the sensor at the current point in time.
    """
    id_name = ""
    name_file.seek(0)
    for line in name_file:
        if line.split()[0] == name:
            id_name = line.split()[1]
            break
    all_data = mc.get('sensor_values')
    if id_name in all_data:
        return all_data[id_name]
    return 'Error, sensor with that name not found'

def get_all_motors():
    """Returns the current power values for every connected motor.
    """
    return mc.get('motor_values')
