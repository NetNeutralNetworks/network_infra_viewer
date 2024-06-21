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
            OPTIONAL MATCH (d)-[:HAS_RWS_LOCATION]-(l2:RWS_object)
            RETURN d, l, l2

        """
        devices=[]
        for device in execute_query(q):
            hostname = ""
            location = ""
            rws_location = ""
            if device[0]:
                hostname = device[0].properties.get('hostname')
            if device[1]:
                location = device[1].properties.get('name')
            if device[2]:
                rws_location = device[2].properties.get('name')
            device = {
            'device':hostname,
            'location':location,
            'rws_location':rws_location,
            }
            devices.append(device)
        
        return self.render_template('devices.html',devices=devices)
    @expose('/list/', methods=['GET'])
    @has_access
    def list_devices(self):
        
        q = f"""
            MATCH (d:Device)
            RETURN d.hostname

        """
        
        return execute_query(q) 
    
        #     q = f"""
        #     MATCH (i:Interface)
        #     return DISTINCT i.name


        # """
        # results = execute_query(q)
        # new_results = []
        # for result in results:
        #     logging.getLogger().info(result[0])
        #     new_results.append(convert(result[0]))
        # return new_results