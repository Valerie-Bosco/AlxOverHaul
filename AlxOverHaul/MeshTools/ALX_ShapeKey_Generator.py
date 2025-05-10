import bmesh
import bpy


class ALX_OT_OBJECT_ShapekeyFromMesh(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_object_shapekey_from_mesh"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def execute(self, context: bpy.types.Context):

        return {"FINISHED"}
