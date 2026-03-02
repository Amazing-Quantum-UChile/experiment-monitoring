#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 10:03:16 2021

@author: jp, victor

Exception handling module for the experiment monitoring suite.

We change it by using the logging librairy (02/03/2026)
"""
from pathlib import Path
# Standard library imports:
import logging
class InfluxDBHandler(logging.Handler):
    
    def __init__(self, database):
        super().__init__()
        self.database = database

    def emit(self, record):
        log_msg = self.format(record)
        self.database.store_log(log_msg)
