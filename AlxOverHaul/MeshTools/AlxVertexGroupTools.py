import bpy

from ..Definitions.AlxConstantsDefinition import NEAR_ZERO_FLOAT


class Alx_OT_Mesh_VertexGroup_Clean(bpy.types.Operator):
    """"""

    bl_label = "Alx VGroups - clean vertex groups"
    bl_idname = "alx.operator_vertex_group_clean"

    bl_options = {"REGISTER", "UNDO"}

    b_empty: bpy.props.BoolProperty()  # type:ignore
    b_skeleton_only: bpy.props.BoolProperty()  # type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.area is not None) and (context.area.type == "VIEW_3D")

    def execute(self, context: bpy.types.Context):
        if (bool(context.selected_objects)):
            for selected_object in context.selected_objects:
                if (selected_object is not None) and (selected_object.type == "MESH"):
                    cleaning_target: bpy.types.Object = selected_object
                    pending_delete = set()

                    VXGroup: bpy.types.VertexGroup
                    if (self.b_empty == True):
                        for VXGroup in cleaning_target.vertex_groups:
                            for vert in cleaning_target.data.vertices:
                                try:
                                    if (VXGroup.weight(vert.index) > NEAR_ZERO_FLOAT):
                                        break
                                except:
                                    pass
                            else:
                                pending_delete.add(VXGroup)

                    if (self.b_skeleton_only == True):
                        armature_object = cleaning_target.find_armature()
                        if (armature_object is not None):
                            bone_name_set = set(
                                bone.name
                                for bone in armature_object.data.bones)

                            for VXGroup in cleaning_target.vertex_groups:
                                if (VXGroup.name not in bone_name_set):
                                    pending_delete.add(VXGroup)

                    for VXGroup in pending_delete:
                        cleaning_target.vertex_groups.remove(VXGroup)

        return {"FINISHED"}

    def draw(self, context: bpy.types.Context):
        self.layout.row().label(text="remove:")
        self.layout.row().prop(self, "b_empty", text="empty")
        self.layout.row().prop(self, "b_skeleton_only", text="name missmatch")

    def invoke(self, context: bpy.types.Context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
