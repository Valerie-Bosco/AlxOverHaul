import bpy

from ..modules.Alx_Module_Manager_Utils import define_dependency
from ..utilities.Alx_Armature_Utils import COMPARE_VertexGroups_BoneNames
from .ALX_Object_Properties import ALX_PT_ObjectProperties


# @define_dependency("ALX_PT_ObjectProperties")
class ALX_PT_ArmatureData(bpy.types.Panel):
    """"""

    bl_label = "Alx Armature Data"
    bl_idname = "ALX_PT_armature_data"
    # bl_parent_id = ALX_PT_ObjectProperties.bl_idname

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    bl_context = "object"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.label(text="Alx")
