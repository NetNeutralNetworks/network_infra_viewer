import json, os
import logging
from collections import Counter
from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access
from pyvis.network import Network

from ..scripts.memgraph import execute_query

class CircuitMissingPort(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        
        q = f"""
            MATCH (l:Circuit)
            WHERE NOT exists((l)-[]-(:Port))
            return l.Circuit


        """
        lines = []
        for entry in execute_query(q):
            # logging.getLogger().info('Response: %s', entry[0])
            lines.append(entry[0])
            
                
        info = """
        <p>
        In this view you can see all the circuits that have been created but the connection to the device/port is unknown.
        </p>
        """   
        return self.render_template('single_column_table.html', table_header="Cicuit names without connected devices", entries=lines, page_info=info)
    
class DeviceMissingLocation(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        
        q = f"""
        OPTIONAL MATCH (d:Device)
        WHERE NOT exists((d)-[]-(:Location))
        RETURN d.hostname

        """
        devices = []
        for entry in execute_query(q):
            # logging.getLogger().info('Response: %s', entry[0])
            devices.append(entry[0])
            
        info = """
        <p>
        In this view you can see all the devices are not plotted on a location. 
        </p>
        """        
        
        return self.render_template('single_column_table.html', table_header="Devices without location (Physical)", entries=devices, page_info=info)
    
    
class DeviceMissingPort(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        
        q = f"""
        OPTIONAL MATCH (d:Device)

        WHERE NOT exists((d)-[]-(:Port)) AND NOT exists((d)-[]-(:Interface))

        RETURN d.hostname


        """
        devices = []
        for entry in execute_query(q):
            # logging.getLogger().info('Response: %s', entry[0])
            devices.append(entry[0])
            
                
        info = """
        <p>
        In this view you can see all the devices of which no port or interface is known. This means the device does not have any known neighborships and is not connected to a circuit.
        </p>
        """   
        return self.render_template('single_column_table.html', table_header="Devices without Port or Interface", entries=devices, page_info=info)
    

class NonConsecutiveLine(BaseView):
    default_view = 'main_page'
    
    

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        request_data = request.args
        cached_output_file = 'quality_non_consecutive_lines.json'
        if os.path.isfile(cached_output_file) and not request_data.get('refresh'):
            with open(cached_output_file, 'r') as outputfile:
                lines = json.loads(outputfile.read())
        else:
            q1 = f"""
            MATCH (l:Circuit)
            RETURN DISTINCT l.Circuit
            """
            lines = []
            for line in execute_query(q1):
                if line[0] == "":
                    continue
                q = f"""
                MATCH (l:Circuit)-[]-(f:Fiber)-[]-(s:Span)
                WHERE l.Circuit = "{line[0]}"

                RETURN DISTINCT s


                """
                try:
                    def count_connected_groups(connections):
                        adjacency_list = {}

                        # Build adjacency list for undirected connections
                        for connection in connections:
                            loc_a = connection["locatie_naam_a"]
                            loc_b = connection["locatie_naam_b"]

                            # Add loc_b to loc_a's neighbors
                            if loc_a not in adjacency_list:
                                adjacency_list[loc_a] = set()
                            adjacency_list[loc_a].add(loc_b)

                            # Add loc_a to loc_b's neighbors
                            if loc_b not in adjacency_list:
                                adjacency_list[loc_b] = set()
                            adjacency_list[loc_b].add(loc_a)

                        visited = set()
                        groups_count = 0

                        def dfs(node):
                            visited.add(node)
                            for neighbor in adjacency_list.get(node, []):
                                if neighbor not in visited:
                                    dfs(neighbor)

                        for locatie_naam in adjacency_list:
                            if locatie_naam not in visited:
                                dfs(locatie_naam)
                                groups_count += 1

                        return groups_count
                    connections = []
                    for span in execute_query(q):
                        connections.append(span[0].properties)
                    group_count = count_connected_groups(connections)
                    if group_count > 1:
                        lines.append(f"""<a href='/mapoverview/circuit/?circuit={line[0]}'>{line[0]}</a>""")
                except:
                    pass
            with open(cached_output_file, 'w') as outputfile:
                outputfile.write(json.dumps(lines))  
                
        info = """
        <p>
        In this table you can see the Circuits that have more than 2 loose ends. Meaning that its not a single line but multiple lines. Lines are considered conencted if the coordinates are less than a meter apart.
        </p>
        """   
        return self.render_template('single_column_table.html', table_header="Malformed circuits", entries=lines, page_info=info)
    
    