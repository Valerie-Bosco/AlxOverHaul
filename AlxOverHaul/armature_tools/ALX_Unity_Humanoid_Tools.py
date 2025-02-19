import bpy


class ALX_OT_Unity_SetHumanoidBoneNames(bpy.types.Operator):
    """"""

    bl_lable = ""
    bl_idname = "alx.operator_set_humanoid_bone_names"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def execute(self, context: bpy.types.Context):

        return
