import bpy

from .UnlockedTools import AlxUnlockedObjectModes

from . import Alx_preferences
from . import AlxAlexandriaGeneralPanel

AlxAddonKeymaps = []


def AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="", ItemidName="", OperatorID="", MapType="", Key="", UseShift=False, UseCtrl=False, UseAlt=False, TriggerType="PRESS", Active=False):
    """KeyconfigSource : [Blender, Blender addon, Blender user]"""
    if (KeyconfigSource != "") and (ConfigSpaceName != ""):
        try:
            WindowManager = bpy.context.window_manager
            match KeyconfigSource:
                case "Blender":
                    DefaultKeyConfigs = WindowManager.keyconfigs.default
                case "Blender addon":
                    DefaultKeyConfigs = WindowManager.keyconfigs.addon
                case "Blender user":
                    DefaultKeyConfigs = WindowManager.keyconfigs.user

            DefaultKeyMaps = DefaultKeyConfigs.keymaps
            KeymapItems = DefaultKeyMaps[ConfigSpaceName].keymap_items
            for KeymapItem in KeymapItems:
                if (OperatorID == ""):
                    if (KeymapItem is not None) and (KeymapItem.idname == ItemidName):
                        if (MapType != ""):
                            KeymapItem.map_type = MapType
                        if (Key != ""):
                            KeymapItem.type = Key
                        KeymapItem.shift = UseShift
                        KeymapItem.ctrl = UseCtrl
                        KeymapItem.alt = UseAlt
                        KeymapItem.value = TriggerType
                        KeymapItem.active = Active

                if (OperatorID != ""):
                    if (KeymapItem is not None) and (KeymapItem.properties is not None) and (KeymapItem.idname == ItemidName) and (KeymapItem.properties.name == OperatorID):
                        if (MapType != ""):
                            KeymapItem.map_type = MapType
                        if (Key != ""):
                            KeymapItem.type = Key
                        KeymapItem.shift = UseShift
                        KeymapItem.ctrl = UseCtrl
                        KeymapItem.alt = UseAlt
                        KeymapItem.value = TriggerType
                        KeymapItem.active = Active
        except Exception as error:
            pass


def AlxKeymapRegister(keymap_call_type="", config_space_name="", space_type="EMPTY", region_type="WINDOW", addon_class=None, key="NONE", key_modifier="NONE", use_shift=False, use_ctrl=False, use_alt=False, trigger_type="PRESS", **kwargs):
    """
    Available keymap_call_type: ["DEFAULT", "OPERATOR", "MENU", "PANEL", "PIE"]
    """

    wm = bpy.context.window_manager
    kmc = wm.keyconfigs.addon

    keymap_call_id = None
    match keymap_call_type:
        case "DEFAULT":
            keymap_call_id = addon_class
        case "OPERATOR":
            keymap_call_id = addon_class.bl_idname
        case "MENU":
            keymap_call_id = "wm.call_menu"
        case "PANEL":
            keymap_call_id = "wm.call_panel"
        case "PIE":
            keymap_call_id = "wm.call_menu_pie"

    Keymap: bpy.types.KeyMap = kmc.keymaps.new(name=config_space_name, space_type=space_type, region_type=region_type)
    KeymapItem = Keymap.keymap_items.new(idname=keymap_call_id, type=key, key_modifier=key_modifier, shift=use_shift, ctrl=use_ctrl, alt=use_alt, value=trigger_type, head=True)

    if (keymap_call_type in ["PANEL", "MENU", "PIE"]):
        KeymapItem.properties.name = addon_class.bl_idname

        # for property, value in kwargs.items():
        #     if (hasattr(KeymapItem.properties, f"{property}")):
        #         setattr(KeymapItem.properties, property, value)

    AlxAddonKeymaps.append((Keymap, KeymapItem))


def AlxCreateKeymaps():
    if (Alx_preferences.AlxGetPreferences().View3d_Pan_Use_Shift_GRLess == True):
        AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="3D View", ItemidName="view3d.move", MapType="KEYBOARD", Key="GRLESS", UseShift=True, Active=True)
    if (Alx_preferences.AlxGetPreferences().View3d_Pan_Use_Shift_GRLess == False):
        AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="3D View", ItemidName="view3d.move", MapType="MOUSE", Key="MIDDLEMOUSE", UseShift=True, Active=True)

    if (Alx_preferences.AlxGetPreferences().View3d_Rotate_Use_GRLess == True):
        AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="3D View", ItemidName="view3d.rotate", MapType="KEYBOARD", Key="GRLESS", Active=True)
    if (Alx_preferences.AlxGetPreferences().View3d_Rotate_Use_GRLess == False):
        AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="3D View", ItemidName="view3d.rotate", MapType="MOUSE", Key="MIDDLEMOUSE", Active=True)

    if (Alx_preferences.AlxGetPreferences().View3d_Zoom_Use_GRLess == True):
        AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="3D View", ItemidName="view3d.zoom", MapType="KEYBOARD", Key="GRLESS", UseCtrl=True, Active=True)
    if (Alx_preferences.AlxGetPreferences() .View3d_Zoom_Use_GRLess == False):
        AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="3D View", ItemidName="view3d.zoom", MapType="MOUSE", Key="MIDDLEMOUSE", UseCtrl=True, Active=True)

    AlxKeymapRegister(keymap_call_type="DEFAULT", config_space_name="Window", region_type="WINDOW", addon_class="wm.window_fullscreen_toggle", key="F11", use_alt=True, trigger_type="CLICK")
    AlxKeymapRegister(keymap_call_type="DEFAULT", config_space_name="Window", region_type="WINDOW", addon_class="scripts.reload", key="F8", trigger_type="CLICK")

    AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="Mesh", ItemidName="mesh.select_more", MapType="MOUSE", Key="WHEELUPMOUSE", UseCtrl=True, Active=True)
    AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="Mesh", ItemidName="mesh.select_less", MapType="MOUSE", Key="WHEELDOWNMOUSE", UseCtrl=True, Active=True)
    AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="Mesh", ItemidName="wm.call_menu", OperatorID="VIEW3D_MT_edit_mesh_merge", Active=False)
    AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="Mesh", ItemidName="mesh.dupli_extrude_cursor", Active=False)

    AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="Armature", ItemidName="armature.align", Active=False)

    AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="Object Non-modal", ItemidName="object.mode_set", Active=False)
    AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="Image", ItemidName="object.mode_set", Active=False)
    AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="Object Non-modal", ItemidName="view3d.object_mode_pie_or_toggle", Active=False)
    AlxEditKeymaps(KeyconfigSource="Blender addon", ConfigSpaceName="Object Non-modal", ItemidName="wm.call_menu_pie", OperatorID="MACHIN3_MT_modes_pie", Active=False)

    AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="Mesh", ItemidName="transform.tosphere", Active=False)
    AlxEditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="3D View Tool: Edit Mesh, To Sphere", ItemidName="transform.tosphere", Active=False)

    AlxKeymapRegister(keymap_call_type="PIE", config_space_name="3D View", space_type="VIEW_3D", addon_class=AlxUnlockedObjectModes.Alx_MT_MenuPie_UnlockedObjectModes, key="TAB", trigger_type="PRESS")
    AlxKeymapRegister(keymap_call_type="PANEL", config_space_name="Window", region_type="WINDOW", addon_class=AlxAlexandriaGeneralPanel.Alx_PT_Panel_AlexandriaGeneralPanel, key="A", use_ctrl=True, use_alt=True, trigger_type="CLICK")
    AlxKeymapRegister(keymap_call_type="PANEL", config_space_name="3D View", space_type="VIEW_3D", addon_class=AlxAlexandriaGeneralPanel.Alx_PT_Scene_GeneralPivot, key="S", use_shift=True, use_alt=True, trigger_type="CLICK")
