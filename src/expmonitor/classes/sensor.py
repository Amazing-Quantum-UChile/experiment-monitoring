#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 12:33:08 2021

@author: jp, victor

Implements the abstract base class Sensor for experiment monitoring.

All interfaces for acquiring data should be subclasses that inherit from this
class.
"""

# Standard library imports:
from abc import ABC, abstractmethod
import traceback
import numpy as np
# Local imports
from expmonitor.utilities.spike_filter import SpikeFilter
from expmonitor.utilities.utility import get_subclass_objects


class Sensor(ABC):
    _format_dict = {"f": float, "i": round, "s": str}
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

    def _apply_num_prec(self, value, num_prec):
        """Apply numerical precision to value."""
        if num_prec is None:
            return value
        try:
            return float("{:.{}f}".format(float(value),num_prec))
        except (ValueError, TypeError):
            return value

    def _apply_format(self, value, format):
        """Apply format to value."""
        try:
            return self._format_dict[format](value)
        except (ValueError, KeyError):
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
        self.measurement = self._apply_num_prec(self.measurement, self.num_prec)
        self.measurement = self._apply_format(self.measurement, self.format_str)
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

class MultiChannelsSensor(Sensor):
    def __init__(self,
        database,
        channel_number,
        descr,
        location, 
        unit,
        category, 
        sensor_type,
        conversion_fctn=None,
        num_prec=None,
        save_raw=None,
        format_str=None,
        value_limit=None,
        save_data=True):
        """Abstract class for the MultiChannelsSensor method. 

        Parameters
        ----------
        database : expmonitor.utilities.database.Database
            the database object in which data should be stored. All sensors share the same database object. 
        channel_number: int
            the number of channels (sensor) of the sensor.
        descr : list of str os size channel_number
            the description of the sensor that will be used as the short name in the database. Choose widely, e.g. temp_k_table_locking ; humidity_table_rb_vapor ; current_coil_mot ; voltage_photodiode_lattice.
        location : list of str os size channel_number
            where the sensor is located.
        unit : list of str of size channel_number
            the unit of the sensor, e.g. °C, %, A, V.
        category : list of str of size channel_number
            the category of the measurement i.e. temperature, voltage, current. 
        sensor_type : list of str of size channel_number
            the type of sensor e.g. k-type thermocouple.
        conversion_fctn : list of lambda function os size channel_number, optional
            the conversion function of the sensor, by default None
        num_prec : list of floats, optional
            the precision to register in the database, by default None
        save_raw : list of bools, optional
            _description_, by default None
        format_str : list of str, optional
            _description_, by default None
        value_limit : list of tuples, optional
            the range in which the value should belong to, by default (-np.inf, np.inf)
        """
        if conversion_fctn is None:
            conversion_fctn=[lambda t:t for i in range(channel_number)]
        elif type(conversion_fctn) ==type(lambda t:t):
            conversion_fctn=[conversion_fctn for i in range(channel_number)]
        if num_prec is None:
            num_prec=[None for i in range(channel_number)]
        elif isinstance(num_prec, (int, float)):
            num_prec=[num_prec for i in range(channel_number)]
        if save_raw is None:
            save_raw=[False for i in range(channel_number)]
        elif type(save_raw)==bool:
            save_raw=[save_raw for i in range(channel_number)]
        if format_str is None:
            format_str=["f" for i in range(channel_number)]
        elif type(format_str)==str:
            format_str=[format_str for i in range(channel_number)]
        if value_limit is None:
            value_limit=[(-np.inf, np.inf) for i in range(channel_number)]
        elif type(value_limit)==tuple:
            value_limit=[value_limit for i in range(channel_number)]
        ## check everything has the same size
        attributes = {
            "descr": descr, "location": location, "unit": unit, "category": category,
            "sensor_type": sensor_type, "conversion_fctn": conversion_fctn,
            "num_prec": num_prec, "save_raw": save_raw, "format_str": format_str,
            "value_limit": value_limit
        }
        for name, value in attributes.items():
            if not isinstance(value, list):
                raise TypeError(f"'{name}' must be a list (got {type(value).__name__})")
            if len(value) != channel_number:
                raise ValueError(f"'{name}' list length must be {channel_number} (got {len(value)})")

    def measure(self, verbose=False, show_raw=False):
        """Execute a measurement."""
        self.connect()
        self.raw_vals = self.rcv_vals() ## list of values
        self.measurements=[0 for i in range()]
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
        self.measurement = self._apply_num_prec(self.measurement, self.num_prec)
        self.measurement = self._apply_format(self.measurement, self.format_str)
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

