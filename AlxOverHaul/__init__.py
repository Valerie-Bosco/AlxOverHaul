import importlib

import bpy

from . import AlxAlexandriaGeneralPanel, AlxHandlers, AlxProperties
from .Alx_Module_Manager import Alx_Module_Manager
from .modules.addon_updater_system.addon_updater import Alx_Addon_Updater
from .UnlockedTools import AlxUnlockedModeling

bl_info = {
    "name": "AlxOverHaul",
    "author": "Valerie Bosco[Valy Arhal]",
    "description": "",
    "warning": "[Heavly Under Development] And Subject To Substantial Changes",
    "version": (0, 7, 3),
    "blender": (4, 0, 0),
    "category": "3D View",
    "location": "[Ctrl Alt A] General Menu, [Shift Alt S] Pivot Menu, [Tab] Auto Mode Pie Menu",
    "doc_url": "https://github.com/Valerie-Bosco/AlxOverHaul/wiki",
    "tracker_url": "https://github.com/Valerie-Bosco/AlxOverHaul/issues",
}


module_loader = Alx_Module_Manager(__path__, globals())
module_loader.developer_load_modules()


addon_updater = Alx_Addon_Updater(__path__[0], bl_info, "Github", "Valerie-Bosco", "AlxOverHaul", "https://github.com/Valerie-Bosco/AlxOverHaul/releases")


def RegisterProperties():
    bpy.types.WindowManager.alx_session_properties = bpy.props.PointerProperty(
        type=AlxProperties.Alx_PG_PropertyGroup_SessionProperties)
    bpy.types.WindowManager.alx_vmc_session_properties = bpy.props.PointerProperty(
        type=AlxProperties.Alx_PG_VMC_SessionProperties)

    bpy.types.Scene.alx_object_selection_properties = bpy.props.CollectionProperty(
        type=AlxAlexandriaGeneralPanel.Alx_PG_PropertyGroup_ObjectSelectionListItem)
    bpy.types.Scene.alx_object_selection_properties_index = bpy.props.IntProperty(
        default=0)

    bpy.types.Scene.alx_object_selection_modifier = bpy.props.CollectionProperty(
        type=AlxAlexandriaGeneralPanel.Alx_PG_PropertyGroup_ObjectSelectionListItem)
    bpy.types.Scene.alx_object_selection_modifier_index = bpy.props.IntProperty(
        default=0)

    bpy.types.Scene.alx_scene_isolator_visibility_object_list = []
    bpy.types.Scene.alx_scene_isolator_visibility_collection_list = []

    bpy.types.Object.alx_self_bmesh_datablock = []
    bpy.types.Scene.alx_draw_handler_unlocked_modeling = None
    bpy.types.Scene.alx_tool_unlocked_modeling_properties = bpy.props.PointerProperty(
        type=AlxUnlockedModeling.Alx_PG_PropertyGroup_UnlockedModelingProperties)

    bpy.types.Object.alx_particle_surface_object = bpy.props.PointerProperty(
        type=bpy.types.Object)
    bpy.types.Object.alx_particle_generator_source_object = bpy.props.PointerProperty(
        type=bpy.types.Object)

    bpy.types.Object.alx_modifier_expand_settings = bpy.props.BoolProperty(
        default=False)
    bpy.types.Object.alx_modifier_collection = bpy.props.CollectionProperty(
        type=AlxAlexandriaGeneralPanel.Alx_PG_PropertyGroup_ModifierSettings)


def UnRegisterProperties():
    del bpy.types.WindowManager.alx_session_properties

    del bpy.types.Scene.alx_object_selection_properties
    del bpy.types.Scene.alx_object_selection_properties_index

    del bpy.types.Scene.alx_object_selection_modifier
    del bpy.types.Scene.alx_object_selection_modifier_index

    del bpy.types.Scene.alx_scene_isolator_visibility_object_list
    del bpy.types.Scene.alx_scene_isolator_visibility_collection_list

    del bpy.types.Object.alx_self_bmesh_datablock
    del bpy.types.Scene.alx_draw_handler_unlocked_modeling
    del bpy.types.Scene.alx_tool_unlocked_modeling_properties

    del bpy.types.Object.alx_particle_surface_object
    del bpy.types.Object.alx_particle_generator_source_object

    del bpy.types.Object.alx_modifier_expand_settings
    del bpy.types.Object.alx_modifier_collection


def RegisterHandlers():
    bpy.app.handlers.load_post.append(AlxHandlers.AlxMain_load_post)
    bpy.app.handlers.depsgraph_update_post.append(
        AlxHandlers.AlxMain_depsgraph_update_post)

    bpy.app.handlers.load_post.append(AlxHandlers.AlxMsgBusSubscriptions)
    bpy.app.handlers.load_post.append(AlxHandlers.AlxAddonKeymapHandler)
    bpy.app.handlers.load_post.append(
        AlxHandlers.AlxUpdateSceneSelectionObjectList)
    bpy.app.handlers.depsgraph_update_post.append(
        AlxHandlers.AlxUpdateSceneSelectionObjectList)


def UnRegisterHandlers():
    bpy.app.handlers.load_post.remove(AlxHandlers.AlxMsgBusSubscriptions)
    bpy.app.handlers.load_post.remove(AlxHandlers.AlxAddonKeymapHandler)
    bpy.app.handlers.load_post.remove(
        AlxHandlers.AlxUpdateSceneSelectionObjectList)
    bpy.app.handlers.depsgraph_update_post.remove(
        AlxHandlers.AlxUpdateSceneSelectionObjectList)


def register():
    module_loader.developer_load_modules
    module_loader.developer_register_modules(mute=True)
    addon_updater.register_addon_updater(mute=True)

    RegisterProperties()
    RegisterHandlers()

    bpy.context.preferences.use_preferences_save = True


def unregister():
    module_loader.developer_unregister_modules()
    addon_updater.unregister_addon_updater()

    UnRegisterProperties()
    UnRegisterHandlers()


if __name__ == "__main__":
    register()
