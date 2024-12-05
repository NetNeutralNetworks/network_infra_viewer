import json, logging, re, itertools, os, glob, xmltodict

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from pyvis.network import Network

from app.parsing.drivers.cisco import ios

from ..scripts.memgraph import execute_query

from dotenv import load_dotenv

def parse_xml_data(data):
            result = dict()
            result['device_id'] = data['NetworkDevice']['Id']
            result['ip_address'] = data['NetworkDevice']['IPAddress']
            result['hostname'] = data['NetworkDevice']['HostName']
            result['os_type'] = data['NetworkDevice']['OSType']
            result['os_version'] = data['NetworkDevice']['OSVersion']
            result['serial'] = data['NetworkDevice']['SerialNumber']
            result['model'] = data['NetworkDevice']['ModelNumber']
            result['inventoryname'] = data['NetworkDevice']['PrimaryDeviceName']
            return result

class DeviceView(BaseView):
    load_dotenv(override=True)
    config_date = os.environ.get('CSPC_FOLDER')
    
    default_view = 'main_page'
    
    

    @expose('/show/', methods=['GET'])
    @has_access
    def main_page(self):
        request_data = request.args
        hostname = request_data.get('hostname', '').upper()
        if not hostname:
            return self.render_template('single_device.html', html="")
        hostname=request_data['hostname'].upper()
        # hostname = hostname.upper()
        logging.getLogger().info('Response: %s', hostname)
        # Get devicedata to show in the details view
        q = f"""
            MATCH (d:Device)
            where d.hostname =~ "{hostname}"
            RETURN distinct d


        """
        
        device = {}
        for line in execute_query(q):
            device = line[0].properties


        q = f"""
            MATCH path=(l:Location)-[]-(d:Device)
            where d.hostname =~ "{hostname}"
            RETURN distinct l,d


        """
        
        for line in execute_query(q):
            device = line[1].properties # line[1] = device
            device['location_name'] = line[0].properties['name'] # line[0] = location
            device['latitude'] = line[0].properties['latitude']
            device['longtitude'] = line[0].properties['longtitude']

        q = f"""
            MATCH path=(l:Location)-[]-(d:Device)-[:HAS_PORT]-(p)-[:IS_CONNECTED_TO]-(lijn:Circuit)-[:IS_CONNECTED_TO]-(p2)-[:HAS_PORT]-(d2:Device)-[]-(l2:Location)
            MATCH (lijn)-[]-(f:Fiber)-[]-(s:Span)
            where d.hostname =~ "{hostname}"
            RETURN distinct l,d,p,lijn,p2,d2,l2,s


        """
        lijnen = dict()
        locations = []
        spans = []
        connections=[]
        for line in execute_query(q):
            
            location1, device1, port1, Circuit,port2, device2, location2, span = line
            hostname1 = device1.properties['hostname']
            hostname2 = device2.properties['hostname']
            connections.append([hostname1,port1.properties['name'],Circuit.properties['Circuit'],port2.properties['name'],hostname2])
            locations.append(location1.properties)
            locations.append(location2.properties)
            connection_type="Unknown"

            span = {
                'path': json.loads(span.properties.get('path', [[],])),
                'spanid': span.properties.get('span', ''),
                'capacity':span.properties['kabelcapaciteit'],
                
            }
            lijnnaam = Circuit.properties.get('Circuit')
            if lijnnaam in lijnen.keys():
                lijnen[lijnnaam]["span"].append(span)
            else:
                lijnen[lijnnaam] = {"span":[span], 'connection_type': connection_type}
            spans.append(span)

        # Filter unique locations
        done = set()
        unique_locations = []
        for location in locations:
            if location['name'] not in done:
                done.add(location['name'])
                unique_locations.append(location)

        # Filter unique paths
        connections.sort()
        connections = list(k for k,_ in itertools.groupby(connections))


        # L2 overview

        q = f"""
            MATCH path=(d:Device)-[]-(i:Interface)-[]-(i2:Interface)-[]-(d2:Device)
            where d.hostname =~ "{hostname}"
            RETURN distinct path


        """
        device_network = Network(notebook=False, cdn_resources='in_line', height='800px')
        # device_network.show_buttons()
        for path in execute_query(q):
            # logging.getLogger().info('Response: %s', path[0])
            nodes = path[0].nodes
            for node in nodes:
                if "Device" in node.labels:
                    device_network.add_node(node.id, label=node.properties.get("hostname"), color="red")
                elif "Interface" in node.labels:
                    device_network.add_node(node.id, label=node.properties.get("name"), color="orange", shape="box", mass=1)
            edges = path[0].relationships
            for edge in edges:
                device_network.add_edge(edge.start_id, edge.end_id)
        l2_html = device_network.generate_html()
        l2_html = re.sub(r'<center>.+?<\/h1>\s+<\/center>', '', l2_html, 2, re.DOTALL)
        l2_html = re.sub(r'<link\s*href.*?\/>', '', l2_html, 0, re.DOTALL)
        l2_html = re.sub(r'row no-gutter', '', l2_html, 0, re.DOTALL)


        # Get device config:
        # TODO: Optimize -> Maybe cache a list of hostnames with id's to not search through all of the files on each request
        
        path = os.path.join(f'/opt/ncubed/data/configs/CSPC_exports/{self.config_date}/Network_1/', 'DeviceList_*.xml')

        os_lookup_table = {
            'IOS': 'ios',
            'IOS-XE': 'iosxe',
            'IOS XR': 'iosxr',
            'FXOS': 'fxos',
            'NX-OS': 'nxos',
        }

        device_config = []
        for filename in glob.glob(path):
            try:
                with open(filename, 'r') as f:
                    doc = xmltodict.parse(f.read())
                    meta_data = parse_xml_data(doc)
                    if meta_data.get('hostname').upper() == request_data['hostname']:
                        logging.getLogger().info('Found config: as device: %s', meta_data['device_id'])
                        config_file_path = f'/opt/ncubed/data/configs/CSPC_exports/{self.config_date}/Network_1/' + "NetworkDevice_" + meta_data['device_id'] + "/CLI/_show running_config"
                        with open(config_file_path, 'r') as config_file:
                            device_config = config_file.readlines()

                        oc = ios.parse(source=config_file_path, platform=os_lookup_table.get(meta_data['os_type']))
                        oc_text = json.dumps(oc, indent=3)
                        break
            except:
                oc = {}
                oc_text = '''Config not found'''

        # Get network components
        q = f"""
        MATCH path=((n:Device)--(v:VRF)--(i:Interface)--(v2:Vlan)--(i2:Interface))
        WHERE n.hostname =~ '{hostname}'
        return v, i, v2, i2
        """
        vrfs = []
        try:
            for vrf_name, vrf_info in oc.get('root', {}).get('network-instances', {}).get('network-instance', {}).items():
                vrfs.append({
                    'name': vrf_name,
                    'interfaces': vrf_info.get('interfaces', {}).get('interface', {}).keys()
                })
        except:
            oc_text = '''Config not found'''
        interfaces = []
        try:
            for name, interface in oc.get('root', {}).get('interfaces',{}).items():
                interfaces.append({
                    'name': name,
                    'ip': interface.get('config', {}).get('ip'),
                    'description': interface.get('config', {}).get('description'),
                    'vrf': interface.get('config', {}).get('vrf', ''),
                    'enabled': interface.get('config', {}).get('enabled', ''),
                })
        except:
            pass
                        

        return self.render_template('single_device.html', device=device, connections=connections, markers = unique_locations, spans=spans, lines=lijnen, html=l2_html, device_config=device_config, l3=vrfs, oc=oc_text, interfaces=interfaces, config_date=self.config_date)
    

    @expose('/l2_extended/', methods=['GET'])
    @has_access
    def l2_extended(self):
        request_data = request.args
        if not request_data.get('hostname'):
            return self.render_template('single_device.html', html="")
        hostname=request_data['hostname'].upper()

         # Get devicedata to show in the details view
        q = f"""
            MATCH (d:Device)
            where d.hostname = "{request_data['hostname']}"
            RETURN distinct d


        """
        
        device = {}
        for line in execute_query(q):
            device = line[0].properties
        
        q=f"""
            MATCH (n:Device)
            WHERE n.hostname = "{hostname}"
            CALL uplink_paths.get_path(n, 200, 5) YIELD * RETURN path, uplink.hostname"""
        
        device_network = Network(notebook=False, cdn_resources='in_line', height='800px')
        for path, uplink in execute_query(q):
            for node in path.nodes:
                
                if "Device" in node.labels:
                    if node.properties["hostname"] == hostname:
                        device_network.add_node(node.id, label=node.properties.get("hostname"), color="blue")
                    else:
                        device_network.add_node(node.id, label=node.properties.get("hostname"), color="red")
                elif "Interface" in node.labels:
                    device_network.add_node(node.id, label=node.properties.get("name"), color="orange", shape="box", mass=1)
                

            edges = path.relationships
            for edge in edges:
                device_network.add_edge(edge.start_id, edge.end_id)
        l2_html = device_network.generate_html()
        l2_html = re.sub(r'<center>.+?<\/h1>\s+<\/center>', '', l2_html, 2, re.DOTALL)
        l2_html = re.sub(r'<link\s*href.*?\/>', '', l2_html, 0, re.DOTALL)
        return self.render_template('l2_extended.html', device=device, html=l2_html)
        
        
        
        



        # Get devicedata to show in the details view
        q = f"""
            MATCH (d:Device)
            where d.hostname = "{request_data['hostname']}"
            RETURN distinct d


        """
        
        device = {}
        for line in execute_query(q):
            device = line[0].properties

        # Find closest 2 CE devices
        q = f"""
            MATCH path=(d:Device)-[:HAS_INTERFACE|:HAS_NEIGHBOR*BFS..]-(d2:Device)
            WHERE d.hostname = "{hostname}" and d2.hostname =~ ".*CE.*"
            RETURN path,size(path) AS distance
            ORDER BY distance
            LIMIT 2



        """
        device_network = Network(notebook=False, cdn_resources='in_line', height='800px')
        for path in execute_query(q):
            nodes = path[0].nodes
            for node in nodes:
                if "Device" in node.labels:
                    device_network.add_node(node.id, label=node.properties.get("hostname"), color="red")
                elif "Interface" in node.labels:
                    device_network.add_node(node.id, label=node.properties.get("name"), color="orange", shape="box", mass=1)
            edges = path[0].relationships
            for edge in edges:
                device_network.add_edge(edge.start_id, edge.end_id)
        l2_html = device_network.generate_html()
        l2_html = re.sub(r'<center>.+?<\/h1>\s+<\/center>', '', l2_html, 2, re.DOTALL)
        l2_html = re.sub(r'<link\s*href.*?\/>', '', l2_html, 0, re.DOTALL)
        return self.render_template('l2_extended.html', device=device, html=l2_html)
    
    @expose('/l2_summary/', methods=['GET'])
    @has_access
    def l2_summary(self):
        request_data = request.args
        if not request_data.get('hostname'):
            return self.render_template('single_device.html', html="")
        hostname=request_data['hostname'].upper()
        q = f"""
            MATCH path=(d:Device)-[]-(i:Interface)-[]-(i2:Interface)-[]-(d2:Device)
            where d.hostname =~ "{hostname}"
            RETURN distinct d, d2;


        """
        device_network_short = Network(notebook=False, cdn_resources='in_line', height='800px')
        for node1, node2 in execute_query(q):
            for node in [node1, node2]:
                if "Device" in node.labels:
                    device_network_short.add_node(node.id, label=node.properties.get("hostname"), color="red")
            device_network_short.add_edge(node1.id, node2.id)
        l2_html_short = device_network_short.generate_html()
        l2_html_short = re.sub(r'<center>.+?<\/h1>\s+<\/center>', '', l2_html_short, 2, re.DOTALL)
        l2_html_short = re.sub(r'<link\s*href.*?\/>', '', l2_html_short, 0, re.DOTALL)
        l2_html_short = re.sub(r'row no-gutter', '', l2_html_short, 0, re.DOTALL)
        return self.render_template('l2_extended.html', device=node1, html=l2_html_short)
