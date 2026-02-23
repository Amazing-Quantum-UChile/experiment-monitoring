#!/usr/bin/env python
# -*- mode:Python; coding: utf-8 -*-

# ----------------------------------
#  Created on the Mon Jan 12 2026 by Victor
#
#  Copyright (c) 2026 - AmazingQuantum@UChile
# ----------------------------------
#
"""
Content of down-sample.py

his script performs automatic downsampling of all measurements in an InfluxDB database.

It reads data from a high-frequency retention policy (RP) named 'downsample_weeks'
and aggregates it into a lower-frequency, long-term RP called 'mean_few-months'.

For each measurement, the script computes the mean of all fields for each 5-minutes
interval, and writes the aggregated points into the target RP.

"""

from expmonitor.utilities.database import Database
from datetime import datetime, timedelta
import logging

# Configure le système de logs
logging.basicConfig(
    filename="/root/.downsampling.log",  # where we write the logs
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Optionnel : log des infos au début
logging.info("Starting downsampling process.")


database = Database()

source_rp = "raw_2weeks"
target_rp = "mean_few-months"
interval = "5m"


end = datetime.utcnow()
start = end - timedelta(minutes=5)

start_str = start.strftime("%Y-%m-%dT%H:%M:%SZ")
end_str = end.strftime("%Y-%m-%dT%H:%M:%SZ")
# List all measurements in the database
measurements_result = database.client.query(
    'SHOW MEASUREMENTS ON "{}"'.format(database.name)
)
measurements = [m["name"] for m in measurements_result.get_points()]
for m in measurements:
    try:
        query = """SELECT mean("value") AS "value" INTO "{}"."{}"."{}" FROM "{}"."{}" WHERE time >= '{}' AND time < '{}' GROUP BY time({})""".format(
            database.name,
            target_rp,
            m,
            source_rp,
            m,
            start_str,
            end_str,
            interval,
        )
        database.client.query(query)
    except Exception as e:
        msg = f"Error occurred for measurement: {m} - {str(e)}"
        logging.error(msg)  # Log d'erreur
        print(msg)
