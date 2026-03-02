#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 15:02:49 2021

@author: jp

Main executable script for Experiment Monitoring.

Service script that is run continously by Linux Systemd. Executes the measure
and to_db methods for all Sensor children defined in config with the frequency
1/acq_interv.
By default, the main loop is run continuously. For testing purposes, it can also
be run a specified amount of times only by passing the corresponding integer as
argument on the command line, e.g. use "python3 exp_monitor/exec.py 5" to run 5
executions of the main loop.
To time the execution of the entire script (however many iterations you specify)
pass the "t" argument on the command line, e.g.:
"python3 exp_monitor/exec.py t 1"
You can also set the "verbose" argument of config.py manually when executing
the script from the command line by including the "v" argument, e.g. use
"python3 exp_monitor/exec.py t v 1" to run 1 execution of the main loop and
print the exception traceback to stdout along with the execution time.
"""

# Standard library imports:
import time, sys, logging
from pathlib import Path

# Local imports:
from expmonitor.config import *
from expmonitor.classes.sensor import Sensor
from expmonitor.utilities.exception_handler import InfluxDBHandler
from expmonitor.utilities.utility import get_subclass_objects


def data_acquisition(sensors, exception_handler):
    """Execute measure method for all sensors."""
    for sensor in sensors:
        try:
            # Make measurement:
            sensor.measure()
            # Write measurement to database:
            sensor.to_db()
            # Run spike filter if set:
            sensor.filter_spikes()
        # Log exceptions but continue execution:
        except Exception as e:
            exception_handler.log_exception(sensor, e)
    # Measurement frequency given by acq_interv:
    time.sleep(acq_interv)


def setup_logging(
    verbose,
    database_obj,
    log_format,
    log_level=logging.WARNING,
    log_file_path=Path.home() / ".expmonitor",
):
    # the logger name must be the same accross all files
    logger = logging.getLogger("ExpMonitorLogger")
    logger.setLevel(log_level)
    # 1. Store error in the log file
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    # 2. Store error in the InfluxDB database
    influx_handler = InfluxDBHandler(database_obj)
    influx_handler.setFormatter(log_format)
    logger.addHandler(influx_handler)

    # 3. Show error in the terminal
    if verbose:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(console_handler)

    return logger


def main():
    """Execute data acquisition cycle continously or a given number of times."""
    # Check for execution time argument on command line:
    if "t" in sys.argv:
        time_exec = True
        start_time = time.time()
        sys.argv.remove("t")
    else:
        time_exec = False
    # Check for verbose argument on command line to override:
    if "v" in sys.argv:
        exception_handler.verbose = True
        sys.argv.remove("v")
    logger = setup_logging(
        verbose=verbose,
        database_obj=database,
        log_level=log_level,
        log_file_path=log_file_path,
    )
    # Get all user defined sensor objects:
    sensors = get_subclass_objects(Sensor)
    sensor_names = "All sensor connected: "
    for sensor in sensors:
        sensor_names.append(sensor.descr) + ", "
    logger.info(sensor_names[:-2]+".")
    # If int argument passed on command line: Run user-defined number of times:
    try:
        sys.argv.remove(sys.argv[0])
        iterations = int(sys.argv[0])
        for iteration in range(iterations):
            print("Iteration", iteration + 1, "/", iterations)
            data_acquisition(sensors, exception_handler)
    except (IndexError, ValueError):  # Default: Run continously
        while True:
            data_acquisition(sensors, exception_handler)
    if time_exec:
        print("--- Execution time: {:.2f} seconds ---".format(time.time() - start_time))


# Execution:
if __name__ == "__main__":

    main()
