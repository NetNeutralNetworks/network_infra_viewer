import json, os
import logging
from collections import Counter
from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access
from pyvis.network import Network

from ..scripts.memgraph import execute_query

class LijnbenamingMissingPort(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        
        q = f"""
            MATCH (l:Lijnbenaming)
            WHERE NOT exists((l)-[]-(:Port))
            return l.lijnbenaming


        """
        lines = []
        for entry in execute_query(q):
            # logging.getLogger().info('Response: %s', entry[0])
            lines.append(entry[0])
            
                
        info = """
        <p>
        In this view you can see all the circuits that have been created in Cocon but the connection to the device/port is unknown. This information should be provided by KPN.
        </p>
        """   
        return self.render_template('single_column_table.html', table_header="Lijnbenaming zonder koppeling met Device", entries=lines, page_info=info)
    
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
        In this view you can see all the devices are not plotted on a location. The current method of determining the location of a device is based on its hostname.
        So UT-PAP-P5-001 is placed in UT-PAP. However most devices roadside are not being matched because a different format is used.
        </p>
        """        
        
        return self.render_template('single_column_table.html', table_header="Devices zonder locatie (Physical)", entries=devices, page_info=info)
    
    
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
        In this view you can see all the devices of which no port or interface is known. This means the device does not have any known neighborships and is not reported te be connected to a fiber (by KPN).
        </p>
        <p>This device probably has CDP disabled.</p>
        """   
        return self.render_template('single_column_table.html', table_header="Devices zonder Port of Interface", entries=devices, page_info=info)
    

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
            MATCH (l:Lijnbenaming)
            RETURN DISTINCT l.lijnbenaming
            """
            lines = []
            for line in execute_query(q1):
                if line[0] == "":
                    continue
                q = f"""
                MATCH (l:Lijnbenaming)-[]-(f:Fiber)-[]-(s:Span)
                WHERE l.lijnbenaming = "{line[0]}"

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
                        lines.append(f"""<a href='/mapoverview/dfc/?dfc={line[0]}'>{line[0]}</a>""")
                    # coordinates = []
                    # loose_ends = []
                    # for span in execute_query(q):
                    #     # logging.getLogger().info('Response: %s', entry[0])
                    #     path = json.loads(span[0].properties['path'])
                    #     coordinates.append((round(path[0][0],5),round(path[0][1],5)))
                    #     coordinates.append((round(path[-1][0],5),round(path[-1][1],5)))
                    #         # else:
                    #         #     logging.getLogger().info('Response: %s', coord[0])
                    # counter_dict = Counter(coordinates)
                    # for coord, value in counter_dict.items():
                    #     if value < 2:
                    #         loose_ends.append(coord)
                    # if len(loose_ends) > 3:
                    #     lines.append(f"""<a href='/mapoverview/dfc/?dfc={line[0]}'>{line[0]}</a>""")
                    #     # logging.getLogger().info('Response: %s -> %s', line[0], loose_ends)
                except:
                    pass
            with open(cached_output_file, 'w') as outputfile:
                outputfile.write(json.dumps(lines))  
                
        info = """
        <p>
        In this table you can see the Circuits that have more than 2 loose ends. Meaning that its not a single line but multiple lines. Lines are considered conencted if the coordinates are less than a meter apart.
        </p>
        <p>This report is based on data provided by Cocon.</p>
        """   
        return self.render_template('single_column_table.html', table_header="Circuits die niet doorlopen", entries=lines, page_info=info)
    
    