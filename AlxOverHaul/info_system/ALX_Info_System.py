import bpy

from ..A_definitions import modifiers

info_dict = dict()


class ALX_PG_PropertyGroup_InfoSystemData(bpy.types.PropertyGroup):

    info_system_ui_show_panel: bpy.props.BoolProperty()  # type:ignore

    info_system_ui_tabs: bpy.props.EnumProperty(
        default="WARNING",
        items=[
            ("INFO", "Info", "", "INFO_LARGE", 1),
            ("WARNING", "Warning", "", "WARNING_LARGE", 1 << 1),
            ("ERROR", "Error", "", "CANCEL_LARGE", 1 << 2)
        ]
    )  # type:ignore


def INFO_Generator(context: bpy.types.Context):
    context_objects = context.view_layer.objects
    global info_dict
    info_dict = dict()

    for object in context_objects:
        if ((object.scale[0], object.scale[1], object.scale[2]) != (1.0, 1.0, 1.0)):
            add_warning(info_dict, object, "Object has non-uniform scale")

        match object.type:
            case "MESH":
                if (object.data is not None) and (object.data.shape_keys is not None):
                    if (len(object.modifiers) > 0) and (len([0 for modifier in object.modifiers if (modifier.type not in modifiers.TD_modifier_allowed_with_shapekeys)]) > 0):
                        add_warning(info_dict, object, "Mesh has shape-keys with incompatible modifiers")


def add_info():
    pass


def add_warning(info_dict: dict, object: bpy.types.Object, warning: str):
    if ("warning" not in info_dict.keys()):
        info_dict["warning"] = dict()

    if (object.name not in info_dict["warning"].keys()):
        info_dict["warning"][object.name] = list()

    info_dict["warning"][object.name].append(warning)


def add_error():
    pass
