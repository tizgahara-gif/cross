import bpy


def ensure_grid_node_group(name: str):
    ng = bpy.data.node_groups.get(name)
    if ng:
        return ng

    ng = bpy.data.node_groups.new(name=name, type='GeometryNodeTree')

    group_in = ng.nodes.new("NodeGroupInput")
    group_in.location = (-200, 0)
    group_out = ng.nodes.new("NodeGroupOutput")
    group_out.location = (200, 0)

    ng.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    ng.links.new(group_in.outputs["Geometry"], group_out.inputs["Geometry"])
    return ng
