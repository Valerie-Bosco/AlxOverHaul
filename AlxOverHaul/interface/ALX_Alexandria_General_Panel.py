import bpy
from bpy_extras import node_utils

from ..definitions.AlxTypesDefinition import (TD_modifier_deform_types,
                                              TD_modifier_generate_types,
                                              TD_modifier_modifiy_types,
                                              TD_modifier_physics_types)
from ..MeshTools.AlxModifierOperators import (Alx_OT_Modifier_ApplyReplace,
                                              Alx_OT_Modifier_BatchVisibility,
                                              Alx_OT_Modifier_ManageOnSelected)
from ..pose_tools.Alx_pose_tools import Alx_OT_Armature_Pose_SetPosePosition
from ..reorganize_later.AlxObjectOperator import ALX_OT_Object_UnlockedQOrigin
from ..reorganize_later.AlxProperties import (
    Alx_PG_PropertyGroup_ObjectSelectionListItem,
    Alx_PG_PropertyGroup_SessionProperties)
from ..reorganize_later.AlxVisibilityOperators import \
    Alx_OT_Scene_VisibilityIsolator
from ..UITools.Alx_OT_UI_SimpleDesigner import Alx_OT_UI_SimpleDesigner
from ..utilities.Alx_armature_utils import Get_ActiveObject_Skeleton
from .ALX_Alexandria_Layouts import (Alx_UL_UIList_ObjectSelectionModifiers,
                                     UIPreset_EnumButtons,
                                     UIPreset_ModifierCreateList,
                                     UIPreset_OverlayToggles,
                                     UIPreset_PosePosition,
                                     UIPreset_VisibilityIsolator)


class Alx_UL_UIList_ObjectSelectionProperties(bpy.types.UIList):
    """"""

    bl_idname = "ALX_UL_ui_list_object_selection_properties"

    def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data: bpy.types.AnyType, item: Alx_PG_PropertyGroup_ObjectSelectionListItem, icon: int, active_data: bpy.types.AnyType, active_property: str, index: int = 0, flt_flag: int = 0):
        self.use_filter_show = True

        layout.ui_units_x = 10
        item_box = layout.column()

        box_column = item_box.column(align=True)

        header = box_column.row(align=True)
        header.prop(item.ObjectPointer, "name", text="",
                    icon="OBJECT_DATA", emboss=True)

        header.prop(item.ObjectPointer, "show_name",
                    text="", icon="SORTALPHA", emboss=True)
        header.prop(item.ObjectPointer, "show_axis", text="",
                    icon="EMPTY_ARROWS", emboss=True)
        if (item.ObjectPointer.type in ["MESH", "META"]):
            header.prop(item.ObjectPointer, "show_wire", text="",
                        icon="MOD_WIREFRAME", emboss=True)
        header.prop(item.ObjectPointer, "show_in_front",
                    text="", icon="OBJECT_HIDDEN", emboss=True)

        body = box_column.row(align=True)

        body.prop(item.ObjectPointer, "display_type", text="")
        if (item.ObjectPointer.type in ["MESH", "META"]):
            body.prop(item.ObjectPointer, "color", text="")

        item_box.separator(factor=2.0)


class Alx_PG_PropertyGroup_ModifierSettings(bpy.types.PropertyGroup):
    """"""
    object_name: bpy.props.StringProperty(name="", default="")  # type:ignore
    object_modifier: bpy.props.StringProperty(
        name="", default="")  # type:ignore
    show_options: bpy.props.BoolProperty(name="", default=False)  # type:ignore


class Alx_PT_Panel_AlexandriaGeneralPanel(bpy.types.Panel):
    """"""

    bl_label = "Alexandria General Panel"
    bl_idname = "ALX_PT_panel_alexandria_general_panel"

    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context: bpy.types.Context):
        # region Variable Shortcuts
        addon_properties: Alx_PG_PropertyGroup_SessionProperties = context.window_manager.alx_session_properties
        context_skeleton: bpy.types.Object = Get_ActiveObject_Skeleton(context)
        # endregion

        # region Overrides
        override_area = [
            area for area in context.window.screen.areas if area.type == "VIEW_3D"]
        b_override_v3d_area_exists = len(override_area) > 0

        override_region = [region for region in override_area[0].regions if region.type == 'WINDOW'] if (
            b_override_v3d_area_exists) else None
        b_override_v3d_region_exists = len(override_area) > 0

        override_window = bpy.context.window
        override_screen = override_window.screen
        override_area = [area for area in override_screen.areas if area.type == "VIEW_3D"]
        override_region = [region for region in override_area[0].regions if region.type == 'WINDOW']

        # endregion

        # region Layouts
        layout: bpy.types.UILayout = self.layout.row()
        self.layout.ui_units_x = 25.0

        if (addon_properties.alexandria_general_panel_tabs == "MODIFIER") or (addon_properties.alexandria_general_panel_modifier_sidetabs != "CLOSED"):
            layout = self.layout.row().split(factor=25 / self.layout.ui_units_x)

        main_page_layout = layout.column()
        side_page_layout = layout.row()

        header_layout = main_page_layout.column()
        header_layout.label(icon="GRIP")
        header_grid = header_layout.grid_flow(columns=2, even_columns=True, even_rows=True)

        body_layout = main_page_layout.column()
# endregion

# region Header
        # header slot one
        header_slot_one = header_grid.column()

        with context.temp_override(window=override_window, area=override_area[0], region=override_region[0]):
            row = header_slot_one.row().split(factor=0.5)
            UIPreset_PosePosition(row, context_skeleton, Alx_OT_Armature_Pose_SetPosePosition.bl_idname)
            header_slot_one.separator()

            row = header_slot_one.row().split(factor=0.5)
            UIPreset_VisibilityIsolator(row, addon_properties, Alx_OT_Scene_VisibilityIsolator.bl_idname)
            header_slot_one.separator()

            UIPreset_OverlayToggles(header_slot_one, context)
            header_slot_one.separator()

# endregion

# region Body
        main_layout = main_page_layout.row()

        tabs = main_layout.column().prop(addon_properties, "alexandria_general_panel_tabs",
                                         icon_only=True, expand=True, emboss=False)
        tabs_panels = main_layout.column()

        header_layout.separator()

        if (addon_properties.alexandria_general_panel_tabs == "OBJECT"):
            ObjectTabBox = tabs_panels.column()

            ObjectTabBox.template_list(Alx_UL_UIList_ObjectSelectionProperties.bl_idname, list_id="", dataptr=context.scene, propname="alx_object_selection_properties",
                                       active_dataptr=context.scene, active_propname="alx_object_selection_properties_index", type="GRID", columns=2)

        if (addon_properties.alexandria_general_panel_tabs == "ARMATURE"):
            ArmatureTabBox = tabs_panels.column()

            if (context_skeleton is not None):
                armature_display_options = ArmatureTabBox.column()
                armature_display_options.row().prop(bpy.data.armatures.get(
                    context_skeleton.data.name), "display_type", expand=True)
                armature_display_options.prop(bpy.data.armatures.get(
                    context_skeleton.data.name), "show_names", text="names")
                armature_display_options.prop(bpy.data.armatures.get(
                    context_skeleton.data.name), "show_bone_custom_shapes", text="custom shapes")
                armature_display_options.prop(bpy.data.armatures.get(
                    context_skeleton.data.name), "show_bone_colors", text="colors")

                armature_display_options.prop(bpy.data.armatures.get(
                    context_skeleton.data.name), "show_axes", text="axis")

        if (addon_properties.alexandria_general_panel_tabs == "MODIFIER"):
            ModifierTabBox = tabs_panels.row().split(factor=0.925)

            column = ModifierTabBox.column()
            row = column.row()
            row.operator(Alx_OT_Modifier_ApplyReplace.bl_idname,
                         text="Apply-Replace Modifier")
            row.operator(Alx_OT_Modifier_BatchVisibility.bl_idname,
                         text="Batch Visibility")
            column.template_list(Alx_UL_UIList_ObjectSelectionModifiers.bl_idname, list_id="", dataptr=context.scene,
                                 propname="alx_object_selection_modifier", active_dataptr=context.scene, active_propname="alx_object_selection_modifier_index", maxrows=3)

            modifier_sidetabs = ModifierTabBox.column()
            UIPreset_EnumButtons(layout=modifier_sidetabs, primary_icon="MODIFIER",
                                 data=addon_properties, data_name="alexandria_general_panel_modifier_sidetabs")

            match addon_properties.alexandria_general_panel_modifier_sidetabs:
                case "STANDARD":
                    UIPreset_ModifierCreateList(
                        layout=side_page_layout.row(),
                        modifiers_types=[
                            ["Modify", TD_modifier_modifiy_types],
                            ["Generate", TD_modifier_generate_types],
                            ["Deform", TD_modifier_deform_types]
                        ],
                        modifier_creation_operator=Alx_OT_Modifier_ManageOnSelected)

                case "PHYSICS":
                    UIPreset_ModifierCreateList(
                        layout=side_page_layout.row(),
                        modifiers_types=[
                            ["Physics", TD_modifier_physics_types]
                        ],
                        modifier_creation_operator=Alx_OT_Modifier_ManageOnSelected)

                case "FAVORITE":
                    pass

        if (addon_properties.alexandria_general_panel_tabs == "ALXOPERATORS"):
            AlxOperatorsTabBox = tabs_panels.column()

        if (addon_properties.alexandria_general_panel_tabs == "RENDER") and (b_override_v3d_area_exists):
            RenderTabBox = tabs_panels.column()

            if (override_region is not None):
                with context.temp_override(window=override_window, area=override_area[0], region=override_region[0]):

                    render_engine_option = RenderTabBox.row()
                    render_engine_option.prop(
                        context.scene.render, "engine", text="")
                    render_engine_option.prop(
                        context.area.spaces.active.shading, "type", text="", expand=True)

                    if (context.area.spaces.active.shading.type == "SOLID"):
                        matcap_preview = RenderTabBox.column()
                        matcap_preview.row().prop(context.area.spaces.active.shading, "light", expand=True)

                        material_display = matcap_preview.row().split(factor=0.5)

                        material_display.template_icon_view(
                            context.area.spaces.active.shading, "studio_light", scale=3.2)
                        material_display.grid_flow(columns=2, align=True).prop(
                            context.area.spaces.active.shading, "color_type", expand=True)

                if (context.area.spaces.active.shading.type == "MATERIAL"):
                    scene_shading_options = RenderTabBox.column()

                    if (context.area.spaces.active.shading.use_scene_world == False):
                        material_preview = scene_shading_options.row().split(factor=0.5)
                        material_preview.template_icon_view(
                            context.area.spaces.active.shading, "studio_light", scale=4.3, scale_popup=3.0)
                        scene_world_shading = material_preview.column()
                        scene_world_shading.prop(
                            context.area.spaces.active.shading, "studiolight_rotate_z", text="rotation")
                        scene_world_shading.prop(
                            context.area.spaces.active.shading, "studiolight_intensity", text="intensity")
                        scene_world_shading.prop(
                            context.area.spaces.active.shading, "studiolight_background_alpha", text="opacity")
                        scene_world_shading.prop(
                            context.area.spaces.active.shading, "studiolight_background_blur", text="blur")

                    scene_shading_options.prop(
                        context.area.spaces.active.shading, "use_scene_lights", text="scene lights")
                    scene_shading_options.prop(
                        context.area.spaces.active.shading, "use_scene_world", text="scene world")

                    if (context.area.spaces.active.shading.use_scene_world == True):
                        scene_shading_options.row().prop(context.scene.world, "use_nodes",
                                                         text="Use Scene World Nodes", toggle=True)

                        if (context.scene.world.use_nodes == True):
                            if (context.scene.world.node_tree is not None):
                                WorldMaterial = context.scene.world.node_tree
                                MaterialOutput = context.scene.world.node_tree.get_output_node(
                                    "ALL")
                                Surface = node_utils.find_node_input(
                                    MaterialOutput, "Surface")
                                scene_shading_options.column().template_node_view(
                                    WorldMaterial, MaterialOutput, Surface)

                if (context.area.spaces.active.shading.type == "RENDERED"):
                    scene_shading_options = RenderTabBox.column()

                    if (context.area.spaces.active.shading.use_scene_world_render == False):
                        material_preview = scene_shading_options.row().split(factor=0.5)
                        material_preview.template_icon_view(
                            context.area.spaces.active.shading, "studio_light", scale=4.3, scale_popup=3.0)
                        scene_world_shading = material_preview.column()
                        scene_world_shading.prop(
                            context.area.spaces.active.shading, "studiolight_rotate_z", text="rotation")
                        scene_world_shading.prop(
                            context.area.spaces.active.shading, "studiolight_intensity", text="intensity")
                        scene_world_shading.prop(
                            context.area.spaces.active.shading, "studiolight_background_alpha", text="opacity")
                        scene_world_shading.prop(
                            context.area.spaces.active.shading, "studiolight_background_blur", text="blur")

                    scene_shading_options.prop(
                        context.area.spaces.active.shading, "use_scene_lights_render", text="scene lights")
                    scene_shading_options.prop(
                        context.area.spaces.active.shading, "use_scene_world_render", text="scene world")

                    if (context.area.spaces.active.shading.use_scene_world_render == True):
                        scene_shading_options.row().prop(context.scene.world, "use_nodes",
                                                         text="Use Scene world Nodes", toggle=True)

                        if (context.scene.world.use_nodes == True):
                            if (context.scene.world.node_tree is not None):
                                WorldMaterial = context.scene.world.node_tree
                                MaterialOutput = context.scene.world.node_tree.get_output_node(
                                    "ALL")
                                Surface = node_utils.find_node_input(
                                    MaterialOutput, "Surface")
                                scene_shading_options.column().template_node_view(
                                    WorldMaterial, MaterialOutput, Surface)

                if (context.area.spaces.active.shading.type == "SOLID"):
                    solid_shading_options = RenderTabBox.column()
                    solid_shading_options.row().prop(
                        context.area.spaces.active.shading, "show_backface_culling")
                    solid_shading_options.row().prop(context.area.spaces.active.shading, "show_cavity")
                    if (context.area.spaces.active.shading.show_cavity == True):
                        solid_shading_options.row().prop(
                            context.area.spaces.active.shading, "cavity_type", text="")
                        cavity_options = solid_shading_options.row()
                        cavity_options.prop(
                            context.area.spaces.active.shading, "curvature_ridge_factor", text="ridge")
                        cavity_options.prop(
                            context.area.spaces.active.shading, "curvature_valley_factor", text="valley")

            if (context.scene.render.engine in ["BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"]):
                eevee_viewport_sample = RenderTabBox.row(
                    align=True).split(factor=0.4)
                eevee_viewport_sample.prop(
                    context.scene.eevee, "use_taa_reprojection", text="Denoise")
                eevee_viewport_sample.prop(
                    context.scene.eevee, "taa_samples", text="Viewport")
                eevee_render_sample = RenderTabBox.row(
                    align=True).split(factor=0.4)
                eevee_render_sample.separator()
                eevee_render_sample.prop(
                    context.scene.eevee, "taa_render_samples", text="Render")

            if (context.scene.render.engine == "CYCLES"):
                cycles_samples = RenderTabBox.row(align=True)
                cycles_samples.prop(context.scene.cycles,
                                    "preview_samples", text="Viewport")
                cycles_samples.prop(context.scene.cycles,
                                    "samples", text="Render")

        if (addon_properties.alexandria_general_panel_tabs == "UI_DESIGNER"):
            AlxUIDesignerTabBox = tabs_panels.column()

            AlxUIDesignerTabBox.row().operator(
                Alx_OT_UI_SimpleDesigner.bl_idname, text="UI Designer")

            # AreaUITypeSelector.template_header()
            #

        #     WindowAreaSpace.row().label(text="Split Vertical:")
        #     SplitVertical = WindowAreaSpace.row()
        #     SplitHalf = SplitVertical.operator(Alx_OT_UI_SimpleDesigner.bl_idname, text="1/2")
        #     SplitHalf.UseAreaSplit = True
        #     # SplitHalf.direction = "VERTICAL"
        #     # SplitHalf.cursor = context.area.width/2

        #     # # SplitVertical.operator("screen.area_split", text="1/3")
        #     # # SplitHalf.direction = "VERTICAL"
        #     # # SplitHalf.factor = 0.33
        #     # # SplitVertical.operator("screen.area_split", text="1/4")
        #     # # SplitHalf.direction = "VERTICAL"
        #     # # SplitHalf.factor = 0.25

        #     # # bpy.ops.screen.area_split()

        #     AlxSpace.label(text=context.area.type)

        if (addon_properties.alexandria_general_panel_tabs == "SETTINGS"):
            AlxSettingsTabBox = tabs_panels.column()

            # AlxSettingsTabBox.prop(AddonProperties, "View3d_Pan_Use_Shift_GRLess", toggle=True)
            # AlxSettingsTabBox.prop(AddonProperties, "View3d_Rotate_Use_GRLess", toggle=True)
            # AlxSettingsTabBox.prop(panel, "View3d_Zoom_Use_GRLess", toggle=True)

            # theme : bpy.types.Theme = context.preferences.themes[0]
            # if (theme is not None):
            #     AlxSettingsTabBox.split(factor=0.33).prop(theme.user_interface.wcol_box, "inner", text="Set alpha to 1.0")

            # AlxSettingsTabBox.operator("script.reload", text="reload scripts")
        #     AlxSpace = LayoutSpace.box().row()

        # ScenePropertyColumn.row().prop(context.space_data.overlay, "show_stats", text="Statistics", toggle=True)

        #         ScenePropertyColumn.row().prop(context.tool_settings, "use_edge_path_live_unwrap", text="Auto Unwrap", icon="UV")

        #         ScenePropertyColumn.row(align=True).prop(context.tool_settings, "vertex_group_user", expand=True)
        #         ScenePropertyColumn.row().prop(context.tool_settings, "use_auto_normalize", text="Auto Normalize", icon="MOD_VERTEX_WEIGHT")

        # MMenuSectionR.row().operator(AlxOperators.Alx_OT_Mesh_EditAttributes.bl_idname, text="Edit Attributes")
        #


class Alx_PT_Scene_GeneralPivot(bpy.types.Panel):
    """"""

    bl_label = "scene general pivot"
    bl_idname = "ALX_PT_panel_scene_general_pivot"

    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        return True

    def draw(self, context):
        self.layout.ui_units_x = 20.0

        PivotLayout = self.layout.row().split(factor=0.5)

        pivot_column = PivotLayout.column()
        pivot_column.prop(
            context.scene.transform_orientation_slots[0], "type", expand=True)
        pivot_column.prop(context.tool_settings,
                          "transform_pivot_point", expand=True)
        pivot_column.prop(context.space_data.overlay, "grid_scale")
        pivot_column.prop(context.space_data.overlay, "grid_subdivisions")

        pivot_column.operator(
            ALX_OT_Object_UnlockedQOrigin.bl_idname, text="Q-Origin")

        snapping_column = PivotLayout.column()

        if (bpy.app.version[0] == 3):
            snapping_column.prop(context.tool_settings,
                                 "snap_elements", expand=True)

        if ((bpy.app.version[0] == 4) and (bpy.app.version[1] in [0, 1, 2])):
            snapping_column.prop(context.tool_settings,
                                 "snap_elements_base", expand=True)
            snapping_column.prop(context.tool_settings,
                                 "snap_elements_individual", expand=True)

        snapping_column.prop(context.tool_settings, "use_snap", text="Snap")
        snapping_column.prop(context.tool_settings, "snap_target", expand=True)

        snapping_column.row().label(text="Snap to:")
        snap_affect_type = snapping_column.row(align=True)
        snap_affect_type.prop(context.tool_settings,
                              "use_snap_translate", text="Move", toggle=True)
        snap_affect_type.prop(context.tool_settings,
                              "use_snap_rotate", text="Rotate", toggle=True)
        snap_affect_type.prop(context.tool_settings,
                              "use_snap_scale", text="Scale", toggle=True)

        snapping_column.prop(context.tool_settings, "use_snap_align_rotation")
        snapping_column.prop(context.tool_settings, "use_snap_grid_absolute")
