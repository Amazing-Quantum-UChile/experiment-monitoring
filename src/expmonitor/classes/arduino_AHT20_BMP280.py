#!/usr/bin/env python
# -*- mode:Python; coding: utf-8 -*-

# ----------------------------------
# Created on the Sun Mar 08 2026 by Victor
#
# Copyright (c) 2026 - AmazingQuantum@UChile
# ----------------------------------
#
'''
Content of arduino_AHT20_BMP280.py

Implements the AHT20+BMP280 sensor to dialog with the arduino.
--> When queried with "p", the Arduino returns a string with the temperature, humidity and pressure values separated by a comma, e.g. "24.5, 45.2, 1013.25".
See the arduino file in arduino_src/main to access the Arduino driver. 
'''

from expmonitor.classes.arduino import ArduinoMultiSensor
import random

class Arduino_AHT20_BMP280_Sensor(ArduinoMultiSensor):
    def __init__(self,
                board, 
                database,
                number_of_sensors=4, 
                descr="aht20_bmp280",
                sensor_parameters=[{
            "sensor_number": 0,
            "descr": "temp_aht20",
            "unit": "°C",
            "category": "temperature",
            "sensor_type": "P-N junction temperature sensor",
            "save_to_database": True,
            "value_limit":(0,40),
            },
            {
            "sensor_number": 1,
            "descr": "humid_aht20",
            "unit": "%",
            "category": "humidity",
            "sensor_type": "capacitive polymer hygrometer",
            "save_to_database": True,
            "value_limit":(0,100),
            },
            {
            "sensor_number": 2,
            "descr": "temp_bmp280",
            "unit": "°C",
            "category": "temperature",
            "sensor_type": "Integrated CMOS capacitive/resistive temperature sensor",
            "save_to_database": True,
            "value_limit":(0,40),
            },
            {
            "sensor_number": 3,
            "descr": "pressure_bmp280",
            "unit": "hPa",
            "category": "pressure",
            "sensor_type": "Piezoresistive Barometric Pressure Sensor",
            "save_to_database": True,
            "value_limit":(300, 1300),
            }],
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
            result = self.board.query("p", timeout=.5)
            try:
                ## transform the string into list
                return [float(elem) for elem in result.split(",")]
            except:
                return result
        else:
            return [random.random() for i in range(self.number_of_sensors)]











