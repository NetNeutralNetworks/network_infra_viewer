import os, re, json

from ttp import ttp
from paramiko import SSHClient, AutoAddPolicy
from netmiko import ConnectHandler
from scp import SCPClient
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

###########################################################################################################
# netmiko
###########################################################################################################
def device_connection(hostname, user, password, port=22,):
    conn_info = {
                'device_type': 'hp_procurve',
                'host': hostname,
                'port': port,
                'username': user,
                'password': password,
                'secret': "",
                'fast_cli': True
                }
    
    return ConnectHandler(**conn_info)  

def backup(hostname, user, password, output):

    with device_connection(str(hostname),user, password) as net_connect:
        net_connect.enable()
        net_connect.config_mode()
        net_connect.send_command('ip ssh filetransfer')
    
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy)
        ssh.connect( hostname = hostname, 
                        username = user, 
                        password = password,
                        allow_agent=False,
                        look_for_keys=False)
        with SCPClient(ssh.get_transport()) as scp:
            scp.get('cfg/running-config', 
                    output)
            print("Config backup succesfull")
        
def backup_safe(hostname, user, password, output):
    try:
        backup(hostname, user, password, output)
    except Exception as e:
        print(e)


###########################################################################################################
# ttp parse functions
###########################################################################################################
def match_stacked_range(data, rangechar, joinchar, stackchar):
    """
    data - string, e.g. '8,1/10-1/13,20'
    rangechar - e.g. '-' for above string
    joinchar - e.g.',' for above string
    stackchar - e.g. '/'
    returns - e.g. '8,10,11,12,13,20 string
    """
    result = []
    try:
        for item in data.split(joinchar):
            if rangechar in item:
                start,end = item.split(rangechar)
                if stackchar in start:
                    start_first,start_end = start.split(stackchar)
                    end_first,end_end = end.split(stackchar)
                    for i in range(int(start_end), int(end_end)+1):
                        result.append("{}{}{}".format(start_first, stackchar, i))
                else:
                    text = re.sub("[^0-9]".format(rangechar),"",start)
                    numeric_filter_start = filter(str.isdigit, start)
                    number_start = "".join(numeric_filter_start)
                    numeric_filter_end = filter(str.isdigit, end)
                    number_end = "".join(numeric_filter_end)
                    for i in range(int(number_start), int(number_end)+1):
                        result.append(str(i))
            else:
                result.append(item)
        data = joinchar.join(result)
        return data, None
    except:
        return data, None

def parse(source, destination):
    try:
        template = Path(os.path.join(f'{BASE_DIR}/templates/procurve', 'show_run.ttp')).resolve()
        parser = ttp(data=source, template=str(template))
        parser.add_function(match_stacked_range, scope="match", name="stacked_unrange")
        parser.parse()
        results = parser.result()[0][0]
        for vlan in results.get('vlans',[]):
            if vlan.get('ip'):
                if not results.get('interfaces', None):
                    results['interfaces'] = []
                results['interfaces'].append(
                    {
                        "routed_vlan": {
                            "ipv4": {
                                "addresses": {
                                    "ip": vlan.get('ip')
                                }
                            }
                        },
                        "config": {
                            "type": "IF_ROUTED_VLAN"
                        },
                        "name": "VLAN" + vlan.get('vlan-id'),
                        "vlan-id": vlan.get('vlan-id')
                    }
                )
        with open(destination, 'w') as f:
            f.write(json.dumps(results))
        return results
    except Exception as e:
        print(e)
        pass
