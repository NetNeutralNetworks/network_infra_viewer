import json

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

# from app import cache

from ..scripts.memgraph import execute_query
from ..cache import appCache

class LocationAPI(BaseView):
    route_base = '/api/locations/v1'
    @expose('/list', methods=['GET'])
    @has_access
    # @appCache.cached(timeout=500)
    def list_locations(self):
        # request_data = request.args
        q = f"""
            MATCH (l:Location)--(d:Device)
            RETURN DISTINCT l

            """
        location_data = []
        results = execute_query(q)
        for result in results:
            location_data.append({
                'name': result[0].properties.get('name'),
                'latitude': result[0].properties.get('latitude'),
                'longtitude': result[0].properties.get('longtitude'),
                'type': result[0].properties.get('type'),
            })
        return location_data