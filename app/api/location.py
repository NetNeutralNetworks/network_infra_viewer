import json

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from ..scripts.memgraph import execute_query

class LocationAPI(BaseView):
    route_base = '/api/locations/v1'
    @expose('/list', methods=['GET'])
    @has_access
    def list_locations(self):
        # request_data = request.args
        q = f"""
            MATCH (l:Location)--(d:Device)
            return l

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