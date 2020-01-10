Install Interlock

# install remi
https://github.com/dddomodossola/remi

pip install timeout-decorator


# install docker
## download influxDB
docker pull influxdb
docker run --name influxdb -p 8086:8086 -v "C:\Users\sauerwei\OneDrive\Projekte und Jobs\EPFL_Brantut\programs\interlock\influxdb":/var/lib/influxdb influxdb
curl http://localhost:8086/query --data-urlencode 'q=CREATE DATABASE "mydb"'

# test database
curl -i -XPOST "http://localhost:8086/write?db=mydb" --data-binary 'myvar,mytag=1 myfield=90 1549412796'


## download grafana/grafana
docker pull grafana/grafana
docker run -d --name=grafana -p 3000:3000 --link influxdb grafana/grafana
link database to http://influxdb:8086


if docker stopped it can be restarted with docker restart container