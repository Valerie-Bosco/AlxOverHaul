from pathlib import Path
from .AlxJson import json_serialize_keymaps


import bpy
from .AlxCallbacks import notify_context_mode_update, notify_workspace_tool_update
from .AlxKeymapUtils import AlxCreateKeymaps


def armature_handler_lambda():
    pass


@bpy.app.handlers.persistent
def AlxMain_depsgraph_update_post(context):
    pass
    # json_serialize_keymaps([Path("E:\ProjectSovereign\Blender\Addon\AlxOverHaul\AlxOverHaul\keymap_json_test.json")], bpy.context.window_manager.keyconfigs.user.keymaps)


@bpy.app.handlers.persistent
def AlxMain_load_post(scene):
    armature_handler_lambda()


@bpy.app.handlers.persistent
def AlxMsgBusSubscriptions(self, context: bpy.types.Context):
    override_window = bpy.context.window
    override_screen = override_window.screen
    override_area = [
        area for area in override_screen.areas if area.type == "VIEW_3D"]
    override_region = [
        region for region in override_area[0].regions if region.type == 'WINDOW']

    with bpy.context.temp_override(window=override_window, area=override_area[0], region=override_region[0]):
        bpy.msgbus.subscribe_rna(key=bpy.context.path_resolve("mode", False), owner=bpy.context.object, args=(
        ), notify=notify_context_mode_update, options={"PERSISTENT"})
        bpy.msgbus.subscribe_rna(key=bpy.context.workspace.path_resolve(
            "tools", False), owner=bpy.context.workspace, args=(), notify=notify_workspace_tool_update, options={"PERSISTENT"})


@bpy.app.handlers.persistent
def AlxAddonKeymapHandler(self, context):
    addon_keymaps_lambda()


def addon_keymaps_lambda():
    AlxCreateKeymaps()


def AlxUpdateSceneSelectionObjectListLambda():
    SelectedObjects = [object for scene in bpy.data.scenes for object in scene.objects if (
        object.select_get() == True)]

    for scene in bpy.data.scenes:
        scene.alx_object_selection_properties.clear()
        scene.alx_object_selection_modifier.clear()

    for scene in bpy.data.scenes:
        for Object in SelectedObjects:
            Item = scene.alx_object_selection_properties.add()
            Item.name = Object.name

            Item.ObjectPointer = Object
            if (Object.type in ["MESH", "FONT", "LATTICE", "CURVE", "SURFACE", "GPENCIL", "VOLUME"]):
                Item = scene.alx_object_selection_modifier.add()
                Item.name = Object.name
                Item.ObjectPointer = Object

    for Object in SelectedObjects:
        for Modifier in Object.modifiers:
            mod = Object.alx_modifier_collection.add()
            mod.name = f"{Object.name}_{Modifier.name}"
            mod.object_modifier = Modifier.name


@bpy.app.handlers.persistent
def AlxUpdateSceneSelectionObjectList(self, context: bpy.types.Context):
    AlxUpdateSceneSelectionObjectListLambda()
