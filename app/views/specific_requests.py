import json
import logging, os, re, csv, traceback, glob, xmltodict
from dotenv import load_dotenv
from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access
from pyvis.network import Network


from app.parsing.drivers.cisco import ios

from ..scripts.memgraph import execute_query
from ..scripts.location_calculations import get_GPS_from_RD, get_closest_point

load_dotenv(override=True)
config_date = os.environ.get('CSPC_FOLDER')

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

class CVRFibers(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        q_lines = f"""
    MATCH (l:RWS_object)--(d:Device)--(:Port)--(lijn:Lijnbenaming)--(:Fiber)--(s:Span)
    WHERE l.name =~ ".*(CVR|VOR).*"
    return DISTINCT s


        """
        spans = []
        for entry in execute_query(q_lines):
            span = entry[0]
            spans.append({
                'span': span.properties['span'],
                'path': json.loads(span.properties['path']),
            })
        q_devices = f"""
MATCH (l:RWS_object)--(d:Device)--(loc:Location)
WHERE l.name =~ ".*(CVR|VOR).*"
return DISTINCT l, d, loc


        """
        devices = []
        for entry in execute_query(q_devices):
            cvr, device, location = entry
            devices.append({
                'name': f"{cvr.properties['name']}: {device.properties['hostname']}",
                'latitude': location.properties['latitude'],
                'longtitude': location.properties['longtitude'],
            })
                
        help = """
        <p>This page shows a map of all the fibers that are connected to any CVR object. This is a report requested by Rob de Ruiter</p>
        """
        return self.render_template('generic_map.html', lines=spans, markers=devices, page_info=help, color_strategy="single")
    
class WKSImport(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET', 'POST'])
    @has_access
    def main_page(self):
        help = """
        <p>This page shows a map of all the fibers that are connected to any CVR object. This is a report requested by Rob de Ruiter</p>
        """
        if request.method == 'POST':
        # upload file flask
            q_locations = f"""
MATCH (loc:Location)
return DISTINCT loc

            """
            locations = []
            for entry in execute_query(q_locations):
                location = entry[0]
                locations.append({
                    'name': location.properties['name'],
                    'latitude': location.properties['latitude'],
                    'longtitude': location.properties['longtitude'],
                })

            nodes = []
            f = request.files.get('file')
            f.save('WKS_nodes.csv')
            with open('WKS_nodes.csv', 'r') as file:
                reader = csv.DictReader(file)
                for line in reader:
                    if line.get("name") and line.get("RDx") and line.get("RDy"):
                        try:
                            lat, lon = get_GPS_from_RD(line['RDx'], line['RDy'])
                            logging.getLogger().info(f"""{lat} : {lon}""")
                            closest_location, distance = get_closest_point((lat,lon), locations)
                            logging.getLogger().info(f"""{line.get('name')} -> {closest_location} = {distance}""")
                            nodes.append({
                                'name': line['name'],
                                'latitude': lat,
                                'longtitude': lon,
                                'distance': distance,
                            })
                        except Exception as e:
                            logging.getLogger().info(f"{e} -> {traceback.format_exc()}")
                            pass
            q_lines = f"""
        MATCH (s:Span)
        return DISTINCT s


            """
            spans = []
            for entry in execute_query(q_lines):
                span = entry[0]
                spans.append({
                    'span': span.properties['span'],
                    'path': json.loads(span.properties['path']),
                })

        
            return self.render_template('WKS.html', lines=spans, markers=nodes, page_info=help, color_strategy="single")

        q_lines = f"""
    MATCH (l:RWS_object)--(d:Device)--(:Port)--(lijn:Lijnbenaming)--(:Fiber)--(s:Span)
    WHERE l.name =~ ".*(CVR|VOR).*"
    return DISTINCT s


        """
        spans = []
        for entry in execute_query(q_lines):
            span = entry[0]
            spans.append({
                'span': span.properties['span'],
                'path': json.loads(span.properties['path']),
            })
        q_devices = f"""
MATCH (l:RWS_object)--(d:Device)--(loc:Location)
WHERE l.name =~ ".*(CVR|VOR).*"
return DISTINCT l, d, loc


        """
        devices = []
        for entry in execute_query(q_devices):
            cvr, device, location = entry
            devices.append({
                'name': f"{cvr.properties['name']}: {device.properties['hostname']}",
                'latitude': location.properties['latitude'],
                'longtitude': location.properties['longtitude'],
            })
                
        
        return self.render_template('WKS.html', lines=spans, markers=devices, page_info=help, color_strategy="single")
    
class InterfacesDevices(BaseView):
    default_view = 'main_page'

    @expose('/refresh', methods=['GET'])
    @has_access
    def refresh(self):
        entries = []
        
        path = os.path.join(f'/opt/ncubed/data/configs/CSPC_exports/{config_date}/Network_1/', 'DeviceList_*.xml')

        os_lookup_table = {
            'IOS': 'ios',
            'IOS-XE': 'iosxe',
            'IOS XR': 'iosxr',
            'FXOS': 'fxos',
            'NX-OS': 'nxos',
        }
        for filename in glob.glob(path):
            try:
                with open(filename, 'r') as f:
                    doc = xmltodict.parse(f.read())
                    meta_data = parse_xml_data(doc)
                    config_file_path = f'/opt/ncubed/data/configs/CSPC_exports/{config_date}/Network_1/' + "NetworkDevice_" + meta_data['device_id'] + "/CLI/_show running_config"
                        # logging.getLogger().info('conf lines = %s', len(device_config))
                    oc = ios.parse(source=config_file_path, platform=os_lookup_table.get(meta_data['os_type']))
                    hostname = oc.get('root', {}).get('system', {}).get('config', {}).get('hostname')
                    logging.getLogger().info(f'parsed: {hostname}')
                    if hostname:
                        with open(f'/opt/ncubed/data/configs/CSPC_exports/oc/{hostname}.oc', 'w') as oc_file:
                            json.dump(oc, oc_file)
                        for interface in oc.get('root', {}).get('interfaces', []):
                            if 'Cellular' in interface.get('name', '') or 'Cellular' in interface.get('config', {}).get('name', ''): 
                                entries.append(f"{hostname}</td><td>{interface.get('name') or interface.get('config', {}).get('name', '')}</td><td>{interface.get('config', {}).get('vrf')}")
            except Exception as e:
                entries.append(f"{meta_data['hostname']}</td><td>Error parsing</td><td>Error parsing")
                logging.getLogger().warning(f'error parsing: {filename} -> {e}')

    @expose('/list', methods=['GET'])
    @has_access
    def main_page(self):
        request_data = request.args
        entries = []
        
        path = os.path.join(f'/opt/ncubed/data/configs/CSPC_exports/{config_date}/Network_1/', 'DeviceList_*.xml')

        os_lookup_table = {
            'IOS': 'ios',
            'IOS-XE': 'iosxe',
            'IOS XR': 'iosxr',
            'FXOS': 'fxos',
            'NX-OS': 'nxos',
        }
        
        for filename in glob.glob('/opt/ncubed/data/configs/CSPC_exports/oc/*.oc'):
            try:
                with open(filename, 'r') as f:
                    oc = json.load(f)
                    hostname = oc.get('root', {}).get('system', {}).get('config', {}).get('hostname')
                    for interface in oc.get('root', {}).get('interfaces', []):
                        if isinstance(interface, str):
                            interface = oc.get('root', {}).get('interfaces', {}).get(interface, {})
                        if request_data.get('type', '') == 'cellular':
                            if 'Cellular' in interface.get('name', '') or 'Cellular' in interface.get('config', {}).get('name', ''): 
                                entries.append(f"{hostname}</td><td>{interface.get('name') or interface.get('config', {}).get('name', '')}</td><td>{interface.get('config', {}).get('vrf')}")
                        else:
                            if interface.get('config', {}).get('enabled'):
                                entries.append(f"{hostname}</td><td>{interface.get('name') or interface.get('config', {}).get('name', '')}</td><td>{interface.get('config', {}).get('vrf')}</td><td>{interface.get('config', {}).get('description')}")
            except Exception as e:
                entries.append(f"{hostname}</td><td>Error parsing</td><td>Error parsing")
                logging.getLogger().warning(f'error parsing: {filename} -> {e}')
        info = """
        <p>
        In this view you can see all the devices which have cellular interfaces and their configured VRF.
        </p>
        <p>This data is created from CSPC configs</p>
        """   
        return self.render_template('single_column_table.html', table_header="Hostname</td><td>Interface</td><td>VRF</td><td>Description", entries=entries, page_info=info)
    
class WirelessUplinks(BaseView):
    default_view = 'main_page'

    @expose('/list', methods=['GET'])
    @has_access
    def main_page(self):
        request_data = request.args
        entries = []

        device_query = f"""
        MATCH (d:Device)
        return DISTINCT d
        """
        devices = {}
        for device in execute_query(device_query):
            devices[device[0].properties['hostname']] = device[0].properties
        
        for filename in glob.glob('/opt/ncubed/data/configs/CSPC_exports/oc/*.oc'):
            try:
                with open(filename, 'r') as f:
                    oc = json.load(f)
                    hostname = oc.get('root', {}).get('system', {}).get('config', {}).get('hostname')
                    interfaces = []
                    isWirelessDevice = False
                    for interface in oc.get('root', {}).get('interfaces', []):
                        if isinstance(interface, str):
                            interface = oc.get('root', {}).get('interfaces', {}).get(interface, {})
                        if 'Cellular' in interface.get('name', '') or 'Cellular' in interface.get('config', {}).get('name', ''): 
                            isWirelessDevice = True
                            interfaces.append(f"{hostname}</td><td>{devices.get(hostname, {}).get('hardware', 'Unknown')}</td><td>{interface.get('name') or interface.get('config', {}).get('name', '')}</td><td>{interface.get('config', {}).get('vrf')}</td><td>{interface.get('config', {}).get('description')}")
                        elif interface.get('config', {}).get('enabled'):
                            interfaces.append(f"{hostname}</td><td>{devices.get(hostname, {}).get('hardware', 'Unknown')}</td><td>{interface.get('name') or interface.get('config', {}).get('name', '')}</td><td>{interface.get('config', {}).get('vrf')}</td><td>{interface.get('config', {}).get('description')}")
                    if isWirelessDevice:
                        entries += interfaces
            except Exception as e:
                entries.append(f"{hostname}</td><td>Error parsing</td><td>Error parsing")
                logging.getLogger().warning(f'error parsing: {filename} -> {e}')
        info = """
        <p>
        In this view you can see all the devices which have cellular interfaces and their configured VRF.
        </p>
        <p>This data is created from CSPC configs</p>
        """   
        return self.render_template('single_column_table.html', table_header="Hostname</td><td>Hardware</td><td>Interface</td><td>VRF</td><td>Description", entries=entries, page_info=info)


class DevicesSerial(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        entries = []
        
        path = os.path.join('/opt/ncubed/data/configs/CSPC_exports/20230301/Network_1/', 'DeviceList_*.xml')

        for filename in glob.glob(path):
            try:
                with open(filename, 'r') as f:
                    doc = xmltodict.parse(f.read())
                    meta_data = parse_xml_data(doc)
                    entries.append(f"{meta_data.get('hostname')}</td><td>{meta_data.get('serial')}")
            except Exception as e:
                logging.getLogger().warning(f'error parsing: {filename} -> {e}')
                
        info = """
        <p>
        In this view you can see all the devices and serial numbers that are collected by the CSPC collector.
        </p>
        <p>This data is created from CSPC configs</p>
        """   
        return self.render_template('single_column_table.html', table_header="Hostname</td><td>Serial", entries=entries, page_info=info)
    
class RegexTest(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        entries = ['test</td><td>test 2',
                   'testing</td><td>test 2',
                   'test</td><td>test 3',
                   'test</td><td>test 4',
                   'test</td><td>test 12']
        return self.render_template('table_test.html', table_header="Column A</td><td>Column B", entries=entries, page_info='')
    