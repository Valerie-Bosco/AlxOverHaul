import bpy



# class Alx_PT_Particle_GeneralPanel(bpy.types.Panel):
#     """"""

#     bl_label = ""
#     bl_idname = "ALX_PT_panel_particle_general_panel"

#     bl_space_type = "VIEW_3D"  
#     bl_region_type = "UI"
    
#     bl_order = 0
#     bl_category = "Alx3D"

#     @classmethod
#     def poll(self, context: bpy.types.Context):
#         return True
    
#     def draw(self, context: bpy.types.Context):
#         self.layout.prop(context.active_object, "alx_particle_surface_object", text="Surface")
#         self.layout.prop(context.active_object, "alx_particle_generator_source_object", text="Target")
#         self.layout.operator(Alx_OT_Particle_ConvertToType.bl_idname, text="Convert To Particle")



# class Alx_OT_Particle_ConvertToType(bpy.types.Operator):
#     """"""

#     bl_label = ""
#     bl_idname = "alx.operator_particle_convert_to_type"

#     @classmethod
#     def poll(self, context: bpy.types.Context):
#         return True
    
#     def execute(self, context: bpy.types.Context):
#         override_window = context.window
#         override_screen = override_window.screen
#         override_area = [area for area in override_screen.areas if area.type == "VIEW_3D"]
#         override_region = [region for region in override_area[0].regions if region.type == 'WINDOW']

#         with context.temp_override(window=override_window, area=override_area[0], region=override_region[0]):
#             surface_source : bpy.types.Object = context.active_object.alx_particle_surface_object
#             particle_source = context.active_object.alx_particle_generator_source_object

#             context.view_layer.objects.active = particle_source
#             bpy.ops.object.convert(target="CURVE", keep_original=True)
#             bpy.ops.object.convert(target="CURVES", keep_original=False)

#             curve_object : bpy.types.Curves = bpy.data.hair_curves.get(context.active_object.data.name)
#             if (curve_object is not None):
#                 curve_object.surface = surface_source
#                 if (surface_source.data.uv_layers.get("UVMap") is not None):
#                     curve_object.surface_uv_map = "UVMap" if surface_source.data.uv_layers.get("UVMap") is not None else ""

#             bpy.ops.curves.convert_to_particle_system()
#         return {"FINISHED"}