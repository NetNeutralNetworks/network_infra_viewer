import json

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from ..scripts.memgraph import execute_query

class MapOverview(BaseView):
    default_view = 'main_page'

    @expose('/overview/', methods=['GET','POST'])
    @has_access
    def main_page(self):
        return self.render_template('overview_new.html', page_category='Network Components')
    
    @expose('/span/', methods=['GET'])
    @has_access
    def get_span_info(self):
        request_data = request.args
        q = f"""
            MATCH (l:Circuit)-[r1]-(f:Fiber)-[r2]-(s:Span)
            WHERE s.span = "{request_data['span']}"

            return DISTINCT l.name
    """
        span_info = execute_query(q) 
        return span_info

    @expose('/location/', methods=['GET'])
    @has_access
    def get_location_info(self):
        request_data = request.args
        q = f"""
            MATCH (l:Location)--(d:Device)
            WHERE l.name = '{request_data['location']}'
            return d.hostname

            """
        location_data = execute_query(q) 
        return location_data

    @expose('/circuit/', methods=['GET'])
    @has_access
    def get_circuit_info(self):
        request_data = request.args
        q = f"""
            MATCH (l:Circuit)-[r1]-(f:Fiber)-[r2]-(s:Span)
            WHERE l.Circuit = "{request_data['circuit']}"

            return DISTINCT s

    """
        spans = []
        for span in execute_query(q):
            try:
                line = {
                'capacity':span[0].properties['capacity'],
                'coords': json.loads(span[0].properties['path']),
                'spanid': span[0].properties['span'] 
                }
                spans.append(line)
                
            except Exception as e:
                print(f'''Error: {e}: {span[0]}''')
            
        return self.render_template('overview.html', spans=spans, markers=[], page_category='Network Components')