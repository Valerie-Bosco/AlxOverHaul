import bpy

def notify_context_mode_update():
    pass

def notify_workspace_tool_update():
    workspace_tool_lambda()

def workspace_tool_lambda():
    pass
    # override_window = bpy.context.window
    # override_screen = override_window.screen
    # override_area = [area for area in override_screen.areas if area.type == "VIEW_3D"]
    # override_region = [region for region in override_area[0].regions if region.type == 'WINDOW']

    # with bpy.context.temp_override(window=override_window, area=override_area[0], region=override_region[0]):
    #     if (bpy.context.workspace.tools.get("alx.workspace_unlocked_modeling_tool") is not None):
    #         bpy.ops.alx.operator_unlocked_modeling_tool("INVOKE_DEFAULT")
    #     else:
    #         print(f"from {__name__}: Tool is None")