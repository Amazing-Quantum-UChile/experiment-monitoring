#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 10:03:16 2021

@author: jp, victor

Exception handling module for the experiment monitoring suite.

We change it by using the logging librairy (02/03/2026)
"""

# Standard library imports:
import os, logging
class InfluxDBHandler(logging.Handler):
    
    def __init__(self, database):
        super().__init__()
        self.database = database

    def emit(self, record):
        log_msg = self.format(record)
        
        self.database.store_log(log_msg, record.levelname, unique_id = str(record.created))



def setup_logging(
    name,
    verbose,
    database_obj,
    log_format,
    log_level=logging.WARNING,
    log_dir=os.path.join(os.path.expanduser("~"), ".expmonitor"),
    overwrite_log_file=True
):
    # the logger name must be the same accross all files
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    # 1. Store error in the log file
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    if overwrite_log_file:
        mode='w'
    else: 
        mode = "a"
    file_handler = logging.FileHandler(os.path.join(log_dir, "logs.txt"), mode = mode)
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
