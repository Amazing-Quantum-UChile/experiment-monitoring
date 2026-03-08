# 1. Introduction to Experiment Monitoring Server Setup
We explain how we set up the server on a SBC4 computer (like a Raspberry but from Phidgets company). It is possible to use a old linux computer to do that (and it can be better to also monitor the data in the lab and not view it from an other computer). Not that in most commands below, the sudo word is missing because the SBC4 has a minimal Debian OS (usr is sudo by default).

Note that the installation can also follow the [original one given here but made for the Paris-Saclay University](server_setup_iogs.md).

# 2. Install Python dependencies
I first update `apt update` but the version is old so it does not really work. I will not be able to install the newest Grafana version (we will thus work with Grafana 1.8). 
Not that the following packages should be installed: 
```
apt-get install -y python3 python3-pip python3-dev gcc make libusb-1.0-0-dev libatlas-base-dev libopenjp2-7 libtiff5 libsnmp-dev snmp-mibs-downloader
```
but they were already installed on my minimal Debian computer. I thus only install the following ones
```
apt-get install python3-pip libusb-1.0-0-dev libatlas-base-dev libopenjp2-7 libtiff5 libsnmp-dev snmp-mibs-downloader
```
I then install git and configure it:
```
apt install git
git config --global user.email "_you_@_example.com_"
git config --global user.name "_Your Name_"
```

# 3. Installing Influx dB
We now aim to install InfluxdB to store data. Because our architecture is old, we do not follow the current [documentation](https://docs.influxdata.com/influxdb/v1/introduction/install/?dl=oss&code_lang=sh&code_lines=6&has_placeholders=true&code_type=code&section=Installing%2520InfluxDB%2520OSS&first_line=%2523%2520influxdata-archive.key%2520GPG%2520fingerprint%253A) but we download another version for our Debian 11.7 with armv7l architecture (ARM 32-bit). 
We need to install curl : `apt-get install -y curl libc6 libssl1.1 libpcre3`.
and then download and install influxdb.
```
# Creater temporary folder
mkdir tmp && cd /tmp
# Download 
wget https://dl.influxdata.com/influxdb/releases/influxdb_1.8.10_armhf.deb
# Install 
dpkg -i influxdb_1.8.10_armhf.deb
```
Configure influxDB to start during the boot
```
systemctl enable influxdb
```
This command makes sure that Grafana is always turned on even after a reboot of the SBC4 computer. Check up that InfluxDB works:
```
systemctl start influxdb
influx --version
```

# 4. Installing Grafana
Here again we do not strictly follow [Grafana's web page installation procedure](https://grafana.com/docs/grafana/latest/setup-grafana/installation/debian/) but rather download directly the package.
```
cd /tmp
wget https://dl.grafana.com/oss/release/grafana_8.5.27_armhf.deb
```
Here what we obtain 
```
Adding system user `grafana' (UID 113) ...
Adding new user `grafana' (UID 113) with group `grafana' ...
Not creating home directory `/usr/share/grafana'.
### NOT starting on installation, please execute the following statements to configure grafana to start automatically using systemd
 sudo /bin/systemctl daemon-reload
 sudo /bin/systemctl enable grafana-server
### You can start grafana-server by executing
 sudo /bin/systemctl start grafana-server
```
Configure Grafana to disable alpha for panels in the Grafana settings file
If set to true Grafana will allow script tags in text panels. Not recommended as it enable XSS vulnerabilities.
```
sed -i '/^\[panels\]/a enable_alpha = false' /etc/grafana/grafana.ini
```
We now configure Grafana to start automatically (in case the SBC4 switched off) following the recommandation of the software. 
```
systemctl daemon-reload
systemctl enable grafana-server
```
Note that depending on your computer, you might want to store data on a USB card rather than directly on the memory available on your computer. 

# 5. Install Experiment Monitoring
**Clone** – We clone the git repository of the [code](https://github.com/Amazing-Quantum-UChile/experiment-monitoring) (I put it in the home folder)
```
git clone https://github.com/Amazing-Quantum-UChile/experiment-monitoring.git
```
You can check all branches by doing `git branch -r` and create new branch from a remote branch using `git checkout -b branch2 origin/branch2`. 
Note that I modify stuffs on my computer, pushes, then pull with the SBC4 to check if it works.

--> Note that it might be better to do the installation of the package within a python environment. 

**Add Python Path** – I cloned the project directly in the home directory, which is /root/ in the SBC4 computer. We thus add this path to the python path in the `.bashrc` file.
```
echo -e '\n# Add location of Experiment Monitoring package to PYTHONPATH:\nexport PYTHONPATH="${PYTHONPATH}:/root/experiment-monitoring/src/"' >> /root/.bashrc
```

If you look at you `.bashrc` file doing `cat /root/.bashrc`, it should contain
```
# Add location of Experiment Monitoring package to PYTHONPATH:
export PYTHONPATH="${PYTHONPATH}:/root/experiment-monitoring/src/"
```

Install the required package 
```
pip3 install -r experiment-monitoring
```
This stage can take a lot of time (hours) because the SBC4 is slow to compile python packages.
Note that I added a few difficulties here because they were issues in the compatibility.
# 6. Setting up the InfluxDB database and the code
We create the database that we name `amazQdatabase`. 
```
influx -execute 'CREATE DATABASE 'amazQdatabase''
```

You chan check that this database is created executing `influx -execute 'SHOW DATABASES'`
```
root@phidgetsbc:~# influx -execute 'SHOW DATABASES'
name: databases
name
----
_internal
amazQdatabase
```
We will use this name when instantiating the Databse object in  
experiment-monitoring/src/expmonitor/config.py 
```
database = Database(port=8086, name="amazQdatabase")
```

# 7. Check that it works and setting up the service
We now check if the code work. We need to adapt the configuration file. If no hardware is plugged, you should lunch dummy sensors. With Phidgets for example, this is achieved passing the argument is_dummy= True when instanciating the object in the config.py file. Rather than doing a measurement, the sensor will return a random number between 20 and 30.
```
# config.py file
tc0 = PhidgetTC(
    hub_serial=622701,
    hub_port=0,
    hub_channel=0,
    database=database,
    descr="temp_k_table_rb_vapor",
    location="Optical table, optics near the science Rb Cell",
    is_dummy=True
)
```
We will tell the database to do 1 measurement
```
python3 experiment-monitoring/src/expmonitor/exec.py 1
```
You should see `Iteration 1 / 1` ! It means it work, congrats!! Note that if you run the code without a "1" after the command, you will continuously acquire data (infinite loop). 

Now we set up the service i.e. the commands which automatically runs the code when the device is switched on and off. We copy and paste the service file (make sure the path do agree in the service)
```
cp /root/experiment-monitoring/server_setup/expmonitor.service /lib/systemd/system/
```
Allow to read and execute the sript
```
chmod 644 /lib/systemd/system/expmonitor.service
chmod +x /root/experiment-monitoring/src/expmonitor/exec.py
```
and reload the systemd to take into account the new service
```
systemctl daemon-reload
```
We now start the service
```
systemctl start expmonitor.service
```
and set up the service so that it turns on at all boot of the system
```
systemctl enable expmonitor.service
```

You can check if the service is on or off doing `systemctl status expmonitor.service` (and press "q" to quit the editor 'less').

# 8. Setting up Grafana
We want now to access the database.  On a local network, we should get directly access the grafana interface entering the ip address in firefox http://172.17.55.144/3000 (grafana is onbut I failed for now (because of the network of the FCFM I guess). The solution is to redirect our computer local port to the one of the SBC4:
```
ssh -L 3000:localhost:3000 root@172.17.55.144
```
and then open up ` http://localhost:3000/`in a web browser. The default usr and pwd is `admin` and you can choose a new password. 
You then need to configure your Grafana configuration. 

# 9. Down sampling
We currently store one data point per sensor every 3 seconds. Depending on the number of sensors, the database can grow very large, while the SBC4 computer only has approx. ten  gigabytes of disk space. The idea is to keep the 3-second data in memory for only 15 days (`raw_2weeks`), and to keep 5-minute averaged data for 6 months (`mean_few-months`).

To do so, we set up a retention policy which define how long data is kept in the database. The retention policy is an automatic delete rule to prevent the database to grow too much. Each retention policy is defined by a name and a duration. In our case, we keep raw data for 15 days and keep averaged data for 6 months.
To know the disk space used by each retention policy, enter 
```
du -sh /var/lib/influxdb/data/amazQdatabase/*
```

**Setting up retention policy rules** –  To set up the retention policy rule, connect to `influx` and checkout if the database appears `SHOW DATABASES;`. Here is what you should see:
```
root@phidgetsbc:~# influx
> SHOW DATABASES;
name: databases
name
----
_internal
amazQdatabase
```
We first create the retention policy for the high-frequency short period database
```
CREATE RETENTION POLICY "raw_2weeks" ON "amazQdatabase" DURATION 15d REPLICATION 1 DEFAULT
```
We now create a second low-frequency long-term retention policy
```
CREATE RETENTION POLICY "mean_few-months" ON "amazQdatabase" DURATION 26w REPLICATION 1
```

**Setting up the automatic down-sampling** –  we finally need to compute the mean of each sensor every 5 minutes and fill it into the `mean_few-months` repository policy. (Note: in InfluxDB 2.xx, downsampling is handled in a must better way with *tasks* and *buckets* but our hardware does not allow the use of this version).  We do not use a *Continuous Query* because we would need to have one query per sensor. Instead, we created a small python code `downsample.py`, located in the `src/expmonitor` folder.  It is basically the following:
```{python}
end = datetime.utcnow()
start = end - timedelta(minutes=5)
start_str = start.strftime("%Y-%m-%dT%H:%M:%SZ")
end_str = end.strftime("%Y-%m-%dT%H:%M:%SZ")
measurements_result = database.client.query('SHOW MEASUREMENTS ON "{}"'.format(database.name))
measurements = [m["name"] for m in measurements_result.get_points()]
for m in measurements:
	try:
		query = """SELECT mean("value") AS "value" INTO "{}"."{}"."{}" FROM "{}"."{}" WHERE time >= '{}' AND time < '{}' GROUP BY time({})""".format( 
		database.name, 
		target_rp,m, 
		source_rp, m, start_str, 
		end_str, interval
		)
		database.client.query(query)
		
	except Exception as e:
		msg = f"Error occurred for measurement: {m} - {str(e)}"
		logging.error(msg) # Log d'erreur
		print(msg)
```
We then add a service to run this code every 5 minutes. To do so, we use `crontab -l` and add the following line to the file 
```
*/5 * * * * python3 /root/experiment-monitoring/src/expmonitor/downsample.py
```


# And what is next?
So now, you might want to write your own (non-dummy) sensor, right??


