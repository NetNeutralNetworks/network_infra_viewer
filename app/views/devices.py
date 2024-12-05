import json

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from ..scripts.memgraph import execute_query

class DevicesOverview(BaseView):
    default_view = 'main_page'

    @expose('/show_all/', methods=['GET'])
    @has_access
    def main_page(self):
        
        q = f"""
            MATCH (d:Device)
            WHERE d.hostname != ""
            OPTIONAL MATCH (d)-[:IS_LOCATED_AT]-(l:Location)
            OPTIONAL MATCH (d)-[:BELONGS_TO_GROUP]-(l2:ObjectGroup)
            RETURN d, l, l2

        """
        devices=[]
        for device in execute_query(q):
            hostname = ""
            location = ""
            object_group = ""
            if device[0]:
                hostname = device[0].properties.get('hostname')
            if device[1]:
                location = device[1].properties.get('name')
            if device[2]:
                object_group = device[2].properties.get('name')
            device = {
            'device':hostname,
            'location':location,
            'object_group':object_group,
            }
            devices.append(device)
        
        return self.render_template('devices.html',devices=devices, page_category='Network Components')
    @expose('/list/', methods=['GET'])
    @has_access
    def list_devices(self):
        
        q = f"""
            MATCH (d:Device)
            RETURN d.hostname

        """
        
        return execute_query(q) 