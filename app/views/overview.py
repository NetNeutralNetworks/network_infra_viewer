import json

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from ..scripts.memgraph import execute_query

class MapOverview(BaseView):
    default_view = 'main_page'

    @expose('/overview/', methods=['GET','POST'])
    @has_access
    def main_page(self):
    #     print("starting")
    #     query = None
    #     if request.method == 'POST':
    #         query = request.form['query']
    #         span_status = request.form['span_status']
    #     else:
    #         span_status = 'all'
        
    #     q = f"""
    # MATCH (l:Location)--(d:Device)
    # {'WHERE l.name CONTAINS "' + query + '"' if query != None else ''}
    # RETURN DISTINCT l
    # """
    #     markers=[]
    #     for location in execute_query(q):
    #         marker = {
    #         'lat':location[0].properties['latitude'],
    #         'lon':location[0].properties['longtitude'],
    #         'popup':location[0].properties['name']
    #         }
    #         markers.append(marker)
    #     print('q1 done')
    #     if query:
    #         q2 = f"""
    #         MATCH (l:Lijnbenaming)-[r1]-(f:Fiber)-[r2]-(s:Span)
    #         WHERE (s.span CONTAINS "{query}" and s.status > 0) OR s.locatie_naam_a CONTAINS "{query}" OR s.locatie_naam_a CONTAINS "{query}" OR l.lijnbenaming CONTAINS "{query}"
    #         RETURN s
    #         """
    #     else:
    #         q2 = f"""
    #         MATCH (s:Span)
    #     {"WHERE s.status = '" + span_status + "'" if span_status != 'all' else ""}
    #         RETURN s
    #         """
    #     print("q2 done")
    #     spans=[]
    #     for span in execute_query(q2):
    #         try:
    #             line = {
    #             'capacity':span[0].properties['kabelcapaciteit'],
    #             'coords': json.loads(span[0].properties['path']),
    #             'spanid': span[0].properties['span'] 
    #             }
    #             spans.append(line)
                
    #         except Exception as e:
    #             print(f'''Error: {e}: {span[0]}''')
            
        return self.render_template('overview_new.html', 
                                    # markers=markers, 
                                    # spans=spans, 
                                    page_category='Network Components',
                                    page='Overview')
    
    @expose('/overview/old', methods=['GET','POST'])
    @has_access
    def main_page_old(self):
        print("starting")
        query = None
        if request.method == 'POST':
            query = request.form['query']
            span_status = request.form['span_status']
        else:
            span_status = 'all'
        
        q = f"""
    MATCH (l:Location)--(d:Device)
    {'WHERE l.name CONTAINS "' + query + '"' if query != None else ''}
    RETURN DISTINCT l
    """
        markers=[]
        for location in execute_query(q):
            marker = {
            'lat':location[0].properties['latitude'],
            'lon':location[0].properties['longtitude'],
            'popup':location[0].properties['name']
            }
            markers.append(marker)
        print('q1 done')
        if query:
            q2 = f"""
            MATCH (l:Lijnbenaming)-[r1]-(f:Fiber)-[r2]-(s:Span)
            WHERE (s.span CONTAINS "{query}" and s.status > 0) OR s.locatie_naam_a CONTAINS "{query}" OR s.locatie_naam_a CONTAINS "{query}" OR l.lijnbenaming CONTAINS "{query}"
            RETURN s
            """
        else:
            q2 = f"""
            MATCH (s:Span)
        {"WHERE s.status = '" + span_status + "'" if span_status != 'all' else ""}
            RETURN s
            """
        print("q2 done")
        spans=[]
        for span in execute_query(q2):
            try:
                line = {
                'capacity':span[0].properties['kabelcapaciteit'],
                'coords': json.loads(span[0].properties['path']),
                'spanid': span[0].properties['span'] 
                }
                spans.append(line)
                
            except Exception as e:
                print(f'''Error: {e}: {span[0]}''')
            
        return self.render_template('overview.html', 
                                    markers=markers, 
                                    spans=spans, 
                                    page_category='Network Components',
                                    page='Overview')
    
    @expose('/span/', methods=['GET'])
    @has_access
    def get_span_info(self):
        request_data = request.args
        q = f"""
            MATCH (l:Lijnbenaming)-[r1]-(f:Fiber)-[r2]-(s:Span)
            WHERE s.span = "{request_data['span']}"

            return DISTINCT l.lijnbenaming
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

    @expose('/dfc/', methods=['GET'])
    @has_access
    def get_dfc_info(self):
        request_data = request.args
        q = f"""
            MATCH (l:Lijnbenaming)-[r1]-(f:Fiber)-[r2]-(s:Span)
            WHERE l.lijnbenaming = "{request_data['dfc']}"

            return DISTINCT s

    """
        spans = []
        for span in execute_query(q):
            try:
                line = {
                'capacity':span[0].properties['kabelcapaciteit'],
                'coords': json.loads(span[0].properties['path']),
                'spanid': span[0].properties['span'] 
                }
                spans.append(line)
                
            except Exception as e:
                print(f'''Error: {e}: {span[0]}''')
        print(len(spans))
            
        return self.render_template('overview.html', spans=spans, markers=[], page_category='Network Components')