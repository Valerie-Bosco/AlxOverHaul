
import bpy

from ..info_system import ALX_Info_System
from ..reorganize_later.AlxModifierOperators import (
    Alx_OT_Modifier_ManageOnSelected, Alx_PT_Operator_ModifierChangeSettings)
from ..reorganize_later.AlxProperties import \
    Alx_PG_PropertyGroup_ObjectSelectionListItem
from ..utilities.AlxUtilities import get_enum_property_items

LABEL = "LABEL_"
SEPARATOR = "SEPARATOR"


def UIPreset_PosePosition(parent_layout: bpy.types.UILayout = None, skeleton_object: bpy.types.Object = None, operator_bl_idname: str = ""):
    layout = parent_layout.row().split(factor=0.5, align=True)
    if (skeleton_object is not None):
        op_pose = layout.operator(
            operator_bl_idname,
            text="Pose",
            icon="ARMATURE_DATA",
            depress=(skeleton_object.data.pose_position == "POSE"))
        op_pose.b_pose = True
        op_pose.optional_skeleton_target_name = skeleton_object.data.name

        op_rest = layout.operator(
            operator_bl_idname,
            text="Rest",
            icon="OUTLINER_OB_ARMATURE",
            depress=(skeleton_object.data.pose_position == "REST"))
        op_rest.b_pose = False
        op_rest.optional_skeleton_target_name = skeleton_object.data.name
    else:
        layout.label(text="[Armature] [Missing]")


def UIPreset_VisibilityIsolator(parent_layout: bpy.types.UILayout = None, addon_properties: bpy.types.PropertyGroup = None, operator_bl_idname: str = ""):
    layout = parent_layout.row().split(factor=0.5)

    column_l = layout.column()
    column_r = layout.row()

    column_l.prop(
        addon_properties,
        "operator_object_and_collection_isolator_visibility_target",
        expand=True
    )
    op_isolator_hide = column_l.operator(
        operator_bl_idname,
        text="Isolate",
        icon="HIDE_ON",
        emboss=True
    )
    op_isolator_hide.PanicReset = False
    op_isolator_hide.TargetVisibility = False

    column = column_r.column()
    column.prop(
        addon_properties,
        "operator_object_and_collection_isolator_type_target",
        expand=True
    )
    op_isolator_show = column.operator(
        operator_bl_idname,
        text="Show",
        icon="HIDE_OFF",
        emboss=True
    )
    op_isolator_show.PanicReset = False
    op_isolator_show.TargetVisibility = True

    op_isolator_revert_ui = column_r.row()
    op_isolator_revert_ui.scale_y = 3.1
    op_isolator_revert = op_isolator_revert_ui.operator(
        operator_bl_idname,
        text="",
        icon="LOOP_BACK",
        emboss=True
    )
    op_isolator_revert.PanicReset = True


def UIPreset_OverlayToggles(parent_layout: bpy.types.UILayout = None, context: bpy.types.Context = None):
    layout = parent_layout.row()

    column = layout.column()
    column.prop(context.space_data.overlay, "show_overlays", text="", icon="OVERLAY")
    column.prop(context.space_data.overlay, "show_face_orientation", text="", icon="NORMALS_FACE")

    column = layout.column()

    row = column.row().split(factor=0.5, align=True)
    row.prop(context.area.spaces.active.shading, "show_xray", text="Mesh", icon="XRAY")
    row.prop(context.space_data.overlay, "show_xray_bone", text="Bone", icon="XRAY")

    row = column.row().split(factor=0.5, align=True)
    row.prop(context.space_data.overlay, "show_wireframes", text="Wireframe", icon="MOD_WIREFRAME")
    row.prop(context.space_data.overlay, "show_retopology", text="Retopology", icon="MESH_GRID")

    grid = layout.grid_flow(align=True, row_major=True, columns=2, even_columns=True, even_rows=True)
    grid.prop(context.area.spaces.active.shading, "type", text="", expand=True)


def UIPreset_ModifierCreateList(layout: bpy.types.UILayout = None, modifiers_types: list[list[str, list[str]]] = [], modifier_creation_operator: bpy.types.Operator = None):
    """
    modifiers_types : [ [label_name_1, [modifier_types_list_1]], [label_name_2, [modifier_types_list_2]] ]
    """

    for label, modifier_types in modifiers_types:
        modifier_space = layout.column()

        modifier_space.label(text=label)

        for mod_type in modifier_types:
            mod_name = bpy.types.Modifier.bl_rna.properties['type'].enum_items[mod_type].name
            mod_icon = bpy.types.Modifier.bl_rna.properties['type'].enum_items[mod_type].icon
            mod_id = bpy.types.Modifier.bl_rna.properties['type'].enum_items[mod_type].identifier

            modifier_button = modifier_space.operator(
                modifier_creation_operator.bl_idname, text=mod_name, icon=mod_icon)
            modifier_button.modifier_type = mod_id
            modifier_button.create_modifier = True
            modifier_button.remove_modifier = False


def UIPreset_ObjectTabUIWrapper(self, context):
    layout = self.layout
    addon_properties = context.window_manager.alx_session_properties
    show_modifier_list = addon_properties.ui_modifier_list_wrapper_toggle_display

    row = layout.row()
    row.prop(
        addon_properties,
        "ui_modifier_list_wrapper_toggle_display",
        text="ALX Modifier List",
        icon="TRIA_DOWN" if (show_modifier_list) else "TRIA_RIGHT",
        emboss=not show_modifier_list
    )

    if (show_modifier_list):
        UIPreset_ModifierList(layout, context)

    UIPreset_ObjectInfoList(layout, context)


def UIPreset_ObjectInfoList(layout: bpy.types.UILayout = None, context: bpy.types.Context = bpy.context):
    object_info = ALX_Info_System.info_dict

    layout = layout.box()

    info_column = layout.column()
    if (object_info is not None):
        for object, info in object_info.items():
            box = info_column.box()

            box.label(text=object)

            row = box.split(factor=0.05)
            row.separator()
            column = row.column()
            for info_type, info_text in info.items():
                if (info_type == "info"):
                    column.label(text="Info:", icon="INFO_LARGE")
                    for text in info_text:
                        column.label(text=text)

                if (info_type == "warning"):
                    column.label(text="Warning:", icon="WARNING_LARGE")
                    for text in info_text:
                        column.label(text=text)

                if (info_type == "error"):
                    column.label(text="Error:", icon="CANCEL_LARGE")
                    for text in info_text:
                        column.label(text=text)


# region Modifier


class Alx_UL_UIList_ObjectSelectionModifiers(bpy.types.UIList):
    """"""

    bl_idname = "ALX_UL_ui_list_object_selection_modifiers"

    def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data: bpy.types.AnyType, item: Alx_PG_PropertyGroup_ObjectSelectionListItem, icon: int, active_data: bpy.types.AnyType, active_property: str, index: int = 0, flt_flag: int = 0):

        self.use_filter_show = True

        item_object: bpy.types.Object = item.ObjectPointer

        object_slot_layout = layout.box()

        object_header = object_slot_layout.row()
        object_header.prop(
            item_object,
            "alx_modifier_expand_settings",
            text="",
            icon="TRIA_DOWN" if item_object.alx_modifier_expand_settings == True else "TRIA_RIGHT",
            emboss=False
        )
        object_header.label(text=item_object.name)
        if (item_object.type == "MESH") and (item_object.data.shape_keys is not None):
            object_header.label(text="MESH HAS SHAPE-KEYS", icon="WARNING_LARGE")

        modifier_items_layout = object_slot_layout.row()
        if (item_object.alx_modifier_expand_settings == True):
            modifier_items_layout.separator()
            modifier_layout = modifier_items_layout.column()

            for raw_object_modifier in item_object.modifiers:
                modifier_slots = modifier_layout.box().column()

                modifier_header = modifier_slots.row(align=True)

                icon_name = bpy.types.Modifier.bl_rna.properties['type'].enum_items.get(raw_object_modifier.type).icon
                show_options = item_object.alx_modifier_collection.get(f"{item_object.name}_{raw_object_modifier.name}").show_options

                modifier_change_settings = modifier_header.operator(
                    Alx_PT_Operator_ModifierChangeSettings.bl_idname,
                    icon="TRIA_DOWN" if (show_options) else "TRIA_RIGHT",
                    emboss=False,
                    depress=show_options
                )
                modifier_change_settings.object_name = item_object.name
                modifier_change_settings.modifier_name = raw_object_modifier.name

                modifier_delete_button: Alx_OT_Modifier_ManageOnSelected = modifier_header.operator(
                    Alx_OT_Modifier_ManageOnSelected.bl_idname,
                    icon="PANEL_CLOSE",
                    emboss=False
                )
                modifier_delete_button.object_pointer_reference = item_object.name
                modifier_delete_button.object_modifier_index = item_object.modifiers.find(raw_object_modifier.name)
                modifier_delete_button.create_modifier = False
                modifier_delete_button.apply_modifier = False
                modifier_delete_button.remove_modifier = True
                modifier_delete_button.move_modifier_up = False
                modifier_delete_button.move_modifier_down = False

                modifier_apply_button: Alx_OT_Modifier_ManageOnSelected = modifier_header.operator(
                    Alx_OT_Modifier_ManageOnSelected.bl_idname, icon="FILE_TICK", emboss=False)
                modifier_apply_button.object_pointer_reference = item_object.name
                modifier_apply_button.object_modifier_index = item_object.modifiers.find(
                    raw_object_modifier.name)
                modifier_apply_button.create_modifier = False
                modifier_apply_button.apply_modifier = True
                modifier_apply_button.remove_modifier = False
                modifier_apply_button.move_modifier_up = False
                modifier_apply_button.move_modifier_down = False

                if (item_object.alx_modifier_collection.get(f"{item_object.name}_{raw_object_modifier.name}").show_options == True):
                    UIPreset_ModifierSettings(
                        modifier_slots, raw_object_modifier, context, item_object)

                modifier_header.prop(
                    raw_object_modifier, "name", text="", icon=icon_name, emboss=True)

                modifier_header.prop(raw_object_modifier,
                                     "show_in_editmode", text="", emboss=True)
                modifier_header.prop(raw_object_modifier,
                                     "show_viewport", text="", emboss=True)
                modifier_header.prop(raw_object_modifier,
                                     "show_render", text="", emboss=True)

                modifier_move_up_button: Alx_OT_Modifier_ManageOnSelected = modifier_header.operator(
                    Alx_OT_Modifier_ManageOnSelected.bl_idname, icon="TRIA_UP")
                modifier_move_up_button.object_pointer_reference = item_object.name
                modifier_move_up_button.object_modifier_index = item_object.modifiers.find(
                    raw_object_modifier.name)
                modifier_move_up_button.create_modifier = False
                modifier_move_up_button.apply_modifier = False
                modifier_move_up_button.remove_modifier = False
                modifier_move_up_button.move_modifier_up = True
                modifier_move_up_button.move_modifier_down = False

                modifier_move_down_button = modifier_header.operator(
                    Alx_OT_Modifier_ManageOnSelected.bl_idname, icon="TRIA_DOWN")
                modifier_move_down_button.object_pointer_reference = item_object.name
                modifier_move_down_button.object_modifier_index = item_object.modifiers.find(
                    raw_object_modifier.name)
                modifier_move_down_button.create_modifier = False
                modifier_move_down_button.apply_modifier = False
                modifier_move_down_button.remove_modifier = False
                modifier_move_down_button.move_modifier_up = False
                modifier_move_down_button.move_modifier_down = True

                modifier_header.prop(raw_object_modifier, "use_pin_to_last",
                                     text="",
                                     icon="PINNED" if raw_object_modifier.use_pin_to_last == True else "UNPINNED",
                                     emboss=True)

            object_slot_layout.separator(factor=2.0)


def UIPreset_ModifierList(layout: bpy.types.UILayout = None, context: bpy.types.Context = bpy.context):

    layout.template_list(
        Alx_UL_UIList_ObjectSelectionModifiers.bl_idname,
        list_id="", dataptr=context.scene,
        propname="alx_object_selection_modifier",
        active_dataptr=context.scene,
        active_propname="alx_object_selection_modifier_index",
        maxrows=3
    )


# class WRAPPER_OT_BPYOPS_MODIFIER(bpy.types.Operator):
#     bl_idname = "alx.bpyops_modifier"
#     bl_label = ""
#     bl_options = {"UNDO"}

#     active_object: bpy.props.StringProperty()  # type:ignore
#     modifier_name: bpy.props.StringProperty()  # type:ignore
#     modifier_setting: bpy.props.StringProperty()  # type:ignore

#     def lambda_function(self, context, modifier_context):
#         context.view_layer.objects.active = modifier_context["active_object"]
#         for selected_object in context.selected_objects:
#             if (selected_object.name in [obj.name for obj in modifier_context["selected_objects"]]):
#                 selected_object.select_set(True)

#     def execute(self, context):
#         modifier_context = context.copy()

#         modifier_context["active_object"] = bpy.data.objects[self.active_object]

#         with context.temp_override(**modifier_context):
#             bpy.ops.object.multires_subdivide(modifier=self.modifier_name, mode=self.modifier_setting)

#         # self.lambda_function(context, modifier_context)
#         return {'FINISHED'}


def UIPreset_ModifierSettings(layout: bpy.types.UILayout = None, modifier: bpy.types.Modifier = None, context: bpy.types.Context = None, object: bpy.types.Object = None):
    if (layout is not None) and (modifier is not None):
        indented_layout = layout.row()
        indented_layout.separator(factor=2.0)

        mod_layout = indented_layout.column()
        mod_layout.separator()

        match modifier.type:

            case "SUBSURF":

                row = mod_layout.split(factor=0.75)
                row.prop(modifier, "subdivision_type", text="")
                row.prop(modifier, "show_only_control_edges", text="optimal")
                mod_layout.separator()

                row = mod_layout.row(align=True)
                row.prop(modifier, "levels", text="View")
                row.prop(modifier, "render_levels", text="Render")
                mod_layout.separator()

                row = mod_layout.row()
                column = row.column()
                column.prop(modifier, "use_limit_surface", text="Smoothest")
                column.prop(modifier, "quality")

                column = row.column()
                column.prop(modifier, "use_creases", text="Use Crease")
                column.prop(modifier, "use_custom_normals", text="Use C-Normals")

                column = mod_layout.column()
                row = column.split(factor=0.35)
                row.label(text="Smooth UV:")
                row.prop(modifier, "uv_smooth", text="")
                row = column.split(factor=0.35)
                row.label(text="Smooth Bounds:")
                row.prop(modifier, "boundary_smooth", text="")

            case "MULTIRES":
                row = mod_layout.row()
                # column = row.column()
                # column.prop(modifier, "levels", text="Viewport")
                # column.prop(modifier, "render_levels", text="Render")
                # column.prop(modifier, "sculpt_levels", text="Sculpt")

                # column = row.column()

                # subdivide = column.operator(WRAPPER_OT_BPYOPS_MODIFIER.bl_idname, text="Subdivide")
                # subdivide.active_object = object.name
                # subdivide.modifier_name = modifier.name
                # subdivide.modifier_setting = "CATMULL_CLARK"

                # subdivide_simple = column.operator(WRAPPER_OT_BPYOPS_MODIFIER.bl_idname, text="Subdivide Simple")
                # subdivide_simple.active_object = object.name
                # subdivide_simple.modifier_name = modifier.name
                # subdivide_simple.modifier_setting = "SIMPLE"

                # subdivide_linear = column.operator(WRAPPER_OT_BPYOPS_MODIFIER.bl_idname, text="Subdivide Linear")
                # subdivide_linear.active_object = object.name
                # subdivide_linear.modifier_name = modifier.name
                # subdivide_linear.modifier_setting = "LINEAR"

            case "BEVEL":
                row = layout.row().split(factor=0.33, align=True)

                row.prop(modifier, "offset_type", text="")
                row.prop(modifier, "width", text="width")
                row.prop(modifier, "segments", text="segments")
                layout.row().prop(modifier, "limit_method", text="")

                layout.row().prop(modifier, "miter_outer", text="miter outer")
                layout.row().prop(modifier, "harden_normals", text="harden")

            case "DATA_TRANSFER":
                modifier: bpy.types.DataTransferModifier

                split = mod_layout.row().split()
                row = split.row(align=True)
                row.prop(modifier, "object", text="")
                row.prop(modifier, "use_object_transform",
                         text="", icon="ORIENTATION_GLOBAL")

                row = split.row(align=True)
                row.prop(modifier, "mix_mode", text="")
                row.prop(modifier, "mix_factor", text="")

                row = mod_layout.row(align=True).split(factor=0.75)

                data_row = row.row()
                data_row.label(text="Type:")
                data_row.prop(modifier, "use_vert_data", text="vertex")
                data_row.prop(modifier, "use_edge_data", text="edge")
                data_row.prop(modifier, "use_poly_data", text="face")
                data_row.prop(modifier, "use_loop_data", text="loop")

                if (modifier.use_vert_data == True):
                    column = mod_layout.column()
                    column.row().prop(modifier, "data_types_verts")
                    column.prop(modifier, "vert_mapping", text="Mapping")

                    row = column.row().split(factor=0.5)

                    if ("VGROUP_WEIGHTS" in modifier.data_types_verts):
                        column = row.column()
                        column.label(text="VGroup Source:")
                        column.prop(
                            modifier, "layers_vgroup_select_src", text="")
                        column.label(text="VGroup Mapping:")
                        column.prop(
                            modifier, "layers_vgroup_select_dst", text="")
                    if ("COLOR_VERTEX" in modifier.data_types_verts):
                        column = row.column()
                        column.label(text="Color Source:")
                        column.prop(
                            modifier, "layers_vcol_vert_select_src", text="")
                        column.label(text="Color Mapping:")
                        column.prop(
                            modifier, "layers_vcol_vert_select_dst", text="")

            case "SMOOTH":
                pass

            case "SHRINKWRAP":
                modifier: bpy.types.ShrinkwrapModifier = modifier
                row = layout.row().split(factor=0.5, align=True)
                row.prop(modifier, "target", text="")

                row = layout.row().split(factor=0.5, align=True)
                row.prop(modifier, "wrap_method", text="")
                row.prop(modifier, "wrap_mode", text="")

                row = layout.row()
                row.prop(modifier, "use_negative_direction")
                row.prop(modifier, "use_positive_direction")

        if (modifier.type == "DATA_TRANSFER"):
            row = layout.row()
            row.prop(modifier, "object", text="")
            split = row.row(align=True)
            split.prop(modifier, "use_object_transform", text="", toggle=True, icon="OBJECT_ORIGIN")

            row = layout.row()
            row.prop(modifier, "use_vert_data", text="")

            row = layout.row()
            row.prop(modifier, "use_edge_data", text="")
            row.prop(modifier, "data_types_edges")

            row = layout.row()

            row.prop(modifier, "data_types_loops")

            row = layout.row()

            row.prop(modifier, "data_types_polys")

        if (modifier.type == "MIRROR"):
            row = layout.column()

            row.prop(modifier, "mirror_object", text="object")
            row.prop(modifier, "use_clip", text="clip")
            row.prop(modifier, "use_mirror_merge", text="merge")
            row.prop(modifier, "merge_threshold", text="")

        if (modifier.type == "ARMATURE"):
            layout.row().prop(modifier, "object", text="")
            layout.row().prop(modifier, "use_deform_preserve_volume", text="preserve volume")

        if (modifier.type == "BOOLEAN"):
            row = layout.row()
            row.prop(modifier, "object", text="")
            row.prop(modifier, "operation", expand=True)

        if (modifier.type == "TRIANGULATE"):
            layout.row().prop(modifier, "keep_custom_normals", text="keep normals")

        if (modifier.type == "SOLIDIFY"):
            row = layout.row().split(factor=0.5, align=True)
            row.prop(modifier, "thickness")
            row.prop(modifier, "offset")

        if (modifier.type == "DISPLACE"):
            row = layout.row().split(factor=0.034)
            row.separator()

            options_layout = row.box()
            row = options_layout.row()
            row.prop(modifier, "strength")
            row.prop(modifier, "mid_level")

# endregion


def UIPreset_EnumButtons(layout: bpy.types.UILayout = None, primary_icon: str = "NONE", data=None, data_name: str = ""):
    enum_items = get_enum_property_items(data, data_name)

    enum_layout = layout.row()
    icons_column = enum_layout.column()
    buttons_column = enum_layout.column()
    buttons_column.scale_y = 1.125

    for enum_item in enum_items:
        if (enum_item.identifier != "CLOSED"):
            icons_column.label(icon=primary_icon)
        else:
            icons_column.label(text="")

    buttons_column.prop(data, data_name, expand=True, emboss=False)
