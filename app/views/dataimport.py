import json, logging, re, itertools, os, glob, xmltodict

from flask import request, flash
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from pyvis.network import Network

from ..scripts.memgraph import execute_query, commit_query
from ..scripts.score_rendering import render_config_scores

class ImportSiteView(BaseView):
    default_view = 'add'

    @expose('/add/', methods=['GET', 'POST'])
    @has_access
    def add(self):
        if request.method == 'GET':
            return self.render_template('add_site_form.html')
        request_data = request.form
        q = f"""
        CREATE (:Location {{name: '{request_data['site_name']}', latitude: '{request_data['site_lat']}', longtitude: '{request_data['site_lon']}'}});
        """
        commit_query(q)
        flash(f"Site: { request_data['site_name'] } succesfully added", "success")
        return self.render_template('add_site_form.html', page_category='Import')
    
class ImportDeviceView(BaseView):
    default_view = 'add'

    @expose('/add/', methods=['GET', 'POST'])
    @has_access
    def add(self):
        if request.method == 'GET':
            return self.render_template('add_device_form.html')
        request_data = request.form
        q = f"""
        MATCH (l:Location {{name: '{request_data['site_name']}'}})
        MERGE (d:Device {{hostname: '{request_data['device_hostname']}'}})
        MERGE (d)-[:IS_LOCATED_AT]->(l)
        RETURN (d)
        """
        commit_query(q)
        flash(f"Device: { request_data['device_hostname'] } succesfully added", "success")
        return self.render_template('add_device_form.html', page_category='Import')
    
class ImportSpanView(BaseView):
    default_view = 'add'

    @expose('/add/', methods=['GET', 'POST'])
    @has_access
    def add(self):
        if request.method == 'GET':
            return self.render_template('add_span_form.html')
        request_data = request.form
        q = f"""
        CREATE (:Span {{span: '{request_data['span_id']}', path: '{request_data['path']}', capacity: '{request_data['capacity']}'}});
        """
        commit_query(q)
        flash(f"Span: { request_data['span_id'] } succesfully added", "success")
        return self.render_template('add_device_form.html', page_category='Import')
    