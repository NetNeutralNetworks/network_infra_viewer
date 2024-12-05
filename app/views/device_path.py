import json
import logging
from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access
from pyvis.network import Network

from ..scripts.memgraph import execute_query

class L2PathOverview(BaseView):
    default_view = 'main_page'

    @expose('/show/', methods=['GET'])
    @has_access
    def main_page(self):
        request_data = request.args
        q = f"""
            MATCH path=(n:Device)-[rel:HAS_INTERFACE|:HAS_NEIGHBOR*BFS..15]-(m:Device)
            WHERE n.hostname = "{request_data['d1']}" and m.hostname = "{request_data['d2']}"
            RETURN path

        """
        device_network = Network(notebook=True, cdn_resources='in_line')
        for path in execute_query(q):
            logging.getLogger().info('Response: %s', path[0])
            nodes = path[0].nodes
            for node in nodes:
                if "Device" in node.labels:
                    device_network.add_node(node.id, label=node.properties.get("hostname"), color="red")
                elif "Interface" in node.labels:
                    device_network.add_node(node.id, label=node.properties.get("name"), color="orange")
            edges = path[0].relationships
            for edge in edges:
                device_network.add_edge(edge.start_id, edge.end_id)
                
        
        return self.render_template('device.html', html= device_network.generate_html())
    
    
    