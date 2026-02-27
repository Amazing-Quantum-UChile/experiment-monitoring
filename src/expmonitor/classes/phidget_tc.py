#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 11:00:08 2021

@author: jp

Implements the Phidget TC Class for experiment monitoring.
"""

# Standard library imports:
from Phidget22.Devices import TemperatureSensor

# Local imports:
from expmonitor.classes.sensor import Sensor


class PhidgetTC(Sensor):

    def __init__(self, 
                 hub_serial, 
                 hub_port, 
                 hub_channel, 
                 database,
                 descr, 
                 location, 
                 unit = "°C",
                 category="temperature", 
                 sensor_type="Type K",
                 num_prec=2,
                 **kwargs):
        # General sensor setup:
        descr = descr.replace(" ", "_").lower() 
        super().__init__(
            database, 
            descr=descr,
            location=location, 
            unit=unit,
            category=category, 
            sensor_type=sensor_type,
            num_prec=num_prec,
            **kwargs
        )        
        # Phidget-specific setup:
        self.hub_serial = hub_serial
        self.hub_port = hub_port
        self.hub_channel = hub_channel
        self.ts_handle = TemperatureSensor.TemperatureSensor()
        # Set addressing parameters to specify which channel to open:
        self.ts_handle.setHubPort(self.hub_port)
        self.ts_handle.setDeviceSerialNumber(self.hub_serial)
        self.ts_handle.setChannel(self.hub_channel)

    def connect(self):
        # Open Phidgets and wait for attachment:
        self.ts_handle.openWaitForAttachment(1000)

    def disconnect(self):
        # Close Phidgets:
        self.ts_handle.close()

    def rcv_vals(self):
        # Receive temperature value:
        return self.ts_handle.getTemperature()


# Execution:
if __name__ == "__main__":

    from expmonitor.config import *

    PhidgetTC.test_execution()
