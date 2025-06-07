import bpy

from .info_system import ALX_Info_System
from .interface import ALX_Alexandria_General_Panel, ALX_Shapeky_Toolset
from .interface.ALX_Alexandria_Layouts import UIPreset_ObjectTabUIWrapper
from .modules.ALXAddonUpdater.ALXAddonUpdater.ALX_AddonUpdater import \
    Alx_Addon_Updater
from .modules.ALXModuleManager.ALXModuleManager.ALX_ModuleManager import \
    Alx_Module_Manager
from .reorganize_later import ALX_Handlers, AlxProperties
from .UnlockedTools import AlxUnlockedModeling

bl_info = {
    "name": "AlxOverHaul",
    "author": "Valerie Bosco[Valy Arhal]",
    "description": "",
    "warning": "[Heavly Under Development] And Subject To Substantial Changes",
    "version": (0, 8, 2),
    "blender": (4, 0, 0),
    "category": "3D View",
    "location": "[Ctrl Alt A] General Menu, [Shift Alt S] Pivot Menu, [Tab] Auto Mode Pie Menu",
    "doc_url": "https://github.com/Valerie-Bosco/AlxOverHaul/wiki",
    "tracker_url": "https://github.com/Valerie-Bosco/AlxOverHaul/issues",
}


module_loader = Alx_Module_Manager(
    path=__path__,
    globals=globals(),
    mute=True
)
addon_updater = Alx_Addon_Updater(
    path=__path__,
    bl_info=bl_info,
    engine="Github",
    engine_user_name="Valerie-Bosco",
    engine_repo_name="AlxOverHaul",
    manual_download_website="https://github.com/Valerie-Bosco/AlxOverHaul/releases/tag/main_branch_latest"
)


def RegisterProperties():
    bpy.types.WindowManager.alx_session_properties = bpy.props.PointerProperty(
        type=AlxProperties.Alx_PG_PropertyGroup_SessionProperties)
    bpy.types.WindowManager.alx_vmc_session_properties = bpy.props.PointerProperty(
        type=AlxProperties.Alx_PG_VMC_SessionProperties)

    bpy.types.Scene.alx_object_selection_properties = bpy.props.CollectionProperty(
        type=AlxProperties.Alx_PG_PropertyGroup_ObjectSelectionListItem)
    bpy.types.Scene.alx_object_selection_properties_index = bpy.props.IntProperty(
        default=0)

    bpy.types.Scene.alx_object_selection_modifier = bpy.props.CollectionProperty(
        type=AlxProperties.Alx_PG_PropertyGroup_ObjectSelectionListItem)
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
        type=ALX_Alexandria_General_Panel.Alx_PG_PropertyGroup_ModifierSettings)

    bpy.types.WindowManager.alx_info_system_data = bpy.props.PointerProperty(
        type=ALX_Info_System.ALX_PG_PropertyGroup_InfoSystemData)


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

    del bpy.types.WindowManager.alx_info_system_data


def RegisterHandlers():
    bpy.app.handlers.load_post.append(
        ALX_Handlers.AlxMain_load_post
    )
    bpy.app.handlers.save_post.append(
        ALX_Handlers.ALX_MainSavePost
    )

    bpy.app.handlers.load_post.append(
        ALX_Handlers.AlxAddonKeymapHandler
    )
    bpy.app.handlers.load_post.append(
        ALX_Handlers.AlxUpdateSceneSelectionObjectList
    )
    bpy.app.handlers.depsgraph_update_post.append(
        ALX_Handlers.AlxUpdateSceneSelectionObjectList
    )


def UnRegisterHandlers():
    bpy.app.handlers.load_post.remove(
        ALX_Handlers.AlxMain_load_post
    )
    bpy.app.handlers.save_post.remove(
        ALX_Handlers.ALX_MainSavePost
    )

    bpy.app.handlers.load_post.remove(
        ALX_Handlers.AlxAddonKeymapHandler)
    bpy.app.handlers.load_post.remove(
        ALX_Handlers.AlxUpdateSceneSelectionObjectList
    )
    bpy.app.handlers.depsgraph_update_post.remove(
        ALX_Handlers.AlxUpdateSceneSelectionObjectList
    )


def register():
    module_loader.developer_register_modules()
    addon_updater.register_addon_updater(mute=True)

    bpy.types.OBJECT_PT_context_object.prepend(UIPreset_ObjectTabUIWrapper)
    bpy.types.DATA_PT_shape_keys.prepend(ALX_Shapeky_Toolset.ALX_MT_ShapeKeyToolset.draw)

    RegisterProperties()
    RegisterHandlers()

    bpy.context.preferences.use_preferences_save = True


def unregister():
    module_loader.developer_unregister_modules()
    addon_updater.unregister_addon_updater()

    bpy.types.OBJECT_PT_context_object.remove(UIPreset_ObjectTabUIWrapper)
    bpy.types.DATA_PT_shape_keys.remove(ALX_Shapeky_Toolset.ALX_MT_ShapeKeyToolset.draw)

    UnRegisterProperties()
    UnRegisterHandlers()


if __name__ == "__main__":
    register()
