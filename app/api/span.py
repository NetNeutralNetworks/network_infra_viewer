import json

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from ..scripts.memgraph import execute_query

class SpanAPI(BaseView):
    route_base = '/api/spans/v1'
    @expose('/list', methods=['GET'])
    @has_access
    def list_spans(self):
        q2 = f"""
        MATCH (s:Span)
        RETURN s
        """
        spans=[]
        for span in execute_query(q2):
            try:
                line = {
                'capacity':span[0].properties['kabelcapaciteit'],
                'coords': json.loads(span[0].properties['path']),
                'spanid': span[0].properties['span'],
                'status': span[0].properties['status'] 
                }
                spans.append(line)
            except Exception as e:
                print(f'''Error: {e}: {span[0]}''')
        return spans