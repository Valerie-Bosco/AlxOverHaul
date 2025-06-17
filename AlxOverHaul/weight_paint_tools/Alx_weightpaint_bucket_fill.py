import bpy


class Alx_PG_PropertyGroup_WeightPaint_BucketFill_Properties(bpy.types.PropertyGroup):
    """"""

    weight: bpy.props.FloatProperty(default=1.0, min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)  # type:ignore


class ALX_PT_Panel_WeightPaint_BucketFill(bpy.types.Panel):
    """"""

    bl_label = ""
    bl_idname = "ALX_PT_panel_tool_weight_paint_bucket_fill"

    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context: bpy.types.Context):
        if (context is not None):
            return (context.area.type == "VIEW_3D") and (context.mode == "PAINT_WEIGHT")
        else:
            return False

    def draw(self, context: bpy.types.Context):
        properties: Alx_PG_PropertyGroup_WeightPaint_BucketFill_Properties = context.scene.alx_tool_weight_paint_bucket_fill_properties

        layout: bpy.types.UILayout = self.layout

        layout.prop(properties, "weight")


class ALX_OT_WeightPaint_BucketFill(bpy.types.Operator):
    """"""

    bl_label = "WeightPaint - Bucket Fill"
    bl_idname = "alx.operator_weight_paint_bucket_fill"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.weight_paint_object is not None)

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):
        properties: Alx_PG_PropertyGroup_WeightPaint_BucketFill_Properties = context.scene.alx_tool_weight_paint_bucket_fill_properties

        if (context.mode != "PAINT_WEIGHT"):
            return {"CANCELLED"}

        if (context.workspace.tools.from_space_view3d_mode("PAINT_WEIGHT", create=False).idname != "alx.workspacetool_weightpaint_bucket_fill"):
            return {"CANCELLED"}

        if (event.type == "LEFTMOUSE"):
            if (event.alt):
                return {"PASS_THROUGH"}
            if (event.direction == "ANY"):
                return {"RUNNING_MODAL"}

            if (context.area is not None) and (context.area.type == "VIEW_3D"):
                if (context.weight_paint_object is not None):
                    wp_object = context.weight_paint_object
                    if (wp_object.vertex_groups.active is not None):
                        wp_object.vertex_groups.active.add([vert.index for vert in wp_object.data.vertices], weight=context.scene.alx_tool_weight_paint_bucket_fill_properties.weight, type="REPLACE")

                    else:
                        self.report({"INFO"}, "[object][missing] | [active][vertex group]")
            return {"PASS_THROUGH"}

        if (event.type == "RIGHTMOUSE") and (context.area is not None) and (context.area.type == "VIEW_3D"):
            bpy.ops.wm.call_panel(name=ALX_PT_Panel_WeightPaint_BucketFill.bl_idname, keep_open=True)
            return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


class ALX_WST_WeightPaint_BucketFill(bpy.types.WorkSpaceTool):
    """"""

    bl_space_type = "VIEW_3D"
    bl_context_mode = "PAINT_WEIGHT"
    bl_icon = "brush.paint_texture.fill"

    bl_idname = "alx.workspacetool_weightpaint_bucket_fill"
    bl_label = "Bucket Fill"

    after = "None"
    separator = True
    group = False

    bl_keymap = (
        ("alx.operator_weight_paint_bucket_fill", {"type": "RIGHTMOUSE", "value": "PRESS"},
         {"properties": []}),
    )
