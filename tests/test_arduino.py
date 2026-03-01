#!/usr/bin/env python
# -*- mode:Python; coding: utf-8 -*-

# ----------------------------------
# Created on the Sun Mar 01 2026 by Victor
#
# Copyright (c) 2026 - AmazingQuantum@UChile
# ----------------------------------
#
'''
Content of test_arduino.py

Please document your code ;-).

'''
import pytest


def test_send_query_to_arduino(arduino_instance):
    """test to query the arduino
    """
    res = arduino_instance.query("Test")
    assert  isinstance(res, str)

# subsensors_parameters = [
#             {
#                 "sensor_number": 1,
#                 "descr": "temp_k_door",
#                 "unit": "°C",
#                 "category": "temperature",
#                 "sensor_type": "type K thermocouple",
#                 "save_to_database": True,
#             }
#         ]
#         multisensor = DummyMultiSensor(
#             database,
#             number_of_sensors=3,
#             sensor_parameters=subsensors_parameters,
#             descr="My amazing Multi-sensor",
#         )
#         print(multisensor.descr, " is ", multisensor.location)
#         multisensor.measure(verbose=True)
#         multisensor.to_db()