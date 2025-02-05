import bpy


class ALX_PT_ObjectProperties(bpy.types.Panel):
    """"""

    bl_label = ""
    bl_idname = "ALX_PT_object_properties"

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    bl_context = "object"

    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def draw(self, context: bpy.types.Context):
        layout = self.layout
