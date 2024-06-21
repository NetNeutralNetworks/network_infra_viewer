import json
import logging, os, re, csv, traceback
from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access
from pyvis.network import Network



from ..scripts.memgraph import execute_query, commit_query
from ..scripts.location_calculations import get_GPS_from_RD, get_closest_point

class MatchDeviceToLocation(BaseView):
    default_view = 'main_page'

    @expose('/list/', methods=['GET'])
    @has_access
    def main_page(self):
        q_locations = f"""
MATCH (loc:Location)
return DISTINCT loc


        """
        roads = {}
        locations = []
        for entry in execute_query(q_locations):
            location = entry[0]
            name = location.properties['name']
            match = re.search("(OS|WKS|KST|VIRTUEEL-KAST)_(?P<road>(A|N)(\d+))_(?P<direction>L|R)(?P<distance>\d*.\d*)", name)
            # logging.getLogger().info(match)
            if match:
                try:
                    if f"{match['road']}{match['direction']}" in roads.keys():
                        roads[f"{match['road']}{match['direction']}"].append({
                            'name': location.properties['name'],
                            'road': match['road'],
                            'direction': match['direction'],
                            'distance': float(match['distance']),
                            'latitude': location.properties['latitude'],
                            'longtitude': location.properties['longtitude'],
                        })
                    else:
                        roads[f"{match['road']}{match['direction']}"] = [{
                            'name': location.properties['name'],
                            'road': match['road'],
                            'direction': match['direction'],
                            'distance': float(match['distance']),
                            'latitude': location.properties['latitude'],
                            'longtitude': location.properties['longtitude'],
                        }, ]

                    locations.append({
                        'name': location.properties['name'],
                        'road': match['road'],
                        'direction': match['direction'],
                        'distance': float(match['distance']),
                        'latitude': location.properties['latitude'],
                        'longtitude': location.properties['longtitude'],
                    })
                except:
                    pass
        # logging.getLogger().info(roads)


        q_devices = f"""
    MATCH (d:Device)
    WHERE not exists((d)--(:Location))
    return DISTINCT d.hostname


        """
        devices = []
        for entry in execute_query(q_devices):
            hostname = entry[0]
            match = re.search("(?P<road>(A|N)\d+)-(?P<km>\d+)-(?P<m>\d+)(?P<direction>L|R).*", hostname)
            # logging.getLogger().info(match)
            if match:
                distance = float(f"{match['km']}.{match['m']}")
                road = f"{match['road']}{match['direction']}"
                closest_name = None
                closest_distance = float('inf')

                for obj in roads.get(road, []):
                    if obj['distance'] == distance:
                        closest_name = obj['name']
                        q = f"""
                        MATCH (d:Device)
                        WHERE d.hostname = '{hostname}'
                        MATCH (l:Location)
                        WHERE l.name = '{closest_name}'
                        MERGE (d)-[:PROBABLY_LOCATED_AT]->(l)
                        """
                        logging.getLogger().info(commit_query(q))
                        break
                    # elif abs(obj['distance'] - distance) < closest_distance:
                    #     if abs(obj['distance'] - distance) > 0.25:
                    #         continue
                    #     closest_distance = abs(obj['distance'] - distance)
                    #     closest_name = obj['name']
                # logging.getLogger().info(closest_name)
                devices.append({
                    'hostname': hostname,
                    'location': closest_name     
                })
        # logging.getLogger().info(devices)
                

        
        help = """
        <p></p>
        """
        return self.render_template('single_column_table.html', table_header="Locaties per device", entries=devices,  page_info=help)
