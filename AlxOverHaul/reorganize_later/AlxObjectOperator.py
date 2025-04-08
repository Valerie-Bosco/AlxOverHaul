import bmesh
import bpy
import mathutils

from ..utilities.ALX_BMesh_Utils import GET_selected_verts
from ..utilities.ALX_Math_Utils import AVERAGE_NormalFromVectorList


class ALX_OT_Object_UnlockedQOrigin(bpy.types.Operator):
    """"""

    bl_label = "ALX"
    bl_idname = "alx.operator_object_unlocked_q_origin"
    bl_options = {"REGISTER", "UNDO"}

    origin_set_mode: bpy.props.EnumProperty(
        name="", default="CURSOR_TO_WORLD",
        items={
            ("CURSOR_TO_WORLD", "cursor to world", "", 1),
            ("ORIGIN_TO_SELECTION", "origin to selection", "", 1 << 1)
        }
    )  # type:ignore

    ContextMesh: bpy.types.Mesh = None
    ContextBMesh: bmesh.types.BMesh = None

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.area.type == "VIEW_3D") and (context.object is not None)

    def execute(self, context):
        if (context.mode == "EDIT_MESH") and (context.edit_object.type == "MESH"):
            self.ContextMesh = context.edit_object.data
            if (self.ContextBMesh is None) or (not self.ContextBMesh.is_valid):
                self.ContextBMesh = bmesh.from_edit_mesh(self.ContextMesh)

            self.ContextBMesh.verts.ensure_lookup_table()
            self.ContextBMesh.edges.ensure_lookup_table()
            self.ContextBMesh.faces.ensure_lookup_table()

        object_mesh: bpy.types.Mesh = context.object.data

        # average_normal = mathutils.Vector(AVERAGE_NormalFromVectorList([self.ContextBMesh.verts[vert_index].normal for vert_index in GET_selected_verts(self.ContextBMesh)]))
        # angle = average_normal.rotation_difference(mathutils.Vector((0, 0, 0)))

        # correction_matrix = mathutils.Matrix().to_3x3()
        # correction_matrix.rotate(angle)

        # _mode = context.mode if (context.mode[0:4] != "EDIT") else "EDIT" if (context.mode[0:4] == "EDIT") else "OBJECT"
        # bpy.ops.object.mode_set(mode="OBJECT")
        # object_mesh.transform(correction_matrix.to_4x4())
        # bpy.ops.object.mode_set(mode=_mode)

        # if (self.origin_set_mode == "CURSOR_TO_WORLD"):
        #     context.scene.cursor.location = (0.0, 0.0, 0.0)
        #     return {"FINISHED"}

        # if (self.origin_set_mode == "ORIGIN_TO_SELECTION"):
        #     if (self.ContextBMesh is not None):
        #         object_mesh: bpy.types.Mesh = context.object.data
        #         object_Wmatrix: mathutils.Matrix = context.object.matrix_world

        #         selection = [vert.index for vert in self.ContextBMesh.verts if (vert.select == True)]

        #         selection_vertex_Wco_list = list([self.ContextBMesh.verts[vert_index].co for vert_index in selection])
        #         selection_average_Wco: mathutils.Vector = sum(selection_vertex_Wco_list, mathutils.Vector()) / len(selection_vertex_Wco_list)

        #         WM_vertex_corrective_value = mathutils.Matrix.Translation(-selection_average_Wco)

        #         _mode = context.mode if (context.mode[0:4] != "EDIT") else "EDIT" if (context.mode[0:4] == "EDIT") else "OBJECT"
        #         bpy.ops.object.mode_set(mode="OBJECT")
        #         object_mesh.transform(WM_vertex_corrective_value)
        #         bpy.ops.object.mode_set(mode=_mode)

        #         object_Wmatrix.translation = object_Wmatrix @ selection_average_Wco

        # return {"FINISHED"}

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class Alx_OT_Object_BatchMaterial(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_object_batch_material"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def auto_retrieve_file_materials(scene, context: bpy.types.Context):
        unique_modifier_type_set = set()
        unique_modifier_type_set.add(("NONE", "none", "", 1))

        material: bpy.types.Material

        if (len(context.selectable_objects) != 0):
            for i, material in enumerate(bpy.data.materials, start=1):
                unique_modifier_type_set.add((material.name, material.name, "", 1 << i))

        return unique_modifier_type_set

    user_material: bpy.props.EnumProperty(name="material", items=auto_retrieve_file_materials)  # type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.area.type == "VIEW_3D") and (context.object is not None)

    def execute(self, context: bpy.types.Context):
        for object in context.selected_objects:
            if (object.type == "MESH"):
                if (len(object.material_slots) > 0):
                    slot: bpy.types.MaterialSlot = object.material_slots[0]
                else:
                    bpy.context.view_layer.objects.active = object
                    bpy.ops.object.material_slot_add()

                if (self.user_material == "NONE"):
                    slot.material = None
                else:
                    material = bpy.data.materials.get(self.user_material)
                    if (material is not None):
                        slot.material = material

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
