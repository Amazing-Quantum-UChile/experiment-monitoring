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
import time

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
        self.ts_handle.openWaitForAttachment(1500)

    def connect(self):
        """
        Establishes a connection to the Phidget device if not already attached. The phidget takes almost 1s to connect so we only check if it is connected or not. 
        """
        ## connecting to Phidget takes a long time so we only check if we are connected or not. 
        # Open Phidgets and wait for attachment:
        if not self.ts_handle.getAttached():
            self.ts_handle.openWaitForAttachment(1000)

    def disconnect(self):
        pass
        # we do not close Phidgets because it is too long to open
        #self.ts_handle.close()

    def rcv_vals(self):
        # Receive temperature value:
        return self.ts_handle.getTemperature()


# Execution:
if __name__ == "__main__":

    from expmonitor.config import *

    PhidgetTC.test_execution()
