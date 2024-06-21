import json, logging, re, itertools, os, glob, xmltodict

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from pyvis.network import Network

import random

from ..scripts.memgraph import execute_query, commit_query


class GenerateFakeScores(BaseView):
    default_view = 'main_page'

    @expose('/generate/', methods=['GET'])
    @has_access
    def main_page(self):
        q = f"""
    MATCH (d:Device)
    return d
        """
        devices = []
        for entry in execute_query(q):
            device = entry[0]
            seed = hash(device.properties['hostname'])
            random.seed(seed)
            security_score = random.randint(40,100)
            reliability_score = random.randint(50,100)
            management_score = random.randint(40,100)
            q_device = f"""
                MATCH (d:Device)
                WHERE d.hostname = "{device.properties['hostname']}"
                SET d.security_score = {security_score}
                SET d.reliability_score = {reliability_score}
                SET d.management_score = {management_score}
            """
            commit_query(q_device)

        return "Generated fake scores..."