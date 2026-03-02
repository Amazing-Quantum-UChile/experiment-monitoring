#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 12:33:08 2021

@author: jp, victor

Implements the abstract base class Sensor and MultiSensor for experiment monitoring.

All interfaces for acquiring data should be subclasses that inherit from the Sensor class as they will be called in the main code. 

"""

# Standard library imports:
from abc import ABC, abstractmethod
import traceback
import numpy as np
import logging
logger = logging.getLogger("ExpMonitorLogger")

# Local imports
from expmonitor.utilities.spike_filter import SpikeFilter
from expmonitor.utilities.utility import get_subclass_objects


class AbstractSensor(ABC):
    """---------- INIT ----------"""

    def __init__(
        self,
        database,
        descr="sensor_measurement_name",
        location="Somewhere in the lab",
        unit="°C",
        category="temperature",
        sensor_type="k-type thermocouple",
        conversion_fctn=lambda t: t,
        num_prec=None,
        save_raw=False,
        format_str="f",
        value_limit=(-np.inf, np.inf),
        save_to_database=True,
        is_dummy=False
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
        save_to_database : bool, optional,
            if we send the measurement to the database. This is particularly useful when a sensor has many inputs (e.g. the ADC of the arduino) but not all inputs are effectively connected.
        is_dummy : bool, optional
            if True, we do not connect to the hardware.
        """
        self._db = database
        self.descr = descr.replace(" ", "_").lower()  # str
        self.location = location  # str
        self.unit = unit  # str
        self.category = category  # str
        self.sensor_type = sensor_type  # str
        self.conversion_fctn = conversion_fctn  # function_object
        self.num_prec = num_prec  # Set numerical precision
        self.save_raw = save_raw  # bool
        self.format_str = format_str  # 'f': float, 'i': int, 's': str
        self.value_limit = value_limit
        self.measurement_in_range = True
        self.save_to_database = save_to_database
        self.is_dummy=is_dummy
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
        except (ValueError, TypeError):
            return value

    def _convert(self, value):
        """Perform conversion of received values to proper unit."""
        try:
            return self.conversion_fctn(value)
        except (TypeError, ValueError):
            return None

    def measure(self, verbose=False, show_raw=False):
        """_summary_

        Parameters
        ----------
        verbose : bool, optional
            if measurement is printed, by default False
        show_raw : bool, optional
            if verbose true, shows the raw data of the measurement, by default False
        """
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
        if not self.save_to_database:
            return
        if self.measurement_in_range:
            self._db.write(
                descr=self.descr,
                unit=self.unit,
                measurement=self.measurement,
                location=self.location,
                category=self.category,
                sensor_type=self.sensor_type,
                save_raw=self.save_raw,
                raw=self.raw_vals,
            )
        else:
            print(
                "Measurement ({}) is outside the range {}. Not saved into database.".format(
                    self.measurement, self.value_limit
                )
            )

    def filter_spikes(self):
        if self.spike_filter.enabled:
            if self.spike_filter.was_spike():
                self.spike_filter.del_spike()

    @classmethod
    def _test_execution(cls):
        """Execute measure method for all sensors of this class defined in
        config file and print result to stdout. Has to be preceeded by the
        following import line:
        'from exp_monitor.config import *'."""
        sensor_list = get_subclass_objects(cls)
        for sensor in sensor_list:
            sensor.measure(verbose=True)


class Sensor(AbstractSensor):
    def __init__(self, database, **kwargs):
        super().__init__(database, **kwargs)

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




class SubSensor(AbstractSensor):
    """This class is one of the attribut of the MultiSensor class."""

    def __init__(self, database, **kwargs):
        super().__init__(database, **kwargs)
        self.raw_vals = np.nan

    def connect(self):
        """Do nothing because the connection is handled by a Sensor, not a SubSensor."""
        pass

    def disconnect(self):
        """Do nothing because the disconnection is handled by a Sensor, not a SubSensor."""
        pass

    def rcv_vals(self):
        """Receive and return measurement values from sensor. The value of the sensor measurement must be stored in the raw_vals value by the Sensor parent calling the set_vals function."""
        return self.raw_vals

    def set_vals(self, value):
        """Sets the value of the measurement.

        Parameters
        ----------
        value : _type_
            the measurement of the sensor.
        """
        self.raw_vals = value


class MultiSensor(Sensor):
    def __init__(
        self,
        database,
        number_of_sensors,
        sensor_parameters=[],
        descr="multi_sensor",
        unit="a.u.",
        category="MultiSensor",
        **kwargs
    ):
        """Initialise a MultiSensor. This sensor Object will creates self.subsensors, a list of SubSensor objects (as such, each object of the list are not a Sensor so that we do not call them individually in the main code).

        Parameters
        ----------
        database : expmonitor.utilities.database.Database
            the database object in which data should be stored. All sensors share the same database object.
        number_of_sensors : int
            the number of sensors contained by the MultiSensor. It can be 16 channels for the arduino ADC or 2 (temp and pressure) for a simpler sensor.
        sensor_parameters : list of dictionaries
            each dictionary contains all the key arguments for each subsensor that is created. It should also contained an extra-key called "sensor_number", smaller than number_of_sensors, that refers to the position of the sensor in the list self.subsensors.
        descr : str
            the name of the sensor. Choose widely, e.g. adc_arduino.
        unit : str
            the unit of the sensor, e.g. °C, %, A, V.
        category : str
            the category of the sensor i.e. temperature, voltage, current.
        """
        super().__init__(database, descr=descr, unit=unit, category=category, **kwargs)
        self._db = database
        self.number_of_sensors = number_of_sensors
        self.setup_subsensors()
        self.update_subsensors(sensor_parameters)
        self.successful_measurement = False

    def default_subsensor(self, sensor_number: int):
        """Return the default subsensor parameters using the sensor number

        Parameters
        ----------
        sensor_number : int
            the number of the sensor.

        Returns
        -------
        dict
            the dictionary of parameters
        """
        dic = {
            "descr": "{}_{}".format(self.descr, sensor_number),
            "unit": "a.u.",
            "category": "none",
            "sensor_type": "useless sensor",
            "save_to_database": False,
        }
        return dic

    def setup_subsensors(self):
        """instanciate self.subsensors the lists of AbstractSensor contained by the MultiSensor object with Default sensors."""
        self.subsensors = [
            SubSensor(self._db, **self.default_subsensor(i))
            for i in range(self.number_of_sensors)
        ]

    def update_subsensors(self, sensor_parameters):
        """creates self.subsensors the lists of AbstractSensor contained by the MultiSensor object.

        Parameters
        ----------
        sensor_parameters : list of dict
            list of dictionaries
        """
        for element in sensor_parameters:
            sensor_number = element.pop("sensor_number")
            subsensor = SubSensor(self._db, **element)
            self.subsensors[sensor_number] = subsensor

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

    """ ---------- PUBLIC METHODS ---------- """
    def measure(self, verbose=False, show_raw=False):
        """implements the measure method for the 

        Parameters
        ----------
        verbose : bool, optional
            if measurement is printed, by default False
        show_raw : bool, optional
            if verbose true, shows the raw data of the measurement, by default False
        """
        ## connect and receive all values
        self.connect()
        self.raw_vals = (
            self.rcv_vals()
        )  # this should be a list of values of size number_of_sensors
        try:
            if len(self.raw_vals) != self.number_of_sensors:
                print(
                    "Error when reading the measurement. Please check that the rcv_vals method does return a list of size {} and not {}".format(
                        self.number_of_sensors, len(self.raw_vals)
                    )
                )
                self.successful_measurement = False
                return
            else:
                self.successful_measurement = True
        except TypeError:
            print(
                "Error when reading the measurement. Please check that the rcv_vals method does return a list of size {}".format(
                    self.number_of_sensors
                )
            )
            self.successful_measurement = False
            return

        ## Loop over all sensors
        for i in range(self.number_of_sensors):
            subsensor = self.subsensors[i]
            # store the measurement in each subsensor
            subsensor.set_vals(self.raw_vals[i])
            # we call the measure function (that will process data)
            subsensor.measure(verbose=verbose, show_raw=show_raw)
        self.disconnect()

    def to_db(self):
        """if the measurement is succesful, loop over all subsensors to save to the database."""
        if not self.successful_measurement:
            return
        for subsensor in self.subsensors:
            subsensor.to_db()

    def filter_spikes(self):
        if not self.successful_measurement:
            return
        for subsensor in self.subsensors:
            subsensor.filter_spikes()



class DummyMultiSensor(MultiSensor):
    """class that we use just to test the base calss MultiSensor."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connect(self):
        """Open the connection to the sensor."""
        pass

    def disconnect(self):
        """Close the connection to the sensor."""
        pass

    def rcv_vals(self):
        """Receive and return measurement values from sensor."""
        return np.random.rand(self.number_of_sensors)


