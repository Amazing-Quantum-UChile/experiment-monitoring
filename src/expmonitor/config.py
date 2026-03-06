#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 16:35:44 2021

@author: jp, victor

Configuration file for experiment monitoring.

This file regroups all user input for individual setups. Enter all required
information in all sections for the proposed sensors and lab equipment below,
or feel free to add any new hardware interface you want to connect.
"""


""" ---------- GENERAL SETUP ---------- """
import logging, os

from expmonitor.utilities.exception_handler import setup_logging
from expmonitor.utilities.database import Database
from expmonitor.classes.arduino import Arduino
from expmonitor.classes.arduino_adc import Arduino_ADC_Sensor
# Define interval [s] for data acquisition (+ execution time):
acq_interv = 3

# Instanciate the database connection
database = Database(port=8086, name="amazQdatabase")

""" ---------- LOG SET UP ----------"""
# Exception logging:
overwrite_log_file = True  # Replace old log file each time exec is run
verbose = False  # Prints exception traceback to stdout
log_level = logging.INFO
log_dir =os.path.join(os.path.expanduser("~"), ".expmonitor", "logs.txt")
log_format = logging.Formatter('%(asctime)s – %(levelname)s — %(message)s', datefmt='%Y/%m/%d - %Hh%M')
logger = setup_logging(
        name="ExpMonitorLogger",#This name must match the name in all files
        verbose=verbose,
        database_obj=database,
        log_format=log_format,
        log_level=log_level,
        log_dir=log_dir,
        overwrite_log_file=overwrite_log_file
    )


""" ---------- ARDUINO CONNECTION ---------- """


arduino_board = Arduino(port="/dev/ttyUSB0", baudrate=9600)


""" ---------- SENSOR SETUP ---------- """

# Import all specific sensor classes:
###############################
# # Setup Temperature Phidgets:
###############################
from expmonitor.classes.phidget_tc import PhidgetTC

tc0 = PhidgetTC(
    hub_serial=622701,
    hub_port=0,
    hub_channel=0,
    database=database,
    descr="temp_k_table_rb_vapor",
    location="Optical table, optics near the science Rb Cell",
    is_dummy=False
)
tc1 = PhidgetTC(
    hub_serial=622701,
    hub_port=0,
    hub_channel=1,
    database=database,
    descr="temp_k_table_locking",
    location="Optical table, optics of the locking.",
    is_dummy=False
)
tc2 = PhidgetTC(
    hub_serial=622701,
    hub_port=0,
    hub_channel=2,
    database=database,
    descr="temp_k_table_laser",
    location="Optical table, optics near the laser.",
)
tc4 = PhidgetTC(
    hub_serial=622701,
    hub_port=0,
    hub_channel=4,
    database=database,
    descr="temp_k_phidget",
    location="Experiment computer"
)

#############################
######## Arduino ADC ########
#############################
## In this list, we provide the information of all channels of the ADC. 
adc_subsensors_parameters = [
            {
            "sensor_number": 9,# i.e. A9 
            "descr": "voltage monitoring photodiode",
            "unit": "V",
            "category": "voltage",
            "sensor_type": "Photodiode",
            "save_to_database": True,
            }
        ]
adc_sensor = Arduino_ADC_Sensor(
    database=database,
    board= arduino_board,
    sensor_parameters=adc_subsensors_parameters,
    descr="adc_arduino",
)

# # Setup serial devices:
# primary_vac = TPG261('Primary Pump', '/dev/ttyUSB0')
# primary_vac.spike_filter.spike_threshold_perc = 1e3

# # Setup analog devices via Arduino:
# sc_vac = TPG300('Science Chamber', 2)
# sc_vac.spike_filter.spike_threshold_perc = 1e3
# sc_vac.spike_filter.spike_length = 2

# # Setup batteries:
# batteries = EatonUPS('Batteries', '10.117.51.129')



