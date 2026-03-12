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
import logging
log = logging.getLogger("ExpMonitorLogger")

class Database:

    def __init__(self, port, name, is_dummy=False, max_logs=10, use_buffer=True, buffer_size = 50):
        """Connects to the InfluxDB Database.

        Parameters
        ----------
        port : int
            the port of the InfluxDB database
        name : str
            the name of the database
        is_dummy : bool, optional
            if True, instanciate a fake database for tests, by default False
        max_logs : int
            the maximum number of logs stored in the database. 
        use_buffer: bool, optional
            if true, we do not write on the database each time the method write is called. Instead, we write the data in. buffer of size buffer_size and write all points at once. This allowed to weight down the job of the SBC4.
        buffer_size: int, optional 
            the size of the buffer, sets the number of points we wait until to write onto the database.
        """
        self.port = port  # int
        self.name = name  # Make sure this is the same than the name of your influx database
        self.is_dummy = is_dummy
        self.max_logs = 10
        self.use_buffer = use_buffer
        self.buffer_size = buffer_size
        self.buffer = []
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
            if not self.use_buffer:
                self.client.write_points([json_dict])
            else:
                self.add_to_buffer(db_point=json_dict)
        else:
            print("[DummyDatabase] Writing {} into the database.".format(json_dict))

    def add_to_buffer(self, db_point):
        self.buffer.append(db_point)
        if len(self.buffer) >= self.buffer_size:
            log.debug("[Databse] Size of buffer is {}. Sending all points to the database.".format(len(self.buffer)))
            self.client.write_points(self.buffer)
            self.buffer=[]

           
    def store_log(self, msg, levelname, unique_id):
        """store a log in the database (max is self.max_logs=10 by)

        Parameters
        ----------
        msg : str
            msg to store in the database. 
        levelname: str
            The level of the error ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        unique id: str
            we add an ID to make sure InfluxDB log all errors.
        """
        measurement = "logs"

        
        # 1. Get all existing points sorted by time
        points = list(self.client.query('SELECT * FROM "{}" ORDER BY time ASC'.format(measurement)).get_points())
    
        # 2. If we have 10 or more, delete the oldest one
        while len(points) >= self.max_logs:
            oldest_time = points[0]['time']
            self.client.query("DELETE FROM {} WHERE time = '{}'".format(measurement, oldest_time))
            points = list(self.client.query('SELECT * FROM "{}" ORDER BY time ASC'.format(measurement)).get_points())

        # 3. Prepare the new point
        json_error = {
            "measurement": "logs",
            "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tags": { "level": levelname,
                      "unique_id":unique_id },
            "fields": {
                "message": msg
            }
        }
        
        # 4. Write the new point
        if not self.is_dummy:
            self.client.write_points([json_error])
        else:
            print("[DummyDatabase] Error Logged: {}".format(json_error))