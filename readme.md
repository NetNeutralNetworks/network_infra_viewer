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
