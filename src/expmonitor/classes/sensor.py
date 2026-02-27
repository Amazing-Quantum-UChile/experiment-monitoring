#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 12:33:08 2021

@author: jp

Implements the abstract base class Sensor for experiment monitoring.

All interfaces for acquiring data should be subclasses that inherit from this
class.
"""

# Standard library imports:
from abc import ABC, abstractmethod
from influxdb import InfluxDBClient
import traceback
import numpy as np

# Local imports
from expmonitor.utilities.spike_filter import SpikeFilter
from expmonitor.utilities.utility import get_subclass_objects


class Sensor(ABC):
    """---------- INIT ----------"""

    def __init__(
        self,
        database,
        descr,
        location, 
        unit,
        category, 
        sensor_type,
        conversion_fctn=lambda t: t,
        num_prec=None,
        save_raw=False,
        format_str="f",
        value_limit=(-np.inf, np.inf),
    ):
        """Abstract class for the Sensor method. 

        Parameters
        ----------
        database : expmonitor.utilities.database.Database
            the database object in which data should be stored. All sensors share the same database object. 
        descr : str
            the description of the sensor that will be used as the short name in the database. Choose widely, e.g. temp_k_table_locking ; humidity_table_rb_vapor ; current_coil_mot ; voltage_photodiode_lattice.
        location : str
            where the sensor is located.
        unit : str
            the unit of the sensor, e.g. °C, %, A, V.
        category : str
            the category of the measurement i.e. temperature, voltage, current. 
        sensor_type : str
            the type of sensor e.g. k-type thermocouple.
        conversion_fctn : lambda function, optional
            the conversion function of the sensor, by default lambdat:t
        num_prec : float, optional
            the precision to register in the database, by default None
        save_raw : bool, optional
            _description_, by default False
        format_str : str, optional
            _description_, by default "f"
        value_limit : tuple, optional
            the range in which the value should belong to, by default (-np.inf, np.inf)
        """
        self._db = database
        self.descr = descr  # str
        self.location=location # str
        self.unit = unit  # str
        self.category = category # str
        self.sensor_type = sensor_type # str
        self.conversion_fctn = conversion_fctn  # function_object
        self.num_prec = num_prec  # Set numerical precision
        self.save_raw = save_raw  # bool
        self.format_str = format_str  # 'f': float, 'i': int, 's': str
        self.value_limit = value_limit
        self.measurement_in_range = True
        # Spike filter setup:
        self.spike_filter = SpikeFilter(self, spike_threshold_perc=None)
        

    """ ---------- PROPERTIES ---------- """

    @property
    def num_prec(self):
        """Set numerical precision for measurement values.
        For example, num_prec = 12 saves 1.2381e-10 as 1.24e-10."""
        return self._num_prec

    @num_prec.setter
    def num_prec(self, num_prec):
        if type(num_prec) == int and num_prec > 0:
            self._num_prec = num_prec
        else:
            self._num_prec = None

    @property
    def format_str(self):
        """Set format in which to save measurement data. Currently all data
        within one influxDB shard needs to be of the same format."""
        return self._format_str

    @format_str.setter
    def format_str(self, format_str):
        self._format_dict = {"f": float, "i": round, "s": str}
        if format_str in self._format_dict.keys():
            self._format_str = format_str
        else:
            self._format_str = "f"

    @property
    def save_raw(self):
        return self._save_raw

    @save_raw.setter
    def save_raw(self, save_raw):
        if type(save_raw) == bool:
            self._save_raw = save_raw
        else:
            self._save_raw = False

    """ ---------- ABSTRACT METHODS ---------- """

    @abstractmethod
    def connect(self):
        """Open the connection to the sensor."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close the connection to the sensor."""
        pass

    @abstractmethod
    def rcv_vals(self):
        """Receive and return measurement values from sensor."""
        pass  # return received_vals

    """ ---------- PRIVATE METHODS ---------- """

    def _show(self, show_raw=False):
        """Print last measurement with description and units."""
        try:
            if show_raw:
                print(
                    self.descr, self.measurement, self.unit, ";\t raw:", self.raw_vals
                )
            else:
                print(self.descr, self.measurement, self.unit)
        except AttributeError as ae:
            print(self.descr, "_show AttributeError:", ae.args[0])

    def _apply_num_prec(self, value):
        """Apply numerical precision to value."""
        try:
            return float("{:.{}f}".format(float(value), self._num_prec))
        except (ValueError, TypeError):
            return value

    def _apply_format(self, value):
        """Apply format to value."""
        try:
            return self._format_dict[self._format_str](value)
        except ValueError:
            return value

    def _convert(self, value):
        """Perform conversion of received values to proper unit."""
        try:
            return self.conversion_fctn(value)
        except (TypeError, ValueError):
            return None

    """ ---------- PUBLIC METHODS ---------- """

    def measure(self, verbose=False, show_raw=False):
        """Execute a measurement."""
        self.connect()
        self.raw_vals = self.rcv_vals()
        self.measurement = self._convert(self.raw_vals)
        # Check if measurement in range allowed
        try:
            if (self.measurement > min(self.value_limit)) and (
                self.measurement < max(self.value_limit)
            ):
                self.measurement_in_range = True
            else:
                self.measurement_in_range = False
        except Exception as e:
            print(e)
            self.measurement_in_range = True
        # Account for numerical precision and format:
        self.measurement = self._apply_num_prec(self.measurement)
        self.measurement = self._apply_format(self.measurement)
        if verbose:
            self._show(show_raw)
        self.disconnect()

    def to_db(self):
        """Write measurement result to database."""
        if self.measurement_in_range:
                self._db.write(
                    descr = self.descr, 
                    unit = self.unit, 
                    measurement = self.measurement,
                    location= self.location ,
                    category=self.category, 
                    sensor_type=self.sensor_type,
                    save_raw =  self.save_raw, 
                    raw=self.raw_vals
                )
        else:
            print(
                "Measurement ({})outside the range {}. Not saved into database.".format(
                    self.measurement, self.value_limit
                )
            )

    def filter_spikes(self):
        if self.spike_filter.enabled:
            if self.spike_filter.was_spike():
                self.spike_filter.del_spike()

    @classmethod
    def test_execution(cls):
        """Execute measure method for all sensors of this class defined in
        config file and print result to stdout. Has to be preceeded by the
        following import line:
        'from exp_monitor.config import *'."""
        sensor_list = get_subclass_objects(cls)
        for sensor in sensor_list:
            sensor.measure(verbose=True)
