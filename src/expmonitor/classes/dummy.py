#!/usr/bin/env python
# -*- mode:Python; coding: utf-8 -*-

# ----------------------------------
# Created on the Wed Jan 07 2026 by Victor
#
# Copyright (c) 2026 - AmazingQuantum@UChile
# ----------------------------------
#
"""
Content of dummy.py

Thisclass implements a dummy class for testing purposes to add fake data in the database
"""
from expmonitor.classes.sensor import Sensor
import numpy as np
from datetime import datetime
import time


class DummyTemp(Sensor):

    def __init__(self, descr):
        # General sensor setup:
        self.type = "Thermocouple"
        self.descr = descr.replace(" ", "_").lower() + "_temp"  # Multi-word
        self.unit = "°C"
        self.conversion_fctn = lambda t: t  # No conversion needed
        super().__init__(
            self.type, self.descr, self.unit, self.conversion_fctn, num_prec=1
        )

    def connect(self):
        pass

    def disconnect(self):
        pass

    def rcv_vals(self):
        # Receive temperature value:
        return 25


class DummyStableTemperature(DummyTemp):
    def __init__(self, descr, mean_temp, std_temp):
        super().__init__(descr)
        self.mean_temp = mean_temp
        self.std_temp = std_temp

    def rcv_vals(self):
        # Receive temperature value:
        return np.random.normal(self.mean_temp, self.std_temp)


class DummyVaryingTemperature(DummyTemp):
    def __init__(self, descr, mean_temp, std_temp, degree_diff=10):
        super().__init__(descr)
        self.mean_temp = mean_temp
        self.degree_diff = degree_diff
        self.std_temp = std_temp

    def rcv_vals(self):
        # Current time in hours (e.g. 13.5 = 13h30)
        now = datetime.now()
        t = now.hour + now.minute / 60

        # Transition width (1 hour)
        tau = 1  # smaller = sharper transition
        # Smooth day window [9h, 18h]
        day_on = 0.5 * (1 + np.tanh((t - 9) / tau))
        day_off = 0.5 * (1 - np.tanh((t - 18) / tau))
        day_weight = day_on * day_off  # ∈ [0, 1]

        # Interpolated noise
        offset = 2 * self.degree_diff * (day_weight - 1 / 2)
        # Final temperature
        return np.random.normal(self.mean_temp + offset, self.std_temp)


class DummySlowlyVaryingTemperature(DummyTemp):
    def __init__(self, descr, mean_temp, std_temp, deviation_temp=3, drift_time_day=4):
        super().__init__(descr)
        self.mean_temp = mean_temp
        self.deviation_temp = deviation_temp
        self.std_temp = std_temp
        self.drift_time_seconds = drift_time_day * 24 * 60 * 60

    def rcv_vals(self):
        t = time.time()

        # Final temperature
        return np.random.normal(
            np.cos(t / self.drift_time_seconds) * self.deviation_temp + self.mean_temp,
            self.std_temp,
        )


class DummyHumidity(Sensor):
    def __init__(self, descr):
        # General sensor setup:
        self.type = "Humidity Sensor"
        self.descr = descr.replace(" ", "_").lower() + "_humidity"  # Multi-word
        self.unit = "%"
        self.conversion_fctn = lambda t: t  # No conversion needed
        super().__init__(
            self.type, self.descr, self.unit, self.conversion_fctn, num_prec=1
        )

    def connect(self):
        pass

    def disconnect(self):
        pass

    def rcv_vals(self):
        # Receive humidity value:
        return np.random.normal(60, 1)


# sensor = DummySlowlyVaryingTemperature("Test Dummy", mean_temp=22, std_temp=0.0)
# print(sensor.rcv_vals())
# sensor2 = DummyVaryingTemperature(
#     "Test Dummy", mean_temp=100, std_temp=1, degree_diff=30
# )
# print(sensor2.rcv_vals())
# sensor3 = DummyStableTemperature("Test Dummy", mean_temp=22, std_temp=0.5)
# print(sensor3.rcv_vals())
# sensor4 = DummyHumidity("Test Humidity Dummy")
# print(sensor4.rcv_vals())
