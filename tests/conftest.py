#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 08 12:07:49 2022

Fixtures for all testing modules.

@author: jp
"""

# Standard library imports:
import pytest
import os

# Local imports
from expmonitor.classes.phidget_tc import PhidgetTC
from expmonitor.classes.arduino import Arduino
from expmonitor.utilities.database import Database
from expmonitor.classes.sensor import SubSensor, DummyMultiSensor

# We do not have hardware so all classes in dummy mode
IS_DUMMY=True

@pytest.fixture(scope="session")
def database_instance():
    return Database(port=8086, name="my_database", is_dummy=IS_DUMMY)


@pytest.fixture(scope="session")
def arduino_instance():
    return Arduino(port=1, baudrate=9600, is_dummy=IS_DUMMY)

######## SENSORS ########
@pytest.fixture(scope="function")
def subsensor_instance(database_instance):
    return SubSensor(database_instance, descr="My amazing sensor", is_dummy=IS_DUMMY)

@pytest.fixture(scope="function")
def multi_sensor_instance(database_instance):
    subsensors_parameters = [
            {
                "sensor_number": 1,
                "descr": "temp_k_door",
                "unit": "°C",
                "category": "temperature",
                "sensor_type": "type K thermocouple",
                "save_to_database": True,
            }
        ]
    multisensor = DummyMultiSensor(
        database=database_instance,
        number_of_sensors=3,
        sensor_parameters=subsensors_parameters,
        descr="My amazing Multi-sensor",
    )
    return multisensor


######## PHIDGETS ########
@pytest.fixture(scope="function")
def lab_temp_phidget(database_instance):
    """Return sensor object for lab temp phidget."""
    tc0 = PhidgetTC(
         hub_serial=622701,
        hub_port=0,
        hub_channel=0,
        database=database_instance,
        descr="temp_k_table_rb_vapor",
        location="Optical table, optics near the science Rb Cell",
        is_dummy=IS_DUMMY
        )
    return tc0