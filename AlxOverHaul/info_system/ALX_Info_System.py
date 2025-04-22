import bpy

from ..A_definitions import modifiers

info_dict = dict()


def add_warning(info_dict: dict, object: bpy.types.Object, warning: str):
    if (object.name not in info_dict.keys()):
        info_dict[object.name] = dict()

    if ("warning" not in info_dict[object.name].keys()):
        info_dict[object.name]["warning"] = list()

    info_dict[object.name]["warning"].append(warning)


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
