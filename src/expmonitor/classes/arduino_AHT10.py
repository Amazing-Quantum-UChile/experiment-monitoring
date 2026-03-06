#!/usr/bin/env python
# -*- mode:Python; coding: utf-8 -*-

# ----------------------------------
# Created on the Fri Mar 06 2026 by Victor
#
# Copyright (c) 2026 - AmazingQuantum@UChile
# ----------------------------------
#
'''
Content of arduino_AHT10.py

Please document your code ;-).

'''

from expmonitor.classes.arduino import ArduinoMultiSensor
import random

class Arduino_ADC_Sensor(ArduinoMultiSensor):
    def __init__(self,
                board, 
                database,
                number_of_sensors=2, 
                descr="aht10",
                sensor_parameters=[{
            "sensor_number": 0,
            "descr": "temp_aht10",
            "unit": "°C",
            "category": "temperature",
            "sensor_type": "P-N junction temperature sensor",
            "save_to_database": True,
            },
            {
            "sensor_number": 1,
            "descr": "humid_aht10",
            "unit": "%",
            "category": "humidity",
            "sensor_type": "capacitive polymer hygrometer",
            "save_to_database": True,
            }],
                 **kwargs):
        super().__init__(board=board, database=database, number_of_sensors=number_of_sensors, **kwargs)

    def connect(self):
        """Open the connection to the sensor: we do nothing because connection already exists and is handle by the board object."""
        pass

    def disconnect(self):
        """Close the connection to the sensor. We do nothing because connection already exists and is handle by the board object."""
        pass

    def rcv_vals(self):
        """Receive and return measurement values from sensor."""
        if not self.is_dummy:
            result = self.board.query("h", timeout=.5)
            try:
                ## transform the string into list
                return [float(elem) for elem in result.split(",")]
            except:
                return result
        else:
            return [random.random() for i in range(self.number_of_sensors)]


