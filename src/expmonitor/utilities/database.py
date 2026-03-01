#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 10:15:47 2021

@author: jp

Implements the base class Database for experiment monitoring.

The abstract Sensor class inherits from this class to write measurement data to
the database. It is currently set up to use InfluxDB.
"""

# Standard library imports:
from influxdb import InfluxDBClient
from datetime import datetime


class Database:

    def __init__(self, port, name, is_dummy=False):
        """Connects to the InfluxDB Database.

        Parameters
        ----------
        port : int
            the port of the InfluxDB database
        name : str
            the name of the database
        is_dummy : bool, optional
            if True, instanciate a fake database for tests, by default False
        """
        self.port = port  # int
        self.name = name  # Make sure this is the same than the name of your influx database
        self.is_dummy = is_dummy
        if not self.is_dummy:
            self.client = InfluxDBClient(
                host="localhost", port=self.port, database=self.name
            )

    def write(self, descr, unit, measurement,location, category, sensor_type, save_raw=False, raw=None):
        """Write measurement result to InfluxDB database."""
        json_dict = {}
        json_dict["measurement"] = descr
        json_dict["tags"] = {}
        json_dict["tags"]["unit"] = unit
        json_dict["tags"]["location"] = location
        json_dict["tags"]["category"] = category
        json_dict["tags"]["sensor_type"] = sensor_type
        # Grafana assumes UTC:
        json_dict["time"] = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")
        json_dict["fields"] = {}
        json_dict["fields"]["value"] = measurement
        if save_raw:
            json_dict["fields"]["raw"] = raw
        if not self.is_dummy:
            self.client.write_points([json_dict])
        else:
            print(f"[DummyDatabase] Writting {json_dict} into the database.")
