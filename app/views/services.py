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
            RETURN distinct v.name, count(d)
        """
        lines = []
        for vrf in execute_query(q):
            service, count = vrf
            lines.append(f"<a href='/serviceview/show/{service}'>{service}</a></td><td>{count}")


        help = """
            <p>This page shows all VRF's within the network. Each VRF is unique to a device.</p>
            """
        return self.render_template('single_column_table.html', table_header="Service</td><td>#Devices", entries=lines, page_info=help, page_category='Network Components')
    
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
            lines.append(f"<a href='/deviceview/show/?hostname={device.properties['hostname']}'>{device.properties['hostname']}</a>")
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
            """
        return self.render_template('single_column_table_with_map.html', table_header=f"Devices with {vpn} configured", entries=lines, page_info=help, markers=markers, page_category='Network Components')
    