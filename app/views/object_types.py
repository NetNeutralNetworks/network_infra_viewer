import json, logging, re, itertools, os, glob, xmltodict

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from pyvis.network import Network

from ..scripts.memgraph import execute_query
from ..scripts.score_rendering import render_config_scores

class ObjectTypeView(BaseView):
    default_view = 'list_object_types'

    @expose('/list/', methods=['GET'])
    @has_access
    def list_object_types(self):
        # Get all object types (eg. bridges, locks, offices) to show in table view
        q = f"""
            MATCH (d:Device)
            RETURN distinct d.object_type, count(d)
        """
        lines = []
        for vrf in execute_query(q):
            object_type, count = vrf
            lines.append(f"<a href='/objecttypeview/show/?type={object_type}'>{object_type}</a></td><td>{object_type}</td><td>{count}")


        help = """
            <p>This page shows all Object groups</p>
            """
        return self.render_template('single_column_table.html', table_header="Locations </td><td>Object type</td><td>#devices", entries=lines, page_info=help, page_category='Network Components')
    
    @expose('/show/', methods=['GET'])
    @has_access
    def show_object_types(self):
        # Get all locations of a certain object type
        request_data = request.args
        object_type = request_data.get('type')
        q = f"""
            MATCH (d:Device)--(o:ObjectGroup)
            WHERE d.object_type = '{object_type}'
            RETURN distinct o.name, count(d)
        """
        lines = []
        for vrf in execute_query(q):
            object_name, count = vrf
            lines.append(f"<a href='/locationview/show/{object_name}'>{object_name}</a></td><td>{count}")
            
        q = f"""
            MATCH (d:Device)--(o:ObjectGroup)
            WHERE d.object_type = '{object_type}'
            OPTIONAL MATCH (d)--(l:Location)
            RETURN distinct d.hostname, o.name, l
        """
        markers = []
        for result in execute_query(q):
            hostname, object_name, location = result
            try:
                marker = {
                'lat':location.properties['latitude'],
                'lon':location.properties['longtitude'],
                'popup':f"{object_name}: {hostname}" 
                }
                markers.append(marker)
            except:
                pass



        help = """
            <p>This page shows the locations of a single object group.</p>
            """
        return self.render_template('single_column_table_with_map.html', table_header="Location</td><td>#devices", entries=lines, page_info=help, markers=markers, page_category='Network Components')
    