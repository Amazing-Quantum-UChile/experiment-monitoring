#!/usr/bin/env python
# -*- mode:Python; coding: utf-8 -*-

# ----------------------------------
# Created on the Sun Mar 08 2026 by Victor
#
# Copyright (c) 2026 - AmazingQuantum@UChile
# ----------------------------------
#
'''
Content of arduino_MAX31965.py

Implements the MAX31965 sensor to dialog with the arduino.
--> When queried with "t", the Arduino returns a string with the temperature in °C of all connected sensors MAX31965 e.g. "23.5,24.1".
See the arduino file in arduino_src/main to access the Arduino driver. 
'''
from expmonitor.classes.arduino import ArduinoMultiSensor
import random


class Arduino_MAX31965_Sensor(ArduinoMultiSensor):
    def __init__(self,
                board, 
                database,
                number_of_sensors=2, 
                descr="max31965",
                sensor_parameters=[{
            "sensor_number": 0,
            "descr": "temp_max31965_0",
            "unit": "°C",
            "category": "temperature",
            "sensor_type": "Platine thermocouple temperature sensor",
            "save_to_database": True,
            },
            {
            "sensor_number": 1,
            "descr": "temp_max31965_1",
            "unit": "°C",
            "category": "temperature",
            "sensor_type": "Platine thermocouple temperature sensor",
            "save_to_database": True,
            },
            ],
                 **kwargs):
        super().__init__(board=board, 
                         database=database, 
                         number_of_sensors=number_of_sensors,
                         descr=descr,
                         sensor_parameters=sensor_parameters,
                           **kwargs)

    def connect(self):
        """Open the connection to the sensor: we do nothing because connection already exists and is handle by the board object."""
        pass

    def disconnect(self):
        """Close the connection to the sensor. We do nothing because connection already exists and is handle by the board object."""
        pass

    def rcv_vals(self):
        """Receive and return measurement values from sensor."""
        if not self.is_dummy:
            result = self.board.query("t", timeout=.5)
            try:
                ## transform the string into list
                return [float(elem) for elem in result.split(",")]
            except:
                return result
        else:
            return [random.random() for i in range(self.number_of_sensors)]


