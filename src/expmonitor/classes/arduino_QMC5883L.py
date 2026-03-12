#!/usr/bin/env python
# -*- mode:Python; coding: utf-8 -*-

# ----------------------------------
# Created on the Sun Mar 08 2026 by Victor
#
# Copyright (c) 2026 - AmazingQuantum@UChile
# ----------------------------------
#
'''
Content of arduino_QMC5883L.py

Implements the QMC5883L sensor to dialog with the arduino.
--> When queried with "b", the Arduino returns a string with the magnetic field value along the 3 axes "X,Y,Z" e.g. "312,4,1547". Note that the sensor returns the result in bit unit and the conversion to Gauss depends on the hardware resolution chosen (1, 3 or 8 Gauss). To take this into account, use the calibration function conversion_fctn. 
See the arduino file in arduino_src/main to access the Arduino driver. 
'''

from expmonitor.classes.arduino import ArduinoMultiSensor
import random

class Arduino_QMC5883L_Sensor(ArduinoMultiSensor):
    def __init__(self,
                board, 
                database,
                number_of_sensors=4, 
                descr="qmc5883l",
                sensor_parameters=[{
                "sensor_number": 0,
                "descr": "mag_x_qmc5883l",
                "unit": "mG",
                "category": "magnetic field",
                "sensor_type": "Anisotropic Magneto-Resistive sensor",
                "conversion_fctn":lambda t: t,
                "save_to_database": True,
                },
                {
                "sensor_number": 1,
                "descr": "mag_y_qmc5883l",
                "unit": "mG",
                "category": "magnetic field",
                "sensor_type": "Anisotropic Magneto-Resistive sensor",
                "conversion_fctn":lambda t: t,
                "save_to_database": True,
                },
                {
                "sensor_number": 2,
                "descr": "mag_z_qmc5883l",
                "unit": "mG",
                "category": "magnetic field",
                "sensor_type": "Anisotropic Magneto-Resistive sensor",
                "conversion_fctn":lambda t: t,
                "save_to_database": True,
                },],
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
            result = self.board.query("b", timeout=.5)
            try:
                ## transform the string into list
                return [float(elem) for elem in result.split(",")]
            except:
                return result
        else:
            return [random.random() for i in range(self.number_of_sensors)]




