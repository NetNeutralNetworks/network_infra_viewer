import json, logging, re, itertools, os, glob, xmltodict

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from pyvis.network import Network

from ..scripts.memgraph import execute_query
from ..scripts.score_rendering import render_positive_negative

class RecommendationView(BaseView):
    default_view = 'list_recommendations'

    @expose('/list/', methods=['GET'])
    @has_access
    def list_recommendations(self):
        # Get devices baseline
        q = f"""
            MATCH (d:Device)
            RETURN avg(d.security_score), avg(d.reliability_score), avg(d.management_score), count(d)
        """
        avg_security, avg_reliability, avg_management, total_count = execute_query(q)[0]
        # Variable that gets passed to the table view
        lines = []

        # Get services
        q = f"""
            MATCH (d:Device)--(v:VRF)
            RETURN distinct v.name, avg(d.security_score), avg(d.reliability_score), avg(d.management_score), count(d)
        """
        
        for vrf in execute_query(q):
            service, security, reliability, management, count = vrf
            weighted_security_deviation = (security-avg_security)
            weighted_reliability_deviation = (reliability-avg_reliability)
            weighted_management_deviation = (management-avg_management)
            security_display, reliability_display, management_display = render_positive_negative(weighted_security_deviation, weighted_reliability_deviation, weighted_management_deviation)
            lines.append(f"<a href='/serviceview/show/{service}'>{service}</a></td><td>{count}</td><td>{security_display}</td><td>{reliability_display}</td><td>{management_display}")

        # Get Hardware
        q = f"""
            MATCH (d:Device)
            RETURN distinct d.hardware, avg(d.security_score), avg(d.reliability_score), avg(d.management_score), count(d)
        """
        
        for vrf in execute_query(q):
            service, security, reliability, management, count = vrf
            weighted_security_deviation = (security-avg_security)
            weighted_reliability_deviation = (reliability-avg_reliability)
            weighted_management_deviation = (management-avg_management)
            security_display, reliability_display, management_display = render_positive_negative(weighted_security_deviation, weighted_reliability_deviation, weighted_management_deviation)
            lines.append(f"<a href='/hardwareview/show/{service}'>{service}</a></td><td>{count}</td><td>{security_display}</td><td>{reliability_display}</td><td>{management_display}")

        # Get location
        q = f"""
            MATCH (d:Device)--(o:RWS_object)
            RETURN distinct o.name, avg(d.security_score), avg(d.reliability_score), avg(d.management_score), count(d)
        """
        
        for vrf in execute_query(q):
            service, security, reliability, management, count = vrf
            weighted_security_deviation = (security-avg_security)
            weighted_reliability_deviation = (reliability-avg_reliability)
            weighted_management_deviation = (management-avg_management)
            security_display, reliability_display, management_display = render_positive_negative(weighted_security_deviation, weighted_reliability_deviation, weighted_management_deviation)
            lines.append(f"<a href='/locationview/show/{service}'>{service}</a></td><td>{count}</td><td>{security_display}</td><td>{reliability_display}</td><td>{management_display}")


        help = """
            <p>This page shows an aggregated view of all the device 'slices'. Its shows the total deviation per category.</p>
            <p>Negative means this group is lower than the average, Positive means its higher than the average</p>
            <p>The information provided can be used to decide where to focus on improvements</p>
            <p>This data is provided by the CSPC collector and partly by TOPdesk export.</p>
            """
        return self.render_template('single_column_table.html', table_header="Group</td><td>#Devices</td><td>Average security</td><td>Average reliabilty</td><td>Average management", entries=lines, page_info=help, page_category='Network Components')
    