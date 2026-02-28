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

# Configure the serial connection (update 'COM port' and baudrate)
# arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)

# def write_read(x):
#     arduino.write(bytes(x, 'utf-8'))
#     time.sleep(0.05)
#     data = arduino.readline()
#     return data.decode('utf-8').strip()

# while True:
#     num = input("Enter a number: ")
#     value = write_read(num)
#     print(f"Response from Arduino: {value}")


class Arduino:
    def __init__(
        self,port, baudrate=9600,
    ):
        """implements the Arduino class.

        Parameters
        ----------
        port : str
            the USB port of the Arduino board.
        baudrate : int, optional
            the beaudrate for the connexion, by default 9600
        timeout : float, optional
            in seconds, the time before which the arduino stops to connect, by default .1
        """
        self.ser = serial.Serial(port, baudrate, timeout=1.)

    def query(self, cmd, timeout=.5):
        """Query the arduino the command cmd

        Parameters
        ----------
        cmd : str
            the command string
        timeout : float, optional
            the maximum time to wait for the answer in seconds, by default .5
        """
        self.ser.timeout = timeout
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
