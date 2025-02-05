import bpy

from ..Definitions.AlxTypesDefinition import TD_object_types


class Alx_MT_MenuPie_UnlockedObjectModes(bpy.types.Menu):
    """"""

    bl_label = "unlocked object modes"
    bl_idname = "ALX_MT_menu_pie_unlocked_object_modes"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.area.type == "VIEW_3D")

    def draw(self, context):
        PieMenu = self.layout.menu_pie()

        object_mode_button: Alx_OT_operator_UnlockedObjectModes = PieMenu.operator(
            Alx_OT_operator_UnlockedObjectModes.bl_idname, text="OBJECT", icon="OBJECT_DATAMODE")
        object_mode_button.target_object_mode = "OBJECT"

        if (context.mode != "POSE"):
            auto_pose_mode_button: Alx_OT_operator_UnlockedObjectModes = PieMenu.operator(
                Alx_OT_operator_UnlockedObjectModes.bl_idname, text="A-POSE", icon="ARMATURE_DATA")
            auto_pose_mode_button.target_object_mode = "POSE"
        else:
            if (context.mode == "POSE"):
                box = PieMenu.box()
                box.label(text="[Mode] | [Pose]")

        if (context.mode != "PAINT_WEIGHT"):
            auto_weight_paint_mode_button: Alx_OT_operator_UnlockedObjectModes = PieMenu.operator(
                Alx_OT_operator_UnlockedObjectModes.bl_idname, text="A-WPAINT", icon="WPAINT_HLT")
            auto_weight_paint_mode_button.target_object_mode = "PAINT_WEIGHT"
        else:
            if (context.mode == "PAINT_WEIGHT"):
                box = PieMenu.box()
                box.label(text="[Mode] | [Weight Paint]")

        edge_edit_mode_button: Alx_OT_operator_UnlockedObjectModes = PieMenu.operator(
            Alx_OT_operator_UnlockedObjectModes.bl_idname, text="Edge", icon="EDGESEL")
        edge_edit_mode_button.target_object_mode = "EDIT"
        edge_edit_mode_button.target_object_sub_mode = "EDGE"
        edge_edit_mode_button.target_object_type = "MESH"

        vertex_edit_mode_button: Alx_OT_operator_UnlockedObjectModes = PieMenu.operator(
            Alx_OT_operator_UnlockedObjectModes.bl_idname, text="Vertex", icon="VERTEXSEL")
        vertex_edit_mode_button.target_object_mode = "EDIT"
        vertex_edit_mode_button.target_object_sub_mode = "VERT"
        vertex_edit_mode_button.target_object_type = "MESH"

        face_edit_mode_button: Alx_OT_operator_UnlockedObjectModes = PieMenu.operator(
            Alx_OT_operator_UnlockedObjectModes.bl_idname, text="Face", icon="FACESEL")
        face_edit_mode_button.target_object_mode = "EDIT"
        face_edit_mode_button.target_object_sub_mode = "FACE"
        face_edit_mode_button.target_object_type = "MESH"

        if (len(context.selected_objects) != 0):

            selection_bulk_edit_box = PieMenu.box().row().split(factor=0.33)
            selection_bulk_edit_box_L = selection_bulk_edit_box.column()
            selection_bulk_edit_box_M = selection_bulk_edit_box.column()
            selection_bulk_edit_box_R = selection_bulk_edit_box.column()

            sbe_armature: Alx_OT_operator_UnlockedObjectModes = selection_bulk_edit_box_L.row().operator(
                Alx_OT_operator_UnlockedObjectModes.bl_idname, text="Armature", icon="ARMATURE_DATA")
            sbe_armature.target_object_mode = "EDIT"
            sbe_armature.target_object_type = "ARMATURE"
            sbe_armature.target_object_sub_mode = ""

            sbe_curve: Alx_OT_operator_UnlockedObjectModes = selection_bulk_edit_box_L.row().operator(
                Alx_OT_operator_UnlockedObjectModes.bl_idname, text="Curve", icon="CURVE_DATA")
            sbe_curve.target_object_mode = "EDIT"
            sbe_curve.target_object_type = "CURVE"
            sbe_curve.target_object_sub_mode = ""

            sbe_surface: Alx_OT_operator_UnlockedObjectModes = selection_bulk_edit_box_L.row().operator(
                Alx_OT_operator_UnlockedObjectModes.bl_idname, text="Surface", icon="SURFACE_DATA")
            sbe_surface.target_object_mode = "EDIT"
            sbe_surface.target_object_type = "SURFACE"

            sbe_meta: Alx_OT_operator_UnlockedObjectModes = selection_bulk_edit_box_M.row().operator(
                Alx_OT_operator_UnlockedObjectModes.bl_idname, text="Meta", icon="META_DATA")
            sbe_meta.target_object_mode = "EDIT"
            sbe_meta.target_object_type = "META"

            sbe_text: Alx_OT_operator_UnlockedObjectModes = selection_bulk_edit_box_M.row().operator(
                Alx_OT_operator_UnlockedObjectModes.bl_idname, text="Text", icon="FILE_FONT")
            sbe_text.target_object_mode = "EDIT"
            sbe_text.target_object_type = "FONT"

            sbe_lattice: Alx_OT_operator_UnlockedObjectModes = selection_bulk_edit_box_M.row().operator(
                Alx_OT_operator_UnlockedObjectModes.bl_idname, text="Lattice", icon="LATTICE_DATA")
            sbe_lattice.target_object_mode = "EDIT"
            sbe_lattice.target_object_type = "LATTICE"

            gpenci_column = selection_bulk_edit_box_R.column()
            sbe_gpencil_point: Alx_OT_operator_UnlockedObjectModes = gpenci_column.operator(
                Alx_OT_operator_UnlockedObjectModes.bl_idname, text="GPencil", icon="GP_SELECT_POINTS")
            sbe_gpencil_point.target_object_mode = "EDIT"
            sbe_gpencil_point.target_object_sub_mode = "POINT"
            sbe_gpencil_point.target_object_type = "GPENCIL"

            sbe_gpencil_stroke: Alx_OT_operator_UnlockedObjectModes = gpenci_column.operator(
                Alx_OT_operator_UnlockedObjectModes.bl_idname, text="Strokes", icon="GP_SELECT_STROKES")
            sbe_gpencil_stroke.target_object_mode = "EDIT"
            sbe_gpencil_stroke.target_object_sub_mode = "STROKE"
            sbe_gpencil_stroke.target_object_type = "GPENCIL"

            sbe_gpencil_segment: Alx_OT_operator_UnlockedObjectModes = gpenci_column.operator(
                Alx_OT_operator_UnlockedObjectModes.bl_idname, text="B-Strokes", icon="GP_SELECT_BETWEEN_STROKES")
            sbe_gpencil_segment.target_object_mode = "EDIT"
            sbe_gpencil_segment.target_object_sub_mode = "SEGMENT"
            sbe_gpencil_segment.target_object_type = "GPENCIL"

        else:
            PieMenu.box().label(text="[Selection] [Missing]")

        if (context.mode != "SCULPT"):
            SculptMode: Alx_OT_operator_UnlockedObjectModes = PieMenu.operator(
                Alx_OT_operator_UnlockedObjectModes.bl_idname, text="Sculpt", icon="SCULPTMODE_HLT")
            SculptMode.target_object_mode = "SCULPT"
        else:
            if (context.mode == "SCULPT"):
                box = PieMenu.box()
                box.label(text="[Mode] | [Sculpt]")


class Alx_OT_operator_UnlockedObjectModes(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_unlocked_object_modes"
    bl_description = "unlocked object mode swapping supports mode to mode hopping without swapping to object mode first"
    bl_options = {"INTERNAL"}

    default_behaviour: bpy.props.BoolProperty(
        name="default behaviour", default=True, options={"HIDDEN"})  # type:ignore
    target_object_mode: bpy.props.StringProperty(
        name="target object mode", default="OBJECT", options={"HIDDEN"})  # type:ignore
    target_object_sub_mode: bpy.props.StringProperty(
        name="target object sub-mode", default="", options={"HIDDEN"})  # type:ignore
    target_object_type: bpy.props.StringProperty(
        name="target object type", default="", options={"HIDDEN"})  # type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.area.type == "VIEW_3D")

    def execute(self, context):
        match self.target_object_mode:
            # region
            case "OBJECT":
                if (context.mode != "OBJECT"):
                    bpy.ops.object.mode_set(mode="OBJECT")
                return {"FINISHED"}
            # endregion

            # region
            case "EDIT":
                if (context.mode != "OBJECT"):
                    bpy.ops.object.mode_set(mode="OBJECT")

                if (len(context.selected_objects) > 0):
                    if (self.target_object_type in TD_object_types):
                        match self.target_object_type:
                            case "MESH":
                                if (self.target_object_sub_mode in ["VERT", "EDGE", "FACE"]):
                                    for selected_object in context.selected_objects:
                                        if (context.active_object is not None and context.active_object.type != "MESH"):
                                            context.view_layer.objects.active = selected_object

                                    if (len(context.selected_objects) > 0) and (context.active_object.type == "MESH"):
                                        bpy.ops.object.mode_set_with_submode(
                                            mode="EDIT",
                                            mesh_select_mode=set([self.target_object_sub_mode])
                                        )
                                return {"FINISHED"}

                            case "ARMATURE":
                                if (self.target_object_sub_mode == ""):
                                    armature_selection_override = list(
                                        filter(
                                            lambda object: object is not None,

                                            [selected_object if (selected_object.type == "ARMATURE") else selected_object.find_armature()
                                             for selected_object in context.selected_objects
                                             if (selected_object is not None) and (selected_object.type in ["ARMATURE", "MESH"])]
                                        )
                                    )

                                    if (len(armature_selection_override) <= 0):
                                        return {"CANCELLED"}

                                    if (context.active_object.type == "MESH"):
                                        reference_object = context.active_object

                                        context.view_layer.objects.active = reference_object.find_armature()

                                        for armature_object in armature_selection_override:
                                            armature_object.select_set(True)

                                    if (context.active_object.type == "ARMATURE"):
                                        reference_object = context.active_object

                                        reference_object.select_set(True)
                                        context.view_layer.objects.active = reference_object

                                        for armature_object in armature_selection_override:
                                            armature_object.select_set(True)

                                    if (len(context.selected_objects) > 0) and (context.active_object.type == "ARMATURE"):
                                        bpy.ops.object.mode_set(mode="EDIT")
                                    return {"FINISHED"}

                            case "CURVE":
                                if (self.target_object_sub_mode == ""):
                                    for selected_object in context.selected_objects:
                                        if (context.active_object is not None and context.active_object.type != "CURVE"):
                                            context.view_layer.objects.active = selected_object

                                    if (len(context.selected_objects) > 0) and (context.active_object.type == "CURVE"):
                                        bpy.ops.object.mode_set(mode="EDIT")

                                return {"FINISHED"}

                            case "SURFACE":
                                if (self.target_object_sub_mode == ""):
                                    for selected_object in context.selected_objects:
                                        if (context.active_object is not None and context.active_object.type != "SURFACE"):
                                            context.view_layer.objects.active = selected_object

                                    if (len(context.selected_objects) > 0) and (context.active_object.type == "SURFACE"):
                                        bpy.ops.object.mode_set(mode="EDIT")

                                return {"FINISHED"}

                            case "META":
                                if (self.target_object_sub_mode == ""):
                                    for selected_object in context.selected_objects:
                                        if (context.active_object is not None and context.active_object.type != "META"):
                                            context.view_layer.objects.active = selected_object

                                    if (len(context.selected_objects) > 0) and (context.active_object.type == "META"):
                                        bpy.ops.object.mode_set_with_submode(
                                            mode="EDIT",
                                            mesh_select_mode=set([self.target_object_sub_mode])
                                        )

                                return {"FINISHED"}

                            case "FONT":
                                if (self.target_object_sub_mode == ""):
                                    for selected_object in context.selected_objects:
                                        if (context.active_object is not None and context.active_object.type != "FONT"):
                                            context.view_layer.objects.active = selected_object

                                    if (len(context.selected_objects) > 0) and (context.active_object.type == "FONT"):
                                        bpy.ops.object.mode_set_with_submode(
                                            mode="EDIT",
                                            mesh_select_mode=set([self.target_object_sub_mode])
                                        )

                                return {"FINISHED"}

                            case "LATTICE":
                                if (self.target_object_sub_mode == ""):
                                    for selected_object in context.selected_objects:
                                        if (context.active_object is not None and context.active_object.type != "LATTICE"):
                                            context.view_layer.objects.active = selected_object

                                    if (len(context.selected_objects) > 0) and (context.active_object.type == "LATTICE"):
                                        bpy.ops.object.mode_set_with_submode(
                                            mode="EDIT",
                                            mesh_select_mode=set([self.target_object_sub_mode])
                                        )

                                return {"FINISHED"}

                            case "GPENCIL":
                                if (self.target_object_sub_mode in ["POINT", "STROKE", "SEGMENT"]):
                                    for selected_object in context.selected_objects:
                                        if (context.active_object is not None and context.active_object.type != "GPENCIL"):
                                            context.view_layer.objects.active = selected_object

                                    if (len(context.selected_objects) > 0) and (context.active_object.type == "GPENCIL"):
                                        bpy.ops.object.mode_set(mode="EDIT_GPENCIL")
                                        context.scene.tool_settings.gpencil_selectmode_edit = self.target_object_sub_mode

                                return {"FINISHED"}

                return {"FINISHED"}
            # endregion

            # region
            case "SCULPT":
                if (context.mode != "OBJECT"):
                    bpy.ops.object.mode_set(mode="OBJECT")

                if (len(context.selected_objects) > 0):
                    sculpt_selection_override = [
                        selected_object
                        for selected_object in context.selected_objects
                        if (selected_object.type == "MESH")
                    ]

                    if (len(sculpt_selection_override) == 0):
                        return {"CANCELLED"}

                    bpy.ops.object.mode_set(mode="OBJECT")
                    context.view_layer.objects.active = sculpt_selection_override[0]
                    bpy.ops.object.mode_set(mode="SCULPT")

                return {"FINISHED"}
            # endregion

            # region
            case "POSE":
                if (context.mode != "OBJECT"):
                    bpy.ops.object.mode_set(mode="OBJECT")

                if (len(context.selected_objects) > 0):
                    armatures = list(filter(
                        lambda object: object is not None,
                        [
                            selected_object if (selected_object.type == "ARMATURE") else selected_object.find_armature()
                            for selected_object in context.selected_objects
                            if (selected_object.type in ["MESH", "ARMATURE"])
                        ]
                    ))

                    for armature in armatures:
                        armature.hide_set(
                            False, view_layer=context.view_layer)
                        armature.hide_viewport = False

                        armature.select_set(
                            True, view_layer=context.view_layer)

                        if (context.active_object is not None and context.active_object.type != "ARMATURE"):
                            context.view_layer.objects.active = armature

                    bpy.ops.object.mode_set(mode="POSE")

                return {"FINISHED"}
            # endregion

            # region
            case "PAINT_WEIGHT":
                if (context.mode != "OBJECT"):
                    bpy.ops.object.mode_set(mode="OBJECT")

                if (len(context.selected_objects) > 0):
                    mesh = None
                    armature = None

                    if (context.active_object.type == "MESH"):
                        context.active_object.select_set(
                            True, view_layer=context.view_layer)

                        mesh = context.active_object
                        armature = context.active_object.find_armature()
                        if (armature is not None):
                            armature.select_set(
                                True, view_layer=context.view_layer)
                            armature.hide_set(
                                False, view_layer=context.view_layer)
                            armature.hide_viewport = False
                    else:
                        if (context.active_object.type == "ARMATURE"):
                            for selected_object in context.selected_objects:
                                if (selected_object.type == "MESH"):
                                    mesh = selected_object
                                    armature = selected_object.find_armature()
                                    if (armature is not None) and (armature is context.active_object):
                                        armature.select_set(
                                            True, view_layer=context.view_layer)
                                        context.view_layer.objects.active = selected_object
                                        break

                    if (armature is not None) or (mesh is not None):
                        bpy.ops.object.mode_set(mode="WEIGHT_PAINT")

                return {"FINISHED"}
            # endregion

        return {"FINISHED"}
