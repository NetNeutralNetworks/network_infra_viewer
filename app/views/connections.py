import json
import logging
from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access
from pyvis.network import Network

from ..scripts.memgraph import execute_query

class ConnectionOverview(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        request_data = request.args
        if not request_data.get('query'):
            return self.render_template('device.html', html="")

        q = f"""
            MATCH path=(d:Device)-[]-(i:Interface)-[]-(i2:Interface)-[]-(d2:Device)
            WHERE d.hostname CONTAINS "{request_data['query']}"
            RETURN distinct path


        """
        device_network = Network(notebook=True, cdn_resources='in_line')
        # device_network.show_buttons()
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
    
    
class CustomConnectionGraph(BaseView):
    default_view = 'main_page'

    @expose('/show/', methods=['GET'])
    @has_access
    def main_page(self):
        q = f"""
            MATCH path=(d:Device)-[]-(i:Interface)-[]-(i2:Interface)-[]-(d2:Device)
            WHERE d.hostname = "UT-PAP-P5-001"
            RETURN distinct path


        """
        for path in execute_query(q):
            nodes = path[0].nodes
            for node in nodes:
                if "Device" in node.labels:
                    # Add device node
                    pass
                elif "Interface" in node.labels:
                    # Add interface node
                    pass
            edges = path[0].relationships
            for edge in edges:
                # Draw lines 
                pass
        return self.render_template('testing.html')
    
class CEInterConnect(BaseView):
    default_view = 'main_page'

    @expose('/show/', methods=['GET', 'POST'])
    @has_access
    def main_page(self):
        if request.method == 'GET':
            q = f"""
            MATCH (d:Device)
            WHERE d.hostname =~ ".*CE.*"
            RETURN DISTINCT d.hostname
            """
            devices = [x[0] for x in execute_query(q)]
            return self.render_template('interconnect_form.html', devices=devices)
        request_data = request.form
        # logging.getLogger().info(request_data)

        q = f"""
            MATCH path=(d:Device)-[:HAS_INTERFACE|:HAS_NEIGHBOR*BFS]-(d2:Device)
            WHERE d.hostname = "{request_data['device_a']}" and d2.hostname = "{request_data['device_b']}"
            RETURN path
            """
        device_network = Network(notebook=True, cdn_resources='in_line')
        for path in execute_query(q):
            # logging.getLogger().info('Response: %s', path[0])
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
                
        
        
    
    