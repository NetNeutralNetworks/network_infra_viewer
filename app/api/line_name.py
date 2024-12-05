import json

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from ..scripts.memgraph import execute_query
from ..cache import appCache

class LineNameAPI(BaseView):
    route_base = '/api/line_names/v1'
    @expose('/list', methods=['GET'])
    @has_access
    # @appCache.cached(timeout=500)
    def list_line_names(self):
        q = f"""
        MATCH (l:Circuit)--(f:Fiber)--(s:Span)
        RETURN DISTINCT l.Circuit, s.span
        """
        line_names=[]
        for result in execute_query(q):
            line_names.append({'line_name': result[0], 'spanid': result[1]})
        return line_names