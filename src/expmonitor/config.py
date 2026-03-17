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
from expmonitor.classes.arduino_AHT10 import Arduino_AHT10_Sensor
from expmonitor.classes.arduino_AHT20_BMP280 import Arduino_AHT20_BMP280_Sensor
from expmonitor.classes.arduino_QMC5883L import Arduino_QMC5883L_Sensor
from expmonitor.classes.arduino_MAX31965 import Arduino_MAX31965_Sensor

# Define interval [s] for data acquisition (+ execution time):
acq_interv = 3

# Instanciate the database connection
database = Database(port=8086, name="amazQdatabase")

""" ---------- LOG SET UP ----------"""
# Exception logging:
overwrite_log_file = True  # Replace old log file each time exec is run
verbose = True  # Prints exception traceback to stdout
log_level = logging.INFO
log_dir = os.path.join(os.path.expanduser("~"), ".expmonitor", "logs.txt")
log_format = logging.Formatter(
    "%(asctime)s – %(levelname)s — %(message)s", datefmt="%Y/%m/%d - %Hh%M"
)
logger = setup_logging(
    name="ExpMonitorLogger",  # This name must match the name in all files
    verbose=verbose,
    database_obj=database,
    log_format=log_format,
    log_level=log_level,
    log_dir=log_dir,
    overwrite_log_file=overwrite_log_file,
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
    is_dummy=False,
)
tc1 = PhidgetTC(
    hub_serial=622701,
    hub_port=0,
    hub_channel=1,
    database=database,
    descr="temp_k_table_locking",
    location="Optical table, optics of the locking.",
    is_dummy=False,
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
    location="Experiment computer",
)

#############################
######## Arduino ADC ########
#############################
## In this list, we provide the information of all channels of the ADC.
adc_subsensors_parameters = [
    {
        "sensor_number": 9,  # i.e. A9
        "descr": "voltage monitoring photodiode",
        "unit": "V",
        "category": "voltage",
        "sensor_type": "Photodiode",
        "save_to_database": True,
    }
]
adc_sensor = Arduino_ADC_Sensor(
    board=arduino_board,
    database=database,
    sensor_parameters=adc_subsensors_parameters,
    descr="adc_arduino",
)
# aht10 = Arduino_AHT10_Sensor( database=database,
#     board= arduino_board,)
ahtbmp_sensor = Arduino_AHT20_BMP280_Sensor(
    board=arduino_board,
    database=database,
    number_of_sensors=4,
    descr="aht20_bmp280_squeezing_table",
    sensor_parameters=[
        {
            "sensor_number": 0,
            "descr": "temp_aht20_squeezing_table",
            "unit": "°C",
            "category": "temperature",
            "sensor_type": "P-N junction temperature sensor",
            "save_to_database": True,
            "value_limit": (0, 40),
        },
        {
            "sensor_number": 1,
            "descr": "humid_aht20_squeezing_table",
            "unit": "%",
            "category": "humidity",
            "sensor_type": "capacitive polymer hygrometer",
            "save_to_database": True,
            "value_limit": (0, 100),
        },
        {
            "sensor_number": 2,
            "descr": "temp_bmp280_squeezing_table",
            "unit": "°C",
            "category": "temperature",
            "sensor_type": "Integrated CMOS capacitive/resistive temperature sensor",
            "save_to_database": True,
            "value_limit": (0, 40),
        },
        {
            "sensor_number": 3,
            "descr": "pressure_bmp280_squeezing_table",
            "unit": "hPa",
            "category": "pressure",
            "sensor_type": "Piezoresistive Barometric Pressure Sensor",
            "save_to_database": True,
            "value_limit": (300, 1300),
        },
    ],
)

### Magnetic field sensor
mag_field_sensor = Arduino_QMC5883L_Sensor(
    board=arduino_board,
    database=database,
    number_of_sensors=3,
    descr="qmc5883l",
    sensor_parameters=[
        {
            "sensor_number": 0,
            "descr": "mag_x_rb_cell",
            "unit": "mG",
            "category": "magnetic field",
            "sensor_type": "Anisotropic Magneto-Resistive sensor",
            "conversion_fctn": lambda t: t,
            "save_to_database": True,
        },
        {
            "sensor_number": 1,
            "descr": "mag_y_rb_cell",
            "unit": "mG",
            "category": "magnetic field",
            "sensor_type": "Anisotropic Magneto-Resistive sensor",
            "conversion_fctn": lambda t: t,
            "save_to_database": True,
        },
        {
            "sensor_number": 2,
            "descr": "mag_z_rb_cell",
            "unit": "mG",
            "category": "magnetic field",
            "sensor_type": "Anisotropic Magneto-Resistive sensor",
            "conversion_fctn": lambda t: t,
            "save_to_database": True,
        },
    ],
)

###-- MAX temperature sensor
Arduino_MAX31965_Sensor(
    board=arduino_board,
    database=database,
    number_of_sensors=2,
    descr="max31965",
    sensor_parameters=[
        {
            "sensor_number": 0,
            "descr": "temp_max_rb_locking",
            "unit": "°C",
            "category": "temperature",
            "sensor_type": "Platine thermocouple temperature sensor",
            "save_to_database": True,
            "conversion_fctn": lambda t: t,
        },
        {
            "sensor_number": 1,
            "descr": "temp_max_aom_locking",
            "unit": "°C",
            "category": "temperature",
            "sensor_type": "Platine thermocouple temperature sensor",
            "save_to_database": True,
            "conversion_fctn": lambda t: t,
        },
    ],
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
