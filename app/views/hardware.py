import json, logging, re, itertools, os, glob, xmltodict

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from pyvis.network import Network

from ..scripts.memgraph import execute_query
from ..scripts.score_rendering import render_config_scores

class HardwareView(BaseView):
    default_view = 'list_hardware'

    @expose('/list/', methods=['GET'])
    @has_access
    def list_hardware(self):
        # Get All vrf's to show in table view
        q = f"""
            MATCH (d:Device)
            RETURN distinct d.hardware, avg(d.security_score), avg(d.reliability_score), avg(d.management_score), count(d)
        """
        lines = []
        for vrf in execute_query(q):
            service, security, reliability, management, count = vrf
            security, reliability, management = render_config_scores(security, reliability, management)
            lines.append(f"<a href='/hardwareview/show/{service}'>{service}</a></td><td>{count}</td><td>{security}</td><td>{reliability}</td><td>{management}")


        help = """
            <p>This page shows all RWS hardware.</p>
            <p>This data is provided by the TOPdesk export.</p>
            """
        return self.render_template('single_column_table.html', table_header="hardware</td><td>#Devices</td><td>Average security</td><td>Average reliabilty</td><td>Average management", entries=lines, page_info=help)
    
    @expose('/show/<string:hardware>', methods=['GET'])
    @has_access
    def show_hardware(self, hardware):
        # Get All vrf's to show in table view
        q = f"""
            MATCH (d:Device)
            WHERE d.hardware = '{hardware}'
            RETURN d
        """
        lines = []
        for device in execute_query(q):
            security, reliability, management = render_config_scores(device[0].properties['security_score'], device[0].properties['reliability_score'], device[0].properties['management_score'])
            lines.append(f"<a href='/deviceview/show/?hostname={device[0].properties['hostname']}'>{device[0].properties['hostname']}</a></td><td>{security}</td><td>{reliability}</td><td>{management}")


        help = """
            <p>This page shows a hardware model with its devices</p>
            <p>This data is provided by TOPdesk export.</p>
            """
        return self.render_template('single_column_table.html', table_header=f"Devices with model {hardware}</td><td>Security</td><td>Reliabilty</td><td>Management", entries=lines, page_info=help)
    