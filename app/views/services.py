import json, logging, re, itertools, os, glob, xmltodict

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from pyvis.network import Network

from ..scripts.memgraph import execute_query
from ..scripts.score_rendering import render_config_scores

class ServiceView(BaseView):
    default_view = 'list_services'

    @expose('/list/', methods=['GET'])
    @has_access
    def list_services(self):
        # Get All vrf's to show in table view
        q = f"""
            MATCH (d:Device)--(v:VRF)
            RETURN distinct v.name, avg(d.security_score), avg(d.reliability_score), avg(d.management_score), count(d)
        """
        lines = []
        for vrf in execute_query(q):
            service, security, reliability, management, count = vrf
            security, reliability, management = render_config_scores(security, reliability, management)
            lines.append(f"<a href='/serviceview/show/{service}'>{service}</a></td><td>{count}</td><td>{security}</td><td>{reliability}</td><td>{management}")


        help = """
            <p>This page shows all VRF's within the network of RWS. Each VRF is unique to a device, but the design principles dictate that if two names of VRF are equal they should be connected.</p>
            <p>This data is provided by the CSPC collector.</p>
            """
        return self.render_template('single_column_table.html', table_header="Service</td><td>#Devices</td><td>Average security</td><td>Average reliabilty</td><td>Average management", entries=lines, page_info=help, page_category='Network Components', page='Services')
    
    @expose('/show/<string:vpn>', methods=['GET'])
    @has_access
    def show_service(self, vpn):
        # Get All vrf's to show in table view
        q = f"""
            MATCH (d:Device)--(v:VRF)
            WHERE v.name = '{vpn}'
            OPTIONAL MATCH (d)--(l:Location)
            RETURN d, l
        """
        lines = []
        markers = []
        for device, location in execute_query(q):
            security, reliability, management = render_config_scores(device.properties['security_score'], device.properties['reliability_score'], device.properties['management_score'])
            lines.append(f"<a href='/deviceview/show/?hostname={device.properties['hostname']}'>{device.properties['hostname']}</a></td><td>{security}</td><td>{reliability}</td><td>{management}")
            try:
                marker = {
                'lat':location.properties['latitude'],
                'lon':location.properties['longtitude'],
                'popup':device.properties['name']
                }
                markers.append(marker)
            except:
                pass


        help = """
            <p>This page shows a VPN with its connected components</p>
            <p>This data is provided by the CSPC collector.</p>
            """
        return self.render_template('single_column_table_with_map.html', table_header=f"Devices with {vpn} configured</td><td>Security</td><td>Reliabilty</td><td>Management", entries=lines, page_info=help, markers=markers, page_category='Network Components', page='Services')
    