# Install Interlock

## install remi
https://github.com/dddomodossola/remi

pip install influxdb


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