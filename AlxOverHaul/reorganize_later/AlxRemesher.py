# # # class Alx_PG_PropertyGroup_GizmoControlPointData(bpy.types.PropertyGroup):
# # #     position_vector : bpy.props.FloatVectorProperty() #type:ignore


# # # class Alx_OT_Remesh_Gizmo_ControlPoint(bpy.types.GizmoGroup):
# # #     bl_label = ""
# # #     bl_idname = "ALX_GGT_remesh_gizmo_control_point"
    
# # #     bl_space_type = 'VIEW_3D'
# # #     bl_region_type = 'WINDOW'
# # #     bl_options = {'3D', 'PERSISTENT'}



# # #     @classmethod
# # #     def poll(self, context: bpy.types.Context):
# # #         return (context.object is not None) and (context.object.type == "MESH") and (context.object.mode == "EDIT")

# # #     def setup(self, context):
# # #         ContextObject = context.object

# # #         control_arrow = self.gizmos.new("GIZMO_GT_box_3d")
# # #         control_arrow.target_set_prop("offset", self, "")


# # #         gz.matrix_basis = ob.matrix_world.normalized()
# # #         gz.draw_style = 'BOX'

# # #         gz.color = 1.0, 0.5, 0.0
# # #         gz.alpha = 0.5

# # #         gz.color_highlight = 1.0, 0.5, 1.0
# # #         gz.alpha_highlight = 0.5

# # #         self.energy_gizmo = gz

# # #     def refresh(self, context):
# # #         ob = context.object
# # #         gz = self.energy_gizmo
# # #         gz.matrix_basis = ob.matrix_world.normalized()

# # class Alx_OT_Retopology(bpy.types.Operator):

# #     bl_label = ""
# #     bl_idname = "alx.operator_retopology"
# #     bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
# #     ContextMesh : bpy.types.Mesh = None
# #     ContextBMesh : bmesh.types.BMesh = None


# #     @classmethod
# #     def poll(self, context: bpy.types.Context):
# #         return (context.area is not None) and (context.area.type == "VIEW_3D") and (context.mode == "EDIT_MESH")


# #     def modal(self, context: bpy.types.Context, event: bpy.types.Event):
# #         override_window = context.window
# #         override_screen = override_window.screen
# #         override_area = [area for area in override_screen.areas if area.type == "VIEW_3D"]
# #         override_region = [region for region in override_area[0].regions if region.type == 'WINDOW']

# #         with context.temp_override(window=override_window, area=override_area[0], region=override_region[0]):
# #             if (event.type == "ESC") or ((context.area is not None) and (context.area.type != "VIEW_3D")) or (context.mode != "EDIT_MESH"):
# #                 return {"CANCELLED"}

# #         if (context.mode == "EDIT_MESH") and (context.edit_object.type == "MESH"):
# #             self.ContextMesh = context.edit_object.data
# #             if (self.ContextBMesh is None) or (not self.ContextBMesh.is_valid):
# #                 self.ContextBMesh = bmesh.from_edit_mesh(self.ContextMesh)

# #             self.ContextBMesh.verts.ensure_lookup_table()
# #             self.ContextBMesh.edges.ensure_lookup_table()
# #             self.ContextBMesh.faces.ensure_lookup_table()


        
# #         return {"PASS_THROUGH"}


# #     def invoke(self, context, event):
# #         context.window_manager.modal_handler_add(self)
# #         return {"RUNNING_MODAL"}