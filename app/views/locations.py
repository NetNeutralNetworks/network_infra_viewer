import json, logging, re, itertools, os, glob, xmltodict

from flask import request
from flask_appbuilder import AppBuilder, BaseView, expose, has_access

from pyvis.network import Network

from ..scripts.memgraph import execute_query
from ..scripts.score_rendering import render_config_scores

class LocationView(BaseView):
    default_view = 'list_locations'

    @expose('/list/', methods=['GET'])
    @has_access
    def list_locations(self):
        # Get All vrf's to show in table view
        q = f"""
            MATCH (d:Device)--(o:RWS_object)
            RETURN distinct o.name, avg(d.security_score), avg(d.reliability_score), avg(d.management_score), count(d), d.object_type
        """
        lines = []
        for vrf in execute_query(q):
            service, security, reliability, management, count, object_type = vrf
            security, reliability, management = render_config_scores(security, reliability, management)
            lines.append(f"<a href='/locationview/show/{service}'>{service}</a></td><td>{object_type}</td><td>{count}</td><td>{security}</td><td>{reliability}</td><td>{management}")


        help = """
            <p>This page shows all RWS Object locations. An object can be a bridge, water lock, highway junction.</p>
            <p>This data is provided by the TOPdesk export.</p>
            """
        return self.render_template('single_column_table.html', table_header="Locations </td><td>Object type</td><td>#devices</td><td>Average security</td><td>Average reliabilty</td><td>Average management", entries=lines, page_info=help, page_category='Network Components', page='Locations')
    
    @expose('/show/<string:location>', methods=['GET'])
    @has_access
    def show_locations(self, location):
        # Get All vrf's to show in table view
        q = f"""
            MATCH (d:Device)--(o:RWS_object)
            WHERE o.name = '{location}'
            RETURN d
        """
        lines = []
        for device in execute_query(q):
            security, reliability, management = render_config_scores(device[0].properties['security_score'], device[0].properties['reliability_score'], device[0].properties['management_score'])
            lines.append(f"<a href='/deviceview/show/?hostname={device[0].properties['hostname']}'>{device[0].properties['hostname']}</a></td><td>{security}</td><td>{reliability}</td><td>{management}")


        help = """
            <p>This page shows a location with its devices</p>
            <p>This data is provided by TOPdesk export.</p>
            """
        
        location_l2_button = f"""
        <a class="btn btn-primary" href="/locationview/l2/?location={location}" style="grid-column: 2/3;">
            Show L2 overview
      </a>
      <a class="btn btn-primary" href="/locationview/uplink_view/?location={location}" style="grid-column: 2/3;">
            Show Uplink chain overview
      </a>
        """
        return self.render_template('single_column_table.html', table_header=f"Devices located at {location}</td><td>Security</td><td>Reliabilty</td><td>Management", entries=lines, page_info=help, extra_html = location_l2_button, page_category='Network Components', page='Locations')
    
    @expose('/l2/', methods=['GET'])
    @has_access
    def show_location_l2(self):
        request_data = request.args
        location = request_data.get('location')
        # Get All vrf's to show in table view
        q = f"""
            MATCH (d:Device)--(o:RWS_object)
            WHERE o.name = '{location}'
            MATCH path=((d)-[:HAS_INTERFACE]-()-[:HAS_NEIGHBOR]-()--(d2:Device))
            RETURN path
        """
        device_network = Network(notebook=False, cdn_resources='in_line', height='800px')
        # device_network.show_buttons()
        devices = {}
        for path in execute_query(q):
            # logging.getLogger().info('Response: %s', path[0])
            nodes = path[0].nodes
            for node in nodes:
                if "Device" in node.labels:
                    if "-CE" in node.properties["hostname"]:
                        device_network.add_node(node.id, label=node.properties.get("hostname"), color="red")
                    elif "-PE" in node.properties["hostname"]:
                        device_network.add_node(node.id, label=node.properties.get("hostname"), color="purple")
                    elif "-P4" in node.properties["hostname"] or "-P5" in node.properties["hostname"]:
                        device_network.add_node(node.id, label=node.properties.get("hostname"), color="blue")
                    else:
                        device_network.add_node(node.id, label=node.properties.get("hostname"), color="yellow")
                    devices[node.properties["hostname"]] = node.properties
                elif "Interface" in node.labels:
                    device_network.add_node(node.id, label=node.properties.get("name"), color="orange", shape="box", mass=1)
            edges = path[0].relationships
            for edge in edges:
                device_network.add_edge(edge.start_id, edge.end_id)
        l2_html = device_network.generate_html()
        l2_html = re.sub(r'<center>.+?<\/h1>\s+<\/center>', '', l2_html, 2, re.DOTALL)
        l2_html = re.sub(r'<link\s*href.*?\/>', '', l2_html, 0, re.DOTALL)
        help = """
            <p>This page shows how devices are connected within a single location</p>
            <p>This data is provided by the CSPC collector using cdp/lldp neighbors.</p>
            """
        device_locations = {}
        for device in devices:
            q = f"""
            MATCH (d:Device)--(l:Location)
            WHERE d.hostname = '{device}'
            RETURN l
            """
            for location in execute_query(q):
                device_locations[device] = {'latitude': location[0].properties['latitude'],'longtitude': location[0].properties['longtitude']}
        markers = []
        for device, location in device_locations.items():
            markers.append({'hostname': device, 'latitude': location['latitude'],'longtitude': location['longtitude']})
        return self.render_template('location.html',  page_info=help, html=l2_html, markers=markers, lines=[], page_category='Network Components', page='Locations')
    
    @expose('/uplink_view/', methods=['GET'])
    @has_access
    def show_location_uplinks(self):
        request_data = request.args
        location = request_data.get('location')
        # Get All vrf's to show in table view
        q = f"""
            MATCH (O:RWS_object)
            WHERE O.name = "{location}"

            MATCH path=((O)--(ce:Device))
            WHERE ce.hostname =~ ".*-CE.*" 
            OPTIONAL MATCH (ce)-[:HAS_INTERFACE|:HAS_NEIGHBOR*1..3]-(pe:Device)
            WHERE pe.hostname =~ ".*-PE.*" 
            OPTIONAL MATCH (pe)-[:HAS_INTERFACE|:HAS_NEIGHBOR*1..3]-(p:Device)
            WHERE p.hostname =~ ".*-P[4,5].*"

            RETURN DISTINCT O, ce, pe, p
        """
        graph = ""
        device_network = Network(notebook=False, cdn_resources='in_line', height='800px')
        devices = []
        for o, ce, pe, p in execute_query(q):
            
            if not o.id in devices:
                icon = "\uf059"
                if ce and ce.properties.get("object_type") == "Sluis":
                    icon = "\uf21a"
                elif ce and ce.properties.get("object_type") == "Brug":
                    icon = "\ue4ce"
                elif ce and ce.properties.get("object_type") == "Wegkant/Waterkant/CVR":
                    icon = "\ue563"
                elif ce and ce.properties.get("object_type") == "Verkeerscentrale / Verkeerspost":
                    icon = "\uf018"
                elif ce and ce.properties.get("object_type") == "Kantoor":
                    icon = "\uf1ad"
                elif ce and ce.properties.get("object_type") == "Tunnel":
                    icon = "\uf1ad"
                device_network.add_node(o.id, label=o.properties.get("name"), color="grey", level=0, shape="icon", icon={"face": "'Font Awesome 6 Free'", "weight": "bold", "code": icon, "size": 50, "color": "#154273"})
                devices.append(o.id)
            if ce and not ce.id in devices:
                color = "red"
                if pe:
                    color = "green"
                device_network.add_node(ce.id, label=ce.properties.get("hostname"), color=color, level=1)
                devices.append(ce.id)
            if pe and not pe.id in devices:
                color = "red"
                if p:
                    color = "green"
                device_network.add_node(pe.id, label=pe.properties.get("hostname"), color=color, level=2)
                devices.append(pe.id)
            if p and not p.id in devices:
                color = "green"
                device_network.add_node(p.id, label=p.properties.get("hostname"), color=color, level=3)
                devices.append(p.id)
            
            
            if ce:
                device_network.add_edge(o.id, ce.id, color="grey")
            if pe:
                device_network.add_edge(ce.id, pe.id, color="grey")
            if p:
                device_network.add_edge(pe.id, p.id, color="grey")
#             graph+=f"""
#     {p.id}[{p.properties['hostname']}] --> {pe.id}[{pe.properties['hostname']}];
#     {pe.id}[{pe.properties['hostname']}] --> {ce.id}[{ce.properties['hostname']}];
#     {ce.id}[{ce.properties['hostname']}] --> {o.id}[{o.properties['name']}];
# """
        # device_network.show_buttons(filter_=["layout"])
        options = {
            # "edges": {
            #     "smooth": {
            #         "type": "continuous",
            #     }
            # },
            "nodes": {
                "physics": False,
            },
            "layout": {
                "improvedLayout": True,
                "hierarchical": {
                    "enabled": True,
                    "direction": "UD",
                    # "levelSeparation": 150,
                    "edgeMinimization": True,
                    "blockShifting": True,
                    "levelSeparation": 150,
                    "nodeSpacing": 150,
                    "treeSpacing": 400,
                    "sortMethod": "hubsize",
                }
            }
        }
        device_network.set_options("const config=" + json.dumps(options))
        l2_html = device_network.generate_html()
        # l2_html = re.sub(r'<center>.+?<\/h1>\s+<\/center>', '', l2_html, 2, re.DOTALL)
        # l2_html = re.sub(r'<link\s*href.*?\/>', '', l2_html, 0, re.DOTALL)
        l2_html += """
<script>
function cluster() {
  network.setData(data);
  var levels = [0, 1, 2, 3];
  var clusterOptionsByData;
  for (var i = 0; i < levels.length; i++) {
    var level = levels[i];
    clusterOptionsByData = {
      joinCondition: function (childOptions) {
        return childOptions.level == level; 
      },
      processProperties: function (clusterOptions, childNodes, childEdges) {
        var totalMass = 0;
        for (var i = 0; i < childNodes.length; i++) {
          totalMass += childNodes[i].mass;
        }
        clusterOptions.mass = totalMass;
        return clusterOptions;
      },
      clusterNodeProperties: {
        id: "cluster:" + level.toString(),
        borderWidth: 3,
        shape: "database",
        color: "grey",
        label: "Level:" + level.toString(),
        level: level
      },
    };
    network.cluster(clusterOptionsByData);
  }
}

network.on("selectNode", function (params) {
  if (params.nodes.length == 1) {
    if (network.isCluster(params.nodes[0]) == true) {
      network.openCluster(params.nodes[0]);
    }
  }
});

network.on("doubleClick", function (params) {
    try{
        var selectedNode = allNodes[network.getSelectedNodes()[0]]
            if(selectedNode.level == 0){
                var selectedNode = network.getSelectedNodes()[0]
                var label = allNodes[selectedNode].label 
                window.location.assign(
                    "/locationview/show/" + label
                );
            }
    }
catch (error){
console.log(error)}
    
  
});

document.fonts
      .load('normal normal 900 24px/1 "Font Awesome 6 Free"')
</script
"""

        return self.render_template('object_uplink_view.html', mermaid_graph=graph, l2_html=l2_html, page_category='Network Components', page='Locations')
    

    @expose('/calculate_reliability/', methods=['GET'])
    @has_access
    def calculate_reliability(self):
        request_data = request.args
        location = request_data.get('location')
        q = f"""
        MATCH (O:RWS_object)
        RETURN DISTINCT O LIMIT 20
        """
        redundant_objects = []
        for o in execute_query(q):
            q2 = f"""
            MATCH (O:RWS_object)
            WHERE O.name = "{o[0].properties['name']}"

            MATCH path=((O)--(ce:Device))
            WHERE ce.hostname =~ ".*-CE.*" 
            OPTIONAL MATCH (ce)-[:HAS_INTERFACE|:HAS_NEIGHBOR*1..3]-(pe:Device)
            WHERE pe.hostname =~ ".*-PE.*" 
            OPTIONAL MATCH (pe)-[:HAS_INTERFACE|:HAS_NEIGHBOR*1..3]-(p:Device)
            WHERE p.hostname =~ ".*-P[4,5].*"

            RETURN DISTINCT O, ce, pe, p
            """
            
            ces = set()
            pes = set()
            ps = set()
            for o, ce, pe, p in execute_query(q2):
                if ce:
                    ces.add(ce.properties['hostname'])
                if pe:
                    pes.add(pe.properties['hostname'])
                if p:
                    ps.add(p.properties['hostname'])
            if len(ces) > 1 and len(pes) > 1 and len(ps) > 1:
                redundant_objects.append({o.properties['name']: True})
            else:
                redundant_objects.append({o[0].properties['name'] : False})
        return str(redundant_objects)
            