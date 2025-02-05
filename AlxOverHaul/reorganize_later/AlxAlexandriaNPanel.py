import bpy

from ..armature_tools import Alx_rigging_tools
from ..MeshTools import AlxShapekeyTools, AlxVertexGroupTools
from ..pose_tools import Alx_pose_tools
from ..UVTools import AlxUDIMTools


class ALX_PT_UI_Addon_ToolShelf(bpy.types.Panel):
    """"""

    bl_label = "Alx Toolshelf"
    bl_idname = "ALX_PT_panel_ui_addon_tool_shelf"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    bl_category = "Alx3D"
    bl_order = 0

    def draw(self, context: bpy.types.Context):
        mainlayout = self.layout

        mesh_tools_panel: bpy.types.UILayout
        mesh_tools_header, mesh_tools_panel = mainlayout.panel("ALX_PT_compact_panel_mesh_tools", default_closed=True)
        mesh_tools_header.label(text="Mesh Tools:")
        if (mesh_tools_panel is not None):
            row = mesh_tools_panel.row()
            row.separator()
            layout = row.column()

            layout.label(text="Vertex Groups:")
            layout.operator(AlxVertexGroupTools.Alx_OT_Mesh_VertexGroup_Clean.bl_idname, text="Clean VGroups")

            layout.label(text="ShapeKeys:")
            layout.operator(AlxShapekeyTools.Alx_OT_Shapekey_TransferShapekeysToTarget.bl_idname, text="Transfer Shapekeys")

            layout.label(text="UV/UDIMs:")
            layout.operator(AlxUDIMTools.Alx_OT_UVTools_udim_square_compressor.bl_idname, text="Compress UDIMs")

        armature_tools_panel: bpy.types.UILayout
        armature_tools_header, armature_tools_panel = mainlayout.panel("ALX_PT_compact_panel_armature_tools", default_closed=True)
        armature_tools_header.label(text="Armature Tools:")
        if (armature_tools_panel is not None):
            row = armature_tools_panel.row()
            row.separator()
            layout = row.column()

            layout.label(text="Pose:")
            layout.operator(Alx_pose_tools.Alx_OT_Armature_Pose_ToggleConstraints.bl_idname, text="Toggle Pose Constraints")
            layout.operator(Alx_pose_tools.Alx_OT_Armature_MatchIKByMirroredName.bl_idname, text="Symmetrize IK")

        vtuber_panel: bpy.types.UILayout
        vtuber_header, vtuber_panel = mainlayout.panel("ALX_PT_compact_panel_vtuber_tools", default_closed=True)
        vtuber_header.label(text="VTuber Tools:")
        if (vtuber_panel is not None):
            row = vtuber_panel.row()
            row.separator()
            layout = row.column()

            layout.label(text="ShapeKeys:")
            layout.operator(AlxShapekeyTools.Alx_OT_Shapekey_AddEmptyShapeKeys.bl_idname, text="Add Empty Shapekeys")

            layout.label(text="Rigging:")
            layout.operator(Alx_rigging_tools.Alx_OT_Armature_BoneChainOnSelection.bl_idname, text="Autorig Strip")


class ALX_PT_UI_Addon_HelpSection(bpy.types.Panel):
    """"""

    bl_label = "Help?"
    bl_idname = "ALX_PT_panel_ui_addon_help_section"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    bl_category = "Alx3D"
    bl_order = 1

    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.label(text="What Tools are Available?")
        layout.separator()

        help_section_info = {
            "Menus:": ["\u2022 Alexandria General [Ctrl+Alt+A]",
                       "\u2022 Alexandria Pivot [Shift+Alt+S]"
                       ],
            "Weight Paint:": ["\u2022 Bucket Fill"]
        }

        for section in help_section_info.keys():
            info_section = layout.column()
            info_section.label(text=section)

            for line in help_section_info[section]:
                paragraph = layout.row().split(factor=0.05)
                paragraph.separator()
                paragraph.label(text=line)
