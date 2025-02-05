import bpy
from ..reorganize_later.AlxProperties import Alx_PG_PropertyGroup_SessionProperties


class Alx_PT_Panel_UI_SimpleDesignerUserOptions(bpy.types.Panel):
    """"""

    bl_label = ""
    bl_idname = "ALX_PT_panel_ui_simple_designer_user_options"

    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def draw(self, context: bpy.types.Context):
        properties: Alx_PG_PropertyGroup_SessionProperties = context.window_manager.alx_session_properties

        self.layout.ui_units_x = 25.0

        grid_flow = self.layout.column_flow(columns=4)

        grid_flow.prop(properties, "ui_simple_designer_user_ui_type", expand=True, emboss=False)


class Alx_OT_UI_SimpleDesigner(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_ui_simple_designer"
    bl_description = "relative to area under mouse and mouse position \n key [C] close area \n Key [S] swaps area \n Key [T] area swap type selector \n key [V]/[H] vertical/horizontal area split"

    context_area: bpy.types.Area = None

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def get_mouse_area(self, screen: bpy.types.Screen, mouse_x, mouse_y):
        for area in screen.areas:
            if (area.x <= mouse_x) and ((area.x + area.width) >= mouse_x) and (area.y <= mouse_y) and ((area.y + area.height) >= mouse_y):
                return area
        return None

    def draw(self, context: bpy.types.Context):
        self.layout.prop(self, "area_ui_type", expand=True)

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):
        if (event.type == "ESC"):
            return {"CANCELLED"}

        if (event.type == "C") and (event.value == "PRESS"):
            self.context_area = self.get_mouse_area(screen=context.window.screen, mouse_x=event.mouse_x, mouse_y=event.mouse_y)

            with context.temp_override(window=context.window, area=self.context_area):
                try:
                    bpy.ops.screen.area_close()
                except:
                    pass

            return {"RUNNING_MODAL"}

        if (event.type == "MOUSEMOVE"):
            return {"PASS_THROUGH"}

        if (event.type == "V") and (event.value == "PRESS"):
            self.context_area = self.get_mouse_area(screen=context.window.screen, mouse_x=event.mouse_x, mouse_y=event.mouse_y)

            with context.temp_override(window=context.window, area=self.context_area):
                try:
                    factor = ((event.mouse_x - self.context_area.x) / self.context_area.width) if ((self.context_area.x + self.context_area.width) != 0.0) else 0.5
                    bpy.ops.screen.area_split(direction="VERTICAL", factor=factor)
                except:
                    pass

            return {"RUNNING_MODAL"}

        if (event.type == "H") and (event.value == "PRESS"):
            self.context_area = self.get_mouse_area(screen=context.window.screen, mouse_x=event.mouse_x, mouse_y=event.mouse_y)

            with context.temp_override(window=context.window, area=self.context_area):
                try:
                    factor = ((event.mouse_y - self.context_area.y) / self.context_area.height) if ((self.context_area.y + self.context_area.height) != 0.0) else 0.5
                    bpy.ops.screen.area_split(direction="HORIZONTAL", factor=factor)
                except:
                    pass

            return {"RUNNING_MODAL"}

        if (event.type == "S") and (event.value == "PRESS"):
            self.context_area = self.get_mouse_area(screen=context.window.screen, mouse_x=event.mouse_x, mouse_y=event.mouse_y)

            with context.temp_override(window=context.window, area=self.context_area):
                properties: Alx_PG_PropertyGroup_SessionProperties = context.window_manager.alx_session_properties
                self.context_area.ui_type = properties.ui_simple_designer_user_ui_type

            return {"RUNNING_MODAL"}

        if (event.type == "T") and (event.value == "PRESS"):
            self.context_area = self.get_mouse_area(screen=context.window.screen, mouse_x=event.mouse_x, mouse_y=event.mouse_y)

            with context.temp_override(window=context.window, area=self.context_area):
                bpy.ops.wm.call_panel(name=Alx_PT_Panel_UI_SimpleDesignerUserOptions.bl_idname)
            return {"RUNNING_MODAL"}

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
