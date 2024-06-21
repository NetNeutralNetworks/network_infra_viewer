import json
import os
import re
import traceback
from pathlib import Path

# from netmiko import ConnectHandler
# from paramiko import AutoAddPolicy, SSHClient
# from scp import SCPClient
from ttp import ttp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


###########################################################################################################
# netmiko
###########################################################################################################
# def device_connection(
#     hostname,
#     user,
#     password,
#     port=22,
# ):
#     conn_info = {
#         "device_type": "cisco_ios",
#         "host": hostname,
#         "port": port,
#         "username": user,
#         "password": password,
#         "secret": "",
#         "fast_cli": True,
#     }

#     return ConnectHandler(**conn_info)


# def backup(hostname, user, password, output):
#     try:
#         with device_connection(str(hostname), user, password) as net_connect:
#             net_connect.enable()
#             config = net_connect.send_command("show run")

#             with open(output, "w") as f:
#                 f.write(config)

#     except Exception as e:
#         print(e)


# def backup_safe(hostname, user, password, output):
#     try:
#         backup(hostname, user, password, output)
#     except Exception as e:
#         print(e)


def parse(source, destination=None, template="pre_parse_show_run.ttp", platform="ios"):
    try:
        os.environ["TTP_TEMPLATES_DIR"] = f"{BASE_DIR}/ttp_templates/{platform}"
        parser = ttp(data=source, template=str(template))

        parser.parse()

        results = parser.result()[0][0]
        # sort upper two dict layers
        results.update(dict(sorted({k:dict(sorted(v.items())) for k,v  in results.items() if isinstance(v,dict)}.items())))

        if destination:
            with open(destination, "w") as f:
                f.write(json.dumps(results))
        return results
    except Exception as e:
        traceback.print_stack()
        print(f"\n\nERROR: {e}\n\n")
