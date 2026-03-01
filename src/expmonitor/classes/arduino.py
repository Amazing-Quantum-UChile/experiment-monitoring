#!/usr/bin/env python
# -*- mode:Python; coding: utf-8 -*-

# ----------------------------------
# Created on the Fri Feb 27 2026 by Victor
#
# Copyright (c) 2026 - AmazingQuantum@UChile
# ----------------------------------
#
"""
Content of arduino.py

Please document your code ;-).

"""
from expmonitor.classes.sensor import Sensor, MultiSensor
import numpy as np
import serial
import time


class Arduino:
    def __init__(
        self,port, baudrate=9600, is_dummy=False
    ):
        """Implements the Arduino class.

        Parameters
        ----------
        port : str
            the USB port of the Arduino board.
        baudrate : int, optional
            the beaudrate for the connexion, by default 9600
        timeout : float, optional
            in seconds, the time before which the arduino stops to connect, by default .1
        is_dummy : bool, optional
            connect to a fake serial port. For test only. 
        """
        if is_dummy:
            self.ser = FakeSerial(port, baudrate)
        else:
            self.ser = serial.Serial(port, baudrate, timeout=1.5)

    def query(self, cmd, timeout=.5,verbose=False):
        """Query the arduino the command cmd

        Parameters
        ----------
        cmd : str
            the command string
        timeout : float, optional
            the maximum time to wait for the answer in seconds, by default .5
        verbose : bool, optional
            if the command sent to the arduino is printed or not
        """
        self.ser.timeout = timeout
        if verbose:
            print(f"[ArduinoQuery] {cmd}")
        self.ser.write(f"{cmd}\n".encode('utf-8'))
        return self.ser.readline().decode('utf-8').strip()


class ArduinoSensor(Sensor):
    def __init__(self, board, database, **kwargs):
        self._board = board
        super().__init__(database, **kwargs)


class ArduinoMultiSensor(MultiSensor):
    def __init__(self, board, database, number_of_sensors, **kwargs):
        self._board = board
        super().__init__(database, number_of_sensors, **kwargs)



### Dummy mode
class FakeSerial():
    def __init__(self, port, baudrate, timeout=.1):
        self.timeout=timeout
        print(f"[FakeSerialPort] Initialisation on port {port} with baudrate {baudrate}.")
    def write(sef, cmd):
        print(f"[FakeSerialPort] Send command '{cmd}'.")
    def readline(self):
        return "".encode('utf-8')

