import json
import logging, os, re
from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access
from pyvis.network import Network

from ..scripts.memgraph import execute_query

class DualHoming(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        cached_output_file = 'anomalies_dual_homing_mistakes.json'
        if os.path.isfile(cached_output_file):
            with open(cached_output_file, 'r') as outputfile:
                lines = json.loads(outputfile.read())
        else:
            q = f"""
    MATCH (d:Device)
    WHERE d.hostname =~ ".*-CE\\\d+D-.*"
    MATCH path=((d)-[:HAS_INTERFACE|:HAS_NEIGHBOR*BFS..3]-(d2:Device))
    WHERE d2.hostname =~ ".*-PE\\\d+.*"
    RETURN d.hostname, count(path)


            """
            lines = []
            for entry in execute_query(q):
                # logging.getLogger().info('Response: %s', entry[0])
                if entry[1] < 2:
                    lines.append(f"<a href='/deviceview/show/?hostname={entry[0]}'>{entry[0]}</a>")
                
            with open(cached_output_file, 'w') as outputfile:
                outputfile.write(json.dumps(lines))
        help = """
            <p>This page shows all devices that should be redundant in uplinks to PE devices (Dualhomed), but are missing one or both direct connections to a PE device. The devices are flagged as Dualhomed if the typical is followed by a "D". For example: CE49D.</p>
            <p>This data is provided by the CSPC collector.</p>
            """
        return self.render_template('single_column_table.html', table_header="Dualhomed devices not actualy conected to 2 PE devices", entries=lines,page_info=help, page_category='Anomalies')
    
class Redundancy(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        cached_output_file = 'anomalies_redundancy_mistakes.json'
        if os.path.isfile(cached_output_file):
            with open(cached_output_file, 'r') as outputfile:
                lines = json.loads(outputfile.read())
        else:
            q = f"""
    MATCH (d:Device)
    WHERE d.hostname =~ ".*-CE\\\d+R-.*"
    MATCH path=((d)-[:HAS_INTERFACE|:HAS_NEIGHBOR*BFS..6]-(d2:Device))
    WHERE d2.hostname =~ ".*-PE\\\d+.*"
    RETURN d.hostname, count(path)


            """
            lines = []
            for entry in execute_query(q):
                # logging.getLogger().info('Response: %s', entry[0])
                if entry[1] < 2:
                    lines.append(f"<a href='/deviceview/show/?hostname={entry[0]}'>{entry[0]}</a>")
                
            with open(cached_output_file, 'w') as outputfile:
                outputfile.write(json.dumps(lines))     
        help = """
            <p>This page shows all devices that should be redundant in both hardware and uplinks (Redundant), but are missing either. This can be caused by HA devices not being interconnected or one of the nodes not having a direct uplink to a PE router. The devices are flagged as Redundant if the typical is followed by a "R". For example: CE49R.</p>
            <p>This data is provided by the CSPC collector.</p>
            """
        return self.render_template('single_column_table.html', table_header="Redundant devices not actualy conected to 2 PE devices", entries=lines, page_info=help, page_category='Anomalies')
    
class LineRedundancy(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        cached_output_file = 'anomalies_line_redundancy.json'
        if os.path.isfile(cached_output_file):
            with open(cached_output_file, 'r') as outputfile:
                entries = json.loads(outputfile.read())
        else:
            entries = []
            # Get Dualhomed redundancy mistakes
            r_device_query = f"""
            MATCH (d:Device)
            WHERE d.hostname =~ '.*CE\\\d+D-.+'
            RETURN d.hostname
            """

            devices = {}
            for device in execute_query(r_device_query):
                q = f"""
                MATCH (d:Device)
                WHERE d.hostname = '{device[0]}'
                MATCH path=((d)-[:HAS_PORT]-()-[:IS_CONNECTED_TO]-(l:Lijnbenaming)-[:IS_CONNECTED_TO]-()-[:HAS_PORT]-(d2:Device))
                WHERE d2.hostname =~ ".*-PE\\\d+.*"

                RETURN DISTINCT l.lijnbenaming
                """

                spans = []
                for entry in execute_query(q):
                    q2 = f"""
                    MATCH (l:Lijnbenaming)
                    WHERE l.lijnbenaming = '{entry[0]}'
                    MATCH (l)--(f:Fiber)--(s:Span)

                    RETURN DISTINCT s
                    """
                    for entry2 in execute_query(q2):
                        spans.append(entry2[0])
                seen = set()
                dupes = []
                length = 0
                for span in spans:
                    if span.properties['span'] in seen:
                        dupes.append(span)
                        length+=float(span.properties['lengte'])
                    seen.add(span.properties['span'])
                
                if len(dupes) > 0:
                    devices[device[0]]={'spans': spans, 'total_length': length}

                
            for key, value in devices.items():
                entries.append(f"<a href='/deviceview/show/?hostname={key}'>{key}</a> </td><td>{value['total_length']}")

            logging.getLogger().info('Response: %s', len(entries))
            # Get Redunant redundancy mistakes
            r_device_query = f"""
            MATCH (d:Device)
            WHERE d.hostname =~ '.*CE\\\d+R-.+'
            RETURN d.hostname
            """
            
            devices = {}
            for device in execute_query(r_device_query):
                z = re.search(r'(.*-CE\d+R-).*',device[0])
                if z:
                    hostname=z.groups()[0]+'.*'
                q = f"""
                MATCH (d:Device)
                WHERE d.hostname =~ '{hostname}'
                MATCH path=((d)-[:HAS_PORT]-()-[:IS_CONNECTED_TO]-(l:Lijnbenaming)-[:IS_CONNECTED_TO]-()-[:HAS_PORT]-(d2:Device))
                WHERE d2.hostname =~ ".*-PE\\\d+.*"

                RETURN DISTINCT l.lijnbenaming
                """

                spans = []
                for entry in execute_query(q):
                    q2 = f"""
                    MATCH (l:Lijnbenaming)
                    WHERE l.lijnbenaming = '{entry[0]}'
                    MATCH (l)--(f:Fiber)--(s:Span)

                    RETURN DISTINCT s
                    """
                    for entry2 in execute_query(q2):
                        spans.append(entry2[0])
                seen = set()
                dupes = []
                length = 0
                for span in spans:
                    if span.properties['span'] in seen:
                        dupes.append(span)
                        length+=float(span.properties['lengte'])
                    seen.add(span.properties['span'])
                
                if len(dupes) > 0:
                    devices[device[0]]={'spans': spans, 'total_length': length}
            for key, value in devices.items():
                entries.append(f"<a href='/deviceview/show/?hostname={key}'>{key}</a> </td><td>{value['total_length']}")
            
            with open(cached_output_file, 'w') as outputfile:
                outputfile.write(json.dumps(entries))

        help = """
        <p>This page shows all the circuits that are supposed to be dualhomed, but the paths used as uplink are within the same fibrebundle somewhere.</p>
        <p>The length of the segments are calculated as the sum of all the segments that share a fibrebundle and is displayed in meters. This data is provided by Cocon</p>
        """
        
        return self.render_template('single_column_table.html', table_header="Hostname</td><td>Total non-redundanct fiber (m)", entries=entries, page_info=help, page_category='Anomalies')
    
# class LineRedundancyR(BaseView):
#     default_view = 'main_page'

#     @expose('/list/', methods=['GET'])
#     @has_access
#     def main_page(self):
#         cached_output_file = 'anomalies_line_redundancy_R.json'
#         if os.path.isfile(cached_output_file):
#             with open(cached_output_file, 'r') as outputfile:
#                 entries = json.loads(outputfile.read())
#         else:
#             r_device_query = f"""
#             MATCH (d:Device)
#             WHERE d.hostname =~ '.*CE\\\d+R-.+'
#             RETURN d.hostname
#             """
            
#             devices = {}
#             for device in execute_query(r_device_query):
#                 z = re.search(r'(.*-CE\d+R-).*',device[0])
#                 if z:
#                     hostname=z.groups()[0]+'.*'
#                 q = f"""
#                 MATCH (d:Device)
#                 WHERE d.hostname =~ '{hostname}'
#                 MATCH path=((d)-[:HAS_PORT]-()-[:IS_CONNECTED_TO]-(l:Lijnbenaming)-[:IS_CONNECTED_TO]-()-[:HAS_PORT]-(d2:Device))
#                 WHERE d2.hostname =~ ".*-PE\\\d+.*"

#                 RETURN DISTINCT l.lijnbenaming
#                 """

#                 spans = []
#                 for entry in execute_query(q):
#                     q2 = f"""
#                     MATCH (l:Lijnbenaming)
#                     WHERE l.lijnbenaming = '{entry[0]}'
#                     MATCH (l)--(f:Fiber)--(s:Span)

#                     RETURN DISTINCT s
#                     """
#                     for entry2 in execute_query(q2):
#                         spans.append(entry2[0])
#                 seen = set()
#                 dupes = []
#                 length = 0
#                 for span in spans:
#                     if span.properties['span'] in seen:
#                         dupes.append(span)
#                         length+=float(span.properties['lengte'])
#                     seen.add(span.properties['span'])
                
#                 if len(dupes) > 0:
#                     devices[device[0]]={'spans': spans, 'total_length': length}

#                 entries = []
#                 for key, value in devices.items():
#                     entries.append(f"<a href='/deviceview/show/?hostname={key}'>{key}</a> </td><td>{value['total_length']}")
#             with open(cached_output_file, 'w') as outputfile:
#                 outputfile.write(json.dumps(entries))

#         help = """
#         <p>This page shows all the circuits that are supposed to be redundant, but the paths used as uplink are within the same fibrebundle somewhere.</p>
#         <p>The length of the segments are calculated as the sum of all the segments that share a fibrebundle and is displayed in meters. This data is provided by Cocon</p>
#         """
        
#         return self.render_template('single_column_table.html', table_header="Hostname</td><td>Total non-redundanct fiber (m)", entries=entries, page_info=help)

class LineRedundancyMap(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        cached_output_file = 'anomalies_line_redundancy_map.json'
        if os.path.isfile(cached_output_file):
            with open(cached_output_file, 'r') as outputfile:
                span_nodes = json.loads(outputfile.read())
        else:
            r_device_query = f"""
            MATCH (d:Device)
            WHERE d.hostname =~ '.*CE\\\d+D-.+'
            RETURN d.hostname
            """

            devices = {}
            span_nodes = []
            for device in execute_query(r_device_query):
                q = f"""
                MATCH (d:Device)
                WHERE d.hostname = '{device[0]}'
                MATCH path=((d)-[:HAS_PORT]-()-[:IS_CONNECTED_TO]-(l:Lijnbenaming)-[:IS_CONNECTED_TO]-()-[:HAS_PORT]-(d2:Device))
                WHERE d2.hostname =~ ".*-PE\\\d+.*"

                RETURN DISTINCT l.lijnbenaming
                """

                spans = []
                for entry in execute_query(q):
                    q2 = f"""
                    MATCH (l:Lijnbenaming)
                    WHERE l.lijnbenaming = '{entry[0]}'
                    MATCH (l)--(f:Fiber)--(s:Span)

                    RETURN DISTINCT s
                    """
                    for entry2 in execute_query(q2):
                        spans.append(entry2[0])
                seen = set()
                dupes = []
                length = 0
                for span in spans:
                    if span.properties['span'] in seen:
                        dupes.append(span)
                        span_nodes.append({
                            'span': span.properties['span'],
                            'path': json.loads(span.properties['path']),
                        })
                        length+=float(span.properties['lengte'])
                    seen.add(span.properties['span'])
                
                if len(spans) > 0:
                    devices[device[0]]={'spans': spans, 'total_length': length}


            r_device_query = f"""
            MATCH (d:Device)
            WHERE d.hostname =~ '.*CE\\\d+R-.+'
            RETURN d.hostname
            """
            
            for device in execute_query(r_device_query):
                z = re.search(r'(.*-CE\d+R-).*',device[0])
                if z:
                    hostname=z.groups()[0]+'.*'
                q = f"""
                MATCH (d:Device)
                WHERE d.hostname =~ '{hostname}'
                MATCH path=((d)-[:HAS_PORT]-()-[:IS_CONNECTED_TO]-(l:Lijnbenaming)-[:IS_CONNECTED_TO]-()-[:HAS_PORT]-(d2:Device))
                WHERE d2.hostname =~ ".*-PE\\\d+.*"

                RETURN DISTINCT l.lijnbenaming
                """

                spans = []
                for entry in execute_query(q):
                    q2 = f"""
                    MATCH (l:Lijnbenaming)
                    WHERE l.lijnbenaming = '{entry[0]}'
                    MATCH (l)--(f:Fiber)--(s:Span)

                    RETURN DISTINCT s
                    """
                    for entry2 in execute_query(q2):
                        spans.append(entry2[0])
                seen = set()
                dupes = []
                length = 0
                for span in spans:
                    if span.properties['span'] in seen:
                        dupes.append(span)
                        span_nodes.append({
                            'span': span.properties['span'],
                            'path': json.loads(span.properties['path']),
                        })
                        length+=float(span.properties['lengte'])
                    seen.add(span.properties['span'])
                
                if len(dupes) > 0:
                    devices[device[0]]={'spans': spans, 'total_length': length}

                # for key, value in devices.items():
                #     span_nodes.append(f"<a href='/deviceview/show/?hostname={key}'>{key}</a> </td><td>{value['total_length']}")
            with open(cached_output_file, 'w') as outputfile:
                outputfile.write(json.dumps(span_nodes))
        help = """
        <p>This page shows a map of all the fibers that should be redundant but arn't. They are plotted on a map.</p>
        """
        return self.render_template('generic_map.html', lines=span_nodes, markers=[], page_info=help, color_strategy='single', page_category='Anomalies')
    