import mgp
import random
 
 
@mgp.read_proc
def get_path(
    start: mgp.Vertex,
    length: int = 10,
    num_uplinks = 2,
) -> mgp.Record(uplink=mgp.Vertex, path=mgp.Path):
    """Generates a random path of length `length` or less starting
    from the `start` vertex.
 
    :param mgp.Vertex start: The starting node of the walk.
    :param int length: The number of edges to traverse.
    :return: Random path.
    :rtype: mgp.Record(mgp.Path)
    """
    # path = mgp.Path(start)
    try:
      uplinks = []
      nodes_to_check = [(start, 0, mgp.Path(start))]
      nodes_checked = []
      distance = 0

      while (len(uplinks) < num_uplinks) and (distance < length) and len(nodes_to_check) > 0:
        vertex, distance, path = nodes_to_check.pop(0)
        
        out_neighbors = [(x.to_vertex, x) for x in list(vertex.out_edges) if 'Device' in x.to_vertex.labels or 'Interface' in x.to_vertex.labels]
        in_neighbors = [(x.from_vertex, x) for x in list(vertex.in_edges) if 'Device' in x.from_vertex.labels or 'Interface' in x.from_vertex.labels]
        neighbors = in_neighbors + out_neighbors
        for neighbor, edge in neighbors:
          new_path = path.__copy__()
          new_path.expand(edge)
          if neighbor not in (x[0] for x in nodes_to_check) and neighbor not in nodes_checked:
            if 'CE' in neighbor.properties.get('hostname', ''):
              uplinks.append((neighbor, new_path))
              nodes_checked.append(neighbor)
            else: 
              nodes_to_check.append((neighbor, distance+1, new_path))
        nodes_checked.append(vertex)
        # return mgp.Record(uplinks=[vertex,])
    except Exception as e:
      raise Exception(f'''
      Current node: {vertex.properties.get("name")}
      Neighbor: {neighbor.properties.get("name")}
      Path: {[x.properties.get("name") for x in path.vertices]}
      To vertex:{edge.to_vertex.properties.get("name")}
      From vertex: {edge.from_vertex.properties.get("name")}
      Edge: {edge.id}''')

    return [mgp.Record(uplink=x[0], path=x[1]) for x in uplinks]