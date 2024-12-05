# Installation
`docker compose up`

# Conecting to memgraph
edit/create `.env` file  

```
# URL used for connecting to Memgraph DB
MEMGRAPH_HOST=
# Port used for connecting to Memgraph DB (default=7687)
MEMGRAPH_PORT=
# Secret key used to hash/encrypt cookies for the frondend
APP_SECRET_KEY=
# IP the webserver is listening on (0.0.0.0 listens on all ip addresses)
WEBSERVER_LISTEN_IP=
# Port the webserver is exposed on
WEBSERVER_PORT=
# Shows stacktraces etc in webui
DEBUG_MODE=
```

# Local files
`./config.py`  
used for config of appbuilder (contains authentication/db connections); Gets mounted to /var/appbuilder/config.py  

`ncubed_flask_base`  
used to store local db; Gets mounted to /var/lib/appbuilder/data  

`/opt/ncubed/data/configs/CSPC_exports/`  
used to access cscp data; Gets mounted to /opt/ncubed/data/configs/CSPC_exports/ as readonly  
Expects a date as foldername with a Network_1 folder inside ('/opt/ncubed/data/configs/CSPC_exports/20230301/Network_1')

`/opt/ncubed/data/configs/CSPC_exports/oc`  
used to access OpenConfig data; Gets mounted to /opt/ncubed/data/configs/CSPC_exports/oc as read+write  

# Building in MicroK8s
This container image is not yet published in a container registry, so in order to use the image in MicroK8s run the following commands:
```
sudo docker build -t docker.io/library/network-infra-viewer:latest .
sudo docker save network-infra-viewer > nivr.tar
microk8s ctr image import nivr.tar
```
