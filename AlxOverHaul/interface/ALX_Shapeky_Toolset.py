import bpy

from ..MeshTools.AlxShapekeyTools import ALX_OT_Shapekey_RemoveUnlockedShapekey


class ALX_MT_ShapeKeyToolset(bpy.types.Menu):
    """"""

    bl_label = ""
    bl_idname = "ALX_MT_menu_shapekey_toolset"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def draw(self, context: bpy.types.Context):
        layout: bpy.types.UILayout = self.layout

        remove_operators_box = layout.box()
        remove_operators_box.operator(ALX_OT_Shapekey_RemoveUnlockedShapekey.bl_idname, text="Remove Unlocked Shapekeys", icon="UNLOCKED")
