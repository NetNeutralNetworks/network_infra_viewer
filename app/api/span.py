import json
import gzip

from flask import request, Response
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from ..scripts.memgraph import execute_query
from ..cache import appCache

class SpanAPI(BaseView):
    route_base = '/api/spans/v1'
    @expose('/list', methods=['GET'])
    @has_access
    # @appCache.cached(timeout=500)
    def list_spans(self):
        q2 = f"""
        MATCH (s:Span)
        RETURN s
        """
        spans=[]
        for span in execute_query(q2):
            try:
                line = {
                'capacity':span[0].properties['capacity'],
                'coords': json.loads(span[0].properties['path']),
                'spanid': span[0].properties['span'],
                # 'status': span[0].properties['status'] 
                }
                spans.append(line)
            except Exception as e:
                print(f'''Error: {e}: {span[0]}''')

        content = gzip.compress(json.dumps(spans).encode('utf8'), 5)
        response = Response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Type'] = 'application/json'
        response.headers['Cache-Control'] = f'Public, Max-Age={15*60}'
        return response