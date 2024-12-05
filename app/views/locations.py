import json, logging, re, itertools, os, glob, xmltodict

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from pyvis.network import Network

from ..scripts.memgraph import execute_query
from ..scripts.score_rendering import render_config_scores

class LocationView(BaseView):
    default_view = 'list_locations'

    @expose('/list/', methods=['GET'])
    @has_access
    def list_locations(self):
        # Get All vrf's to show in table view
        q = f"""
            MATCH (d:Device)--(o:ObjectGroup)
            RETURN distinct o.name, count(d), d.object_type
        """
        lines = []
        for vrf in execute_query(q):
            service, count, object_type = vrf
            lines.append(f"<a href='/locationview/show/{service}'>{service}</a></td><td>{object_type}</td><td>{count}")


        help = """
            <p>This page shows all object groups. Groups can be used to cluster devices or locations</p>
            """
        return self.render_template('single_column_table.html', table_header="Locations </td><td>Object type</td><td>#devices", entries=lines, page_info=help, page_category='Network Components')
    
    @expose('/show/<string:location>', methods=['GET'])
    @has_access
    def show_locations(self, location):
        # Get All vrf's to show in table view
        q = f"""
            MATCH (d:Device)--(o:ObjectGroup)
            WHERE o.name = '{location}'
            RETURN d
        """
        lines = []
        for device in execute_query(q):
            lines.append(f"<a href='/deviceview/show/?hostname={device[0].properties['hostname']}'>{device[0].properties['hostname']}</a>")


        help = """
            <p>This page shows a location with its devices</p>
            """
        
        location_l2_button = f"""
        <a class="btn btn-primary" href="/locationview/l2/?location={location}" style="grid-column: 2/3;">
            Show L2 overview
      </a>
        """
        return self.render_template('single_column_table.html', table_header=f"Devices located at {location}", entries=lines, page_info=help, extra_html = location_l2_button, page_category='Network Components')
    
    @expose('/l2/', methods=['GET'])
    @has_access
    def show_location_l2(self):
        request_data = request.args
        location = request_data.get('location')
        # Get All vrf's to show in table view
        q = f"""
            MATCH (d:Device)--(o:ObjectGroup)
            WHERE o.name = '{location}'
            MATCH path=((d)-[:HAS_INTERFACE]-()-[:HAS_NEIGHBOR]-()--(d2:Device))
            RETURN path
        """
        device_network = Network(notebook=False, cdn_resources='in_line', height='800px')
        # device_network.show_buttons()
        devices = {}
        for path in execute_query(q):
            # logging.getLogger().info('Response: %s', path[0])
            nodes = path[0].nodes
            for node in nodes:
                if "Device" in node.labels:
                    device_network.add_node(node.id, label=node.properties.get("hostname"), color="red")
                    devices[node.properties["hostname"]] = node.properties
                elif "Interface" in node.labels:
                    device_network.add_node(node.id, label=node.properties.get("name"), color="orange", shape="box", mass=1)
            edges = path[0].relationships
            for edge in edges:
                device_network.add_edge(edge.start_id, edge.end_id)
        l2_html = device_network.generate_html()
        l2_html = re.sub(r'<center>.+?<\/h1>\s+<\/center>', '', l2_html, 2, re.DOTALL)
        l2_html = re.sub(r'<link\s*href.*?\/>', '', l2_html, 0, re.DOTALL)
        help = """
            <p>This page shows how devices are connected within a single location</p>
            """
        device_locations = {}
        for device in devices:
            q = f"""
            MATCH (d:Device)--(l:Location)
            WHERE d.hostname = '{device}'
            RETURN l
            """
            for location in execute_query(q):
                device_locations[device] = {'latitude': location[0].properties['latitude'],'longtitude': location[0].properties['longtitude']}
        markers = []
        for device, location in device_locations.items():
            markers.append({'hostname': device, 'latitude': location['latitude'],'longtitude': location['longtitude']})
        return self.render_template('location.html',  page_info=help, html=l2_html, markers=markers, lines=[], page_category='Network Components')
    