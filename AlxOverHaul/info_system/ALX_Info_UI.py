import bpy

from . import ALX_Info_System


def UIPreset_ObjectInfoList(layout: bpy.types.UILayout = None, context: bpy.types.Context = bpy.context):
    object_info = ALX_Info_System.info_dict
    info_system_data = context.window_manager.alx_info_system_data

    layout = layout.box()

    layout.row().prop(info_system_data, "info_system_ui_tabs", icon_only=False, expand=True, emboss=True)
    column = layout.row().column()

    if (info_system_data.info_system_ui_tabs == "INFO"):
        pass

    if (info_system_data.info_system_ui_tabs == "WARNING"):
        if ("warning" in object_info.keys()):
            for object, warnings in object_info["warning"].items():
                box = column.box()

                row = box.row()
                row.separator()
                select_op: ALX_OT_OBJECT_SelectObject = row.operator(ALX_OT_OBJECT_SelectObject.bl_idname, text=object, emboss=True)
                select_op.object_name = object
                row.separator()

                row = box.split(factor=0.05)
                row.separator()

                obj_warnings_col = row.column()
                for warning in warnings:
                    obj_warnings_col.label(text=warning)

    if (info_system_data.info_system_ui_tabs == "ERROR"):
        pass


class ALX_OT_OBJECT_SelectObject(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_select_object"

    object_name: bpy.props.StringProperty()  # type:ignore

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context: bpy.types.Context):
        if (self.object_name is not None) and (self.object_name != ""):
            object = context.view_layer.objects.get(self.object_name)

            if (object is not None):
                for object in context.selected_objects:
                    object.select_set(False)

                object.select_set(True)

        return {"FINISHED"}
