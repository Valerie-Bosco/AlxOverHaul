import bmesh
import bpy

from ..utilities.AlxUtilities import (get_modifiers_of_type,
                                      operator_log_warning)


class Alx_OT_Armature_BoneChainOnSelection(bpy.types.Operator):
    """"""

    bl_label = "Alx Rigging - chain on edge selection"
    bl_idname = "alx.operator_armature_bone_chain_on_selection"
    bl_description = "automatically create and weight paint a bone chain to the current edge-strip selection"
    bl_options = {"REGISTER", "UNDO"}

    user_armature_name: bpy.props.StringProperty(
        name="New armature name:")  # type:ignore
    reverse: bpy.props.BoolProperty(name="Reverse direction")  # type:ignore

    hair_strip_object: bpy.types.Object = None
    hair_strip_mesh: bpy.types.Mesh = None
    hair_strip_bmesh: bmesh.types.BMesh = None

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.area is not None) and (context.area.type == "VIEW_3D") and (context.mode == "EDIT_MESH")

    def execute(self, context: bpy.types.Context):
        if (context.mode == "EDIT_MESH") and (context.edit_object.type == "MESH"):
            self.hair_strip_object = context.edit_object
            self.hair_strip_mesh = context.edit_object.data

            self.hair_strip_bmesh = bmesh.from_edit_mesh(self.hair_strip_mesh)

            self.hair_strip_bmesh.verts.ensure_lookup_table()
            self.hair_strip_bmesh.edges.ensure_lookup_table()
            self.hair_strip_bmesh.faces.ensure_lookup_table()

            if (len(get_modifiers_of_type(self.hair_strip_object, "SUBSURF")) > 0):
                operator_log_warning(
                    self,
                    message="[subdivision][modifier] | [present], [topology][source] | [base mesh]"
                )

            edge_selection = [
                edge.index for edge in self.hair_strip_bmesh.edges
                if (edge.select == True)
            ]

            edge_selection_check = []
            for edge_index in edge_selection:
                count_check = 0
                for vert in self.hair_strip_bmesh.edges[edge_index].verts:
                    for lnk_edge in vert.link_edges:
                        if (lnk_edge.select == True) and (lnk_edge.index != self.hair_strip_bmesh.edges[edge_index].index):
                            count_check += 1
                if (count_check in [1, 2]):
                    edge_selection_check.append(True)
                else:
                    edge_selection_check.append(False)

            edge_selection_validity = (
                len(edge_selection_check) > 0) and all(edge_selection_check)

            if (edge_selection_validity == False):
                self.report(
                    {"ERROR"}, "Selection is invalid - no more than two connected edge selected per vertex")
                return {"CANCELLED"}

            if (edge_selection_validity == True):
                chain_ends = [vert.index for edge_index in edge_selection for vert in self.hair_strip_bmesh.edges[edge_index].verts if (
                    len([0 for edge in vert.link_edges if (edge.select == True)]) == 1)]

                starting_vert: bmesh.types.BMVert = None
                ending_vert: bmesh.types.BMVert = None

                if (self.hair_strip_bmesh.verts[chain_ends[0]].co.z > self.hair_strip_bmesh.verts[chain_ends[1]].co.z) and (self.reverse == False):
                    starting_vert = self.hair_strip_bmesh.verts[chain_ends[0]]
                    ending_vert = self.hair_strip_bmesh.verts[chain_ends[1]]
                elif (self.hair_strip_bmesh.verts[chain_ends[1]].co.z > self.hair_strip_bmesh.verts[chain_ends[0]].co.z) and (self.reverse == False):
                    starting_vert = self.hair_strip_bmesh.verts[chain_ends[1]]
                    ending_vert = self.hair_strip_bmesh.verts[chain_ends[0]]
                elif (self.hair_strip_bmesh.verts[chain_ends[0]].co.z > self.hair_strip_bmesh.verts[chain_ends[1]].co.z) and (self.reverse == True):
                    starting_vert = self.hair_strip_bmesh.verts[chain_ends[1]]
                    ending_vert = self.hair_strip_bmesh.verts[chain_ends[0]]
                elif (self.hair_strip_bmesh.verts[chain_ends[1]].co.z > self.hair_strip_bmesh.verts[chain_ends[0]].co.z) and (self.reverse == True):
                    starting_vert = self.hair_strip_bmesh.verts[chain_ends[0]]
                    ending_vert = self.hair_strip_bmesh.verts[chain_ends[1]]
                else:
                    if (self.reverse == False):
                        starting_vert = self.hair_strip_bmesh.verts[chain_ends[0]]
                        ending_vert = self.hair_strip_bmesh.verts[chain_ends[1]]
                    if (self.reverse == True):
                        starting_vert = self.hair_strip_bmesh.verts[chain_ends[1]]
                        ending_vert = self.hair_strip_bmesh.verts[chain_ends[0]]

                ordered_vert_chain = [starting_vert.index]
                queue_vert = starting_vert
                for i in range(0, len(edge_selection)):
                    for edge in queue_vert.link_edges:
                        if (edge.index in edge_selection):
                            for vert in edge.verts:
                                if (vert.index not in ordered_vert_chain) and (vert.index != queue_vert.index):
                                    ordered_vert_chain.append(vert.index)
                                    queue_vert = vert

                bpy.ops.object.mode_set(mode="OBJECT")
                ordered_bone_position_map = dict()

                for i in range(0, len(ordered_vert_chain) - 1):
                    head = self.hair_strip_object.matrix_world @ self.hair_strip_bmesh.verts[
                        ordered_vert_chain[i]].co
                    tail = self.hair_strip_object.matrix_world @ self.hair_strip_bmesh.verts[
                        ordered_vert_chain[i + 1]].co
                    vertex_normal = self.hair_strip_bmesh.verts[ordered_vert_chain[i]].normal

                    ordered_bone_position_map.update(
                        {f"bone.v_index_{ordered_vert_chain[i]}": [head, tail, vertex_normal]})

                i = 0
                while i < len(ordered_vert_chain) - 1:
                    if (self.hair_strip_object.vertex_groups.get(f"bone.v_index_{ordered_vert_chain[i]}") is None):
                        self.hair_strip_object.vertex_groups.new(
                            name=f"bone.v_index_{ordered_vert_chain[i]}")
                    i += 1

                if (self.user_armature_name != ""):
                    armature_object = bpy.data.objects.get(
                        self.user_armature_name)
                    if (armature_object is None):
                        new_armature_data = bpy.data.armatures.new(
                            name=self.user_armature_name)
                        armature_object = bpy.data.objects.new(
                            name=self.user_armature_name, object_data=new_armature_data)

                    if (armature_object.name not in context.scene.collection.objects):
                        context.scene.collection.objects.link(armature_object)

                    armature_data: bpy.types.Armature = armature_object.data

                    processed_edges = []
                    for i in range(0, len(ordered_vert_chain)):
                        if (i < len(ordered_vert_chain) - 1):
                            bone_vertex_group: bpy.types.VertexGroup = self.hair_strip_object.vertex_groups.get(
                                f"bone.v_index_{ordered_vert_chain[i]}")

                            if (bone_vertex_group is not None):
                                bone_edge = [v1_edge for v1_edge in self.hair_strip_bmesh.verts[ordered_vert_chain[i]].link_edges if (
                                    v1_edge.index in [v2_edge.index for v2_edge in self.hair_strip_bmesh.verts[ordered_vert_chain[i + 1]].link_edges])][0]
                                bone_vertex_group.add(
                                    index=[vert.index for vert in bone_edge.verts], weight=1, type="REPLACE")

                                if (bone_edge is not None):
                                    queue_edges = [bone_edge]

                                    i_rec = 0
                                    while (i_rec < 100):
                                        queue_edge = queue_edges.pop(0) if (
                                            len(queue_edges) > 0) else queue_edge

                                        vertex_blacklist = [
                                            *[vert.index for vert in queue_edge.verts], *[vert.index for vert in queue_edge.verts]]
                                        last_edge = []
                                        if (len(last_edge) >= 2):
                                            break

                                        for q_face in queue_edge.link_faces:

                                            for f_edge in q_face.edges:
                                                for f_vert in f_edge.verts:
                                                    if (f_vert.index in vertex_blacklist):
                                                        break
                                                else:
                                                    if (f_edge not in processed_edges):
                                                        bone_vertex_group.add(
                                                            index=[vert.index for vert in f_edge.verts], weight=1, type="REPLACE")
                                                        last_edge.append(0)
                                                        queue_edges.append(
                                                            f_edge)

                                                processed_edges.append(
                                                    f_edge.index)

                                        i_rec += 1

                    context.view_layer.objects.active = armature_object
                    bpy.ops.object.mode_set(mode="EDIT")

                    i = 0
                    while i < len(ordered_vert_chain):
                        bone = armature_data.edit_bones.new(f"bone.v_index_{ordered_vert_chain[i]}") if armature_data.edit_bones.get(
                            f"bone.v_index_{ordered_vert_chain[i]}") is None else armature_data.edit_bones.get(f"bone.v_index_{ordered_vert_chain[i]}")

                        if (bone is not None):
                            if (f"bone.v_index_{ordered_vert_chain[i]}" in ordered_bone_position_map.keys()):

                                head_vert = ordered_bone_position_map[
                                    f"bone.v_index_{ordered_vert_chain[i]}"][0]
                                bone.head.xyz = head_vert

                                tail_vert = ordered_bone_position_map[
                                    f"bone.v_index_{ordered_vert_chain[i]}"][1]
                                bone.tail.xyz = tail_vert

                                bone.parent = armature_data.edit_bones.get(
                                    f"bone.v_index_{ordered_vert_chain[i-1]}")
                                bone.use_connect = True

                                bone.align_roll(
                                    vector=ordered_bone_position_map[f"bone.v_index_{ordered_vert_chain[i]}"][2])

                        i += 1

                    bpy.ops.object.mode_set(mode="OBJECT")
                    context.view_layer.objects.active = self.hair_strip_object
                    bpy.ops.object.mode_set(mode="EDIT")

                    if (context.mode in ["OBJECT", "SCULPT"]):
                        self.hair_strip_bmesh.to_mesh(self.hair_strip_mesh)
                    if (context.mode == "EDIT_MESH"):
                        bmesh.update_edit_mesh(self.hair_strip_mesh)

            if (self.hair_strip_bmesh is not None):
                self.hair_strip_bmesh.free()
            return {"FINISHED"}

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.row().label(text="Options:")
        layout.row().prop(self, "user_armature_name")
        layout.row().prop(self, "reverse")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
