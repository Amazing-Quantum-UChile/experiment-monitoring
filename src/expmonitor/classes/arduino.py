#!/usr/bin/env python
# -*- mode:Python; coding: utf-8 -*-

# ----------------------------------
# Created on the Fri Feb 27 2026 by Victor
#
# Copyright (c) 2026 - AmazingQuantum@UChile
# ----------------------------------
#
'''
Content of arduino.py

Please document your code ;-).

'''
from expmonitor.classes.sensor import Sensor
import numpy as np

class Arduino():
    def __init__(
        self,
        
    ):
       pass

class ArduinoSensor(Sensor):
    def __init__(self,board,  database,  type, descr, unit, conversion_fctn, **kwargs):
        self._board = board
        super().__init__(database, type, descr, unit, conversion_fctn, **kwargs)


