import bmesh
import bpy


class ALX_OT_MESH_AverageMeshSeamsNormals(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_mesh_average_mesh_seams_normals"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def execute(self, context: bpy.types.Context):
        mesh_selection: dict[str, bmesh.types.BMesh] = dict()
        mesh_data_pair: dict[str, bpy.types.Mesh] = dict()
        for mesh in context.selected_objects:
            if (mesh.type == "MESH"):
                temp_bmesh = bmesh.new()
                temp_bmesh.from_mesh(mesh.data, face_normals=True, vertex_normals=True, use_shape_key=False)
                temp_bmesh.verts.ensure_lookup_table()
                mesh_selection.update({mesh.name: temp_bmesh})
                mesh_data_pair.update({mesh.name: mesh.data})

        boundary_verts = {
            f"{mesh_name}?{vertex.index}": f"{round(vertex.co.x, 4)}?{round(vertex.co.y, 4)}?{round(vertex.co.z, 4)}"
            for mesh_name, mesh in mesh_selection.items() for vertex in mesh.verts
            if (vertex.is_boundary)
        }

        overlapping = list()
        for current_pos in boundary_verts.values():

            current_overlap = set()
            for mesh, pos in boundary_verts.items():
                if (pos == current_pos):
                    current_overlap.add(mesh)
            overlapping.append(current_overlap)

        custom_normals: dict[int, list[float, float, float]] = dict()
        for vertex_set in overlapping:
            normal = {"x": 0, "y": 0, "z": 0}
            for mesh_index_pair in vertex_set:
                vert = mesh_selection[mesh_index_pair.split("?")[0]].verts[int(mesh_index_pair.split("?")[1])]
                normal["x"] += float(vert.normal.x)
                normal["y"] += float(vert.normal.y)
                normal["z"] += float(vert.normal.z)

                custom_normals.update({int(mesh_index_pair.split("?")[1]): [normal["x"] / len(vertex_set), normal["y"] / len(vertex_set), normal["z"] / len(vertex_set)]})

        for mesh in mesh_data_pair.values():
            mesh_custom_split_normals = []
            for vert in mesh.vertices:
                if (vert.index in custom_normals.keys()):
                    mesh_custom_split_normals.append(list(custom_normals[vert.index]))
                else:
                    mesh_custom_split_normals.append([0, 0, 0])

            print(mesh)
            print(custom_normals)

        mesh.normals_split_custom_set_from_vertices(mesh_custom_split_normals)

        return {"FINISHED"}
