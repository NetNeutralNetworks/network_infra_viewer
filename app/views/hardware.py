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
            RETURN distinct d.hardware, count(d)
        """
        lines = []
        for vrf in execute_query(q):
            service, count = vrf
            lines.append(f"<a href='/hardwareview/show/{service}'>{service}</a></td><td>{count}")


        help = """
            <p>This page shows all different hardwares.</p>
            """
        return self.render_template('single_column_table.html', table_header="hardware</td><td>#Devices", entries=lines, page_info=help, page_category='Network Components')
    
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
            lines.append(f"<a href='/deviceview/show/?hostname={device[0].properties['hostname']}'>{device[0].properties['hostname']}</a>")


        help = """
            <p>This page shows a hardware model with its devices</p>
            """
        return self.render_template('single_column_table.html', table_header=f"Devices with model {hardware}", entries=lines, page_info=help, page_category='Network Components')
    