

import bmesh
import bpy

# class Alx_OT_UV_Snapping_BulkSelection(bpy.types.Operator):
#     """"""

#     bl_label = ""
#     bl_idname = "alx.operator_uv_snapping_bulk_selection"

#     uv_editor_area: bpy.types.SpaceUVEditor = None

#     edit_object: bpy.types.Object = None
#     edit_object_mesh: bpy.types.Mesh = None
#     edit_object_bmesh: bmesh.types.BMesh = None

#     uv_layer = None

#     @classmethod
#     def poll(self, context: bpy.types.Context):
#         return (context.mode == "EDIT_MESH") and (context.edit_object.type == "MESH")

#     def execute(self, context: bpy.types.Context):
#         if (self.edit_object is None):
#             self.edit_object = context.edit_object

#         if (self.edit_object is not None) and (self.edit_object_mesh is None):
#             self.edit_object_mesh = self.edit_object.data

#         if (self.edit_object_bmesh is None) or (self.edit_object_bmesh.is_valid == False):
#             self.edit_object_bmesh = bmesh.from_edit_mesh(self.edit_object_mesh)
#             self.uv_layer = self.edit_object_bmesh.loops.layers.uv.new("UVMap") if self.edit_object_bmesh.loops.layers.uv.get("UVMap") is None else self.edit_object_bmesh.loops.layers.uv.get("UVMap")

#         b_should_update = False
#         grid_scale = self.uv_editor_area.custom_grid_subdivisions

#         for loop in [loop for vert in [vert for vert in self.edit_object_bmesh.verts if (vert.select)] for loop in vert.link_loops if (loop[self.uv_layer].select)]:
#             uv_co = loop[self.uv_layer].uv
#             snapped_co = (float(f"{ uv_co[0] - float(f"{uv_co[0]: .{2}f}")  % float(f"{1 / grid_scale[0]: .{2}f}") :.{2}f}"), float(f"{ uv_co[1] - float(f"{uv_co[1]: .{2}f}")  % float(f"{1 / grid_scale[1]: .{2}f}") :.{2}f}"))
#             if (uv_co != snapped_co):
#                 b_should_update = True
#                 loop[self.uv_layer].uv = snapped_co

#         if (b_should_update == True):
#             bmesh.update_edit_mesh(self.edit_object_mesh)
#             b_should_update = False

#         if (self.edit_object_bmesh is not None):
#             self.edit_object_bmesh.free()
#         return {"FINISHED"}

#     def invoke(self, context, event):
#         for area in context.screen.areas:
#             for space in area.spaces:
#                 if (area.type == "IMAGE_EDITOR") and (space.type == "IMAGE_EDITOR"):
#                     self.uv_editor_area = space.uv_editor
#         return self.execute(context)
