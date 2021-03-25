# Installation

For the installation of the QuEMS_interlock, one has to install software on the raspberry pi and another computer (data server) that is used for data storage (influxDB and grafana). 

## Setup on Raspberry pi

### Install the necessary python packages

make sure that the rpi has a connection to the internet during the following steps:

#### REMI

```bash
git clone https://github.com/dddomodossola/remi
cd remi
sudo python3 setup.py install
cd ..
```

#### influxdb

```bash
sudo pip3 install influxdb
```

#### pi-plates

enable spi as described here:
https://pi-plates.com/getting_started/

```bash
sudo pip3 install pi-plates
```

#### psutils

```bash
sudo pip3 install psutil
```

### clone QuEMS_interlock

```bash
git clone https://c4science.ch/source/QuEMS_interlock.git
```

Adjust the code in interlock.py to fit your configuration of influxdb:

```python
dbClient = InfluxDBClient('192.168.0.1', 8086, 'root', 'root', 'mydb', timeout = 0.1) 
```

Adjust the main.py for your needs. This means connect you devices and configure the correct folders for configs and values.

place your old config files in 

```
./QuEMS_interlock/config
```

test the interlock by running

```bash
python3 main.py
```

### Setup of launcher on rasperry pi

```bash
mkdir ./logs
```


Add the following line to crontab -e:

```
@reboot sh /home/pi/QuEMS_interlock/launch_interlock.sh >/home/pi/logs/cronlog 2>&1
```

To state the pi in kiosk mode add:

```
@chromium-browser --start-fullscreen http://localhost:10000
```

to /etc/xdg/lxsession/LXDE-pi/autostart

### Touchscreen setup

If you want to use a touchscreen with the pi you can install the following:

sudo apt-get install at-spi2-core
sudo apt-get install florence



## Setup on data server

install docker from https://www.docker.com/

### download influxDB

make c shared drive of docker
https://stackoverflow.com/questions/56797665/error-response-from-daemon-drive-has-not-been-shared

```bash
docker pull influxdb
docker run -d --name=influxdb -p 8086:8086 --volume "C:/Users/admin/influxdb:/var/lib/influxdb" influxdb
curl http://localhost:8086/query --data-urlencode 'q=CREATE DATABASE "mydb"'
```

### test database

```bash
curl -i -XPOST "http://localhost:8086/write?db=mydb" --data-binary 'myvar,mytag=1 myfield=90 1549412796'
```

### download grafana/grafana

```bash
docker pull grafana/grafana
docker run -d --name=grafana -p 3000:3000 --volume "C:/Users/admin/graphana:/var/lib/grafana" --link influxdb grafana/grafana
link database to http://influxdb:8086 and set database name to mydb
```

if docker stopped it can be restarted with docker restart container

!!! warning
	Make sure that you have made all the firewall exceptions for port 3000 (influxdb), 10000 (QuEMS_interlock), 8086 (Grafana).

## For other computers make port forwarding

```bash
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=10000 connectaddress=192.168.0.4 connectport=10000
```



