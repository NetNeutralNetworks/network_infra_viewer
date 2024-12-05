import mgclient
import os
import json
from dotenv import load_dotenv

load_dotenv()
MEMGRAPH_HOST = os.environ['MEMGRAPH_HOST']
MEMGRAPH_PORT = int(os.environ['MEMGRAPH_PORT'])

def execute_query(q):
    conn = mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)
    cursor = conn.cursor()

    # Execute a query

    cursor.execute(q)
    return cursor.fetchall()

def commit_query(q):
    conn = mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)
    cursor = conn.cursor()

    # Execute a query

    cursor.execute(q)
    conn.commit()
    return cursor.fetchall()