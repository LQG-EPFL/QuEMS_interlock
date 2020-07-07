# Install Interlock

# Setup on rpi



## Setup internet in our lab :

this is used to connect to the epfl intranet/internet through the USB network card

```bash
sudo nano /etc/dhcpcd.conf
	interface eth1
	metric 102 #highest priority
	interface eth1
	static ip_adress=128.178.76.78/24 #/24 defines the subnet mask as 255.255.255.0
	static routers=128.178.76.1
	static domain_name_servers=128.178.15.7
#save and exit
sudo systemctl daemon-reload
sudo systemctl restart dhcpcd
```



make sure that the rpi has a connection to the internet during the following steps:

## install remi
```bash
git clone https://github.com/dddomodossola/remi
cd remi
sudo python3 setup.py install
cd ..
```

### install influxdb

```bash
sudo pip3 install influxdb
```

### install pi-plates

enable spi as described here:
https://pi-plates.com/getting_started/

```bash
sudo pip3 install pi-plates
```

### install psutils

```bash
sudo pip3 install psutil
```

## clone QuEMS_interlock

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

## Setup of launcher on rasperry pi

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

## Touchscreen setup

If you want to use a touchscreen with the pi you can install the following:

sudo apt-get install at-spi2-core
sudo apt-get install florence



# Setup on Data server

## install docker

### download influxDB

docker pull influxdb
#make c shared drive of docker
https://stackoverflow.com/questions/56797665/error-response-from-daemon-drive-has-not-been-shared

```bash
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

## For other computers make port forwarding

```bash
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=10000 connectaddress=192.168.0.4 connectport=10000
```

Make sure that you have made all the firewall exceptions for port 3000 (influxdb), 10000 (QuEMS_interlock), 8086 (Grafana).