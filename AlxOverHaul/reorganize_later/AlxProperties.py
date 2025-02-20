import bpy


class Alx_PG_PropertyGroup_SessionProperties(bpy.types.PropertyGroup):

    alexandria_general_panel_b_show_modifier_creation_panel: bpy.props.BoolProperty(
        default=False)  # type:ignore
    alexandria_general_panel_b_show_modifier_favorite_panel: bpy.props.BoolProperty(
        default=False)  # type:ignore

    alexandria_general_panel_tabs: bpy.props.EnumProperty(
        default="OBJECT",
        items=[
            ("OBJECT", "Object", "", "OBJECT_DATAMODE", 1),
            ("ARMATURE", "Armature", "", "ARMATURE_DATA", 1 << 1),
            ("MODIFIER", "Modifier", "", "MODIFIER", 1 << 2),
            ("ALXOPERATORS", "AlxOPS", "", "PLUGIN", 1 << 3),
            ("RENDER", "Render", "", "SCENE", 1 << 4),
            ("UI_DESIGNER", "UI Designer", "", "WINDOW", 1 << 5),
            ("SETTINGS", "Settings", "", "PREFERENCES", 1 << 6)
        ]
    )  # type:ignore

    alexandria_general_panel_modifier_sidetabs: bpy.props.EnumProperty(
        default="CLOSED",
        items=[
            ("CLOSED", "", "", "X", 1),
            ("STANDARD", "", "", "ADD", 1 << 1),
            ("PHYSICS", "", "", "PHYSICS", 1 << 2),
            ("FAVORITE", "", "", "SOLO_ON", 1 << 3)
        ]
    )  # type:ignore

    operator_object_and_collection_isolator_visibility_target: bpy.props.EnumProperty(
        default={"VIEWPORT"},
        options={'ENUM_FLAG'},
        items=[
            ("VIEWPORT", "Viewport", "", "RESTRICT_VIEW_OFF", 1),
            ("RENDER", "Render", "", "RESTRICT_RENDER_OFF", 1 << 1)
        ]
    )  # type:ignore

    operator_object_and_collection_isolator_type_target: bpy.props.EnumProperty(
        default={"OBJECT"},
        options={'ENUM_FLAG'},
        items=[
            ("OBJECT", "Object", "", "OBJECT_DATAMODE", 1),
            ("COLLECTION", "Collection", "", "OUTLINER_COLLECTION", 1 << 1)
        ]
    )  # type:ignore

    operator_uvtools_uv_map_transfer__source_object: bpy.props.PointerProperty(
        type=bpy.types.Object, name="source")  # type:ignore
    operator_uvtools_uv_map_transfer__target_object: bpy.props.PointerProperty(
        type=bpy.types.Object, name="target")  # type:ignore

    udim_texture_compressor_texture_target: bpy.props.PointerProperty(
        type=bpy.types.Image)  # type:ignore

    vertex_reproject_target_object: bpy.props.PointerProperty(
        type=bpy.types.Object)  # type:ignore
    vertex_reproject_object_use_deform: bpy.props.BoolProperty(
        default=False)  # type:ignore
    vertex_reproject_object_use_cage: bpy.props.BoolProperty(
        default=False)  # type:ignore

    shapekey_transfer_source_object: bpy.props.PointerProperty(
        type=bpy.types.Object)  # type:ignore
    shapekey_transfer_target_object: bpy.props.PointerProperty(
        type=bpy.types.Object)  # type:ignore

    ui_simple_designer_user_ui_type: bpy.props.EnumProperty(items=[
        ("VIEW_3D", "View 3d", "", "VIEW3D", 1),
        ("IMAGE_EDITOR", "Image Editor", "", "IMAGE", 1 << 1),
        ("UV", "UV Editor", "", "UV", 1 << 2),
        ("CompositorNodeTree", "Compositor", "", "NODE_COMPOSITING", 1 << 3),
        ("TextureNodeTree", "Texture Editor", "", "NODE_TEXTURE", 1 << 4),
        ("GeometryNodeTree", "GeoNode Editor", "", "GEOMETRY_NODES", 1 << 5),
        ("ShaderNodeTree", "Shader Editor", "", "NODE_MATERIAL", 1 << 6),
        ("SEQUENCE_EDITOR", "Sequencer", "", "SEQUENCE", 1 << 7),
        ("CLIP_EDITOR", "Clip Editor", "", "TRACKER", 1 << 8),
        ("DOPESHEET", "DopeSheet", "", "ACTION", 1 << 9),
        ("TIMELINE", "Timeline", "", "TIME", 1 << 10),
        ("FCURVES", "FCurve Editor", "", "GRAPH", 1 << 11),
        ("DRIVERS", "Drivers Editor", "", "DRIVER", 1 << 12),
        ("NLA_EDITOR", "NLA Editor", "", "NLA", 1 << 13),
        ("TEXT_EDITOR", "Text Editor", "", "TEXT", 1 << 14),
        ("CONSOLE", "Console", "", "CONSOLE", 1 << 15),
        ("INFO", "Info Panel", "", "INFO", 1 << 16),
        ("OUTLINER", "Outliner", "", "OUTLINER", 1 << 17),
        ("PROPERTIES", "Properties", "", "PROPERTIES", 1 << 18),
        ("FILES", "Files", "", "FILEBROWSER", 1 << 19),
        ("ASSETS", "Assets", "", "ASSET_MANAGER", 1 << 20),
        ("SPREADSHEET", "Spreadsheet", "", "SPREADSHEET", 1 << 21),
        ("PREFERENCES", "Preferences", "", "PREFERENCES", 1 << 22)
    ])  # type:ignore

    operator_armature_merge_source: bpy.props.PointerProperty(type=bpy.types.Object)  # type:ignore

    operator_armature_merge_target: bpy.props.PointerProperty(type=bpy.types.Object)  # type:ignore

    ui_modifier_list_wrapper_toggle_display: bpy.props.BoolProperty(default=True)  # type:ignore


class Alx_PG_VMC_SessionProperties(bpy.types.PropertyGroup):
    vmc_server_target_ip: bpy.props.StringProperty(
        name="",
        default="127.0.0.1"
    )  # type:ignore
    vmc_server_target_port: bpy.props.IntProperty(
        name="",
        default=39539,
        min=1025,
        max=65535
    )  # type:ignore

    vmc_mesh_blendshapes_target: bpy.props.PointerProperty(
        type=bpy.types.Mesh
    )  # type:ignore
    vmc_skeleton_pose_target: bpy.props.PointerProperty(
        type=bpy.types.Armature)  # type:ignore


class Alx_Object_Selection_ListItem(bpy.types.PropertyGroup):
    """"""
    name: bpy.props.StringProperty()  # type:ignore
    ObjectPointer: bpy.props.PointerProperty(
        type=bpy.types.Object
    )  # type:ignore


class Alx_PG_PropertyGroup_ObjectSelectionListItem(bpy.types.PropertyGroup):
    """"""
    name: bpy.props.StringProperty()  # type:ignore
    ObjectPointer: bpy.props.PointerProperty(
        type=bpy.types.Object)  # type:ignore
