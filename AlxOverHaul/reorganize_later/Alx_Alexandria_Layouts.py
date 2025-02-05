import bpy

from ..utilities.AlxUtilities import get_enum_property_items

LABEL = "LABEL_"
SEPARATOR = "SEPARATOR"


def UIPreset_PosePosition(parent_layout: bpy.types.UILayout = None, skeleton_object: bpy.types.Object = None, operator_bl_idname: str = ""):
    layout = parent_layout.row().split(factor=0.5)
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


def UIPreset_ModifierSettings(layout: bpy.types.UILayout = None, modifier: bpy.types.Modifier = None, context: bpy.types.Context = None, object: bpy.types.Object = None):
    if (layout is not None) and (modifier is not None):
        indented_layout = layout.row()
        indented_layout.separator(factor=2.0)

        mod_layout = indented_layout.column()
        match modifier.type:
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

        # if (modifier.type == "DATA_TRANSFER"):
        #     row = layout.row()
        #     row.prop(modifier, "object", text="")
        #     split = row.row(align=True)
        #     split.prop(modifier, "use_object_transform", text="", toggle=True, icon="OBJECT_ORIGIN")
        #

        #     row = layout.row()
        #     row.prop(modifier, "use_vert_data", text="")

        #     row = layout.row()
        #     row.prop(modifier, "use_edge_data", text="")
        #     row.prop(modifier, "data_types_edges")

        #     row = layout.row()

        #     row.prop(modifier, "data_types_loops")

        #     row = layout.row()

        #     row.prop(modifier, "data_types_polys")

        if (modifier.type == "MIRROR"):
            row = layout.column()

            row.prop(modifier, "mirror_object", text="object")
            row.prop(modifier, "use_clip", text="clip")
            row.prop(modifier, "use_mirror_merge", text="merge")
            row.prop(modifier, "merge_threshold", text="")

        if (modifier.type == "SUBSURF"):
            layout.row().prop(modifier, "show_only_control_edges", text="optimal")

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


def UIPreset_ModifierList(layout: bpy.types.UILayout = None, modifiers_types: list[list[str, list[str]]] = [], modifier_creation_operator: bpy.types.Operator = None):
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
