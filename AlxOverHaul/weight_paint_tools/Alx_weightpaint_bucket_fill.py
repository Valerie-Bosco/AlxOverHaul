import bpy


class Alx_OT_WeightPaint_BucketFill(bpy.types.Operator):
    """"""

    bl_label = "WeightPaint - Bucket Fill"
    bl_idname = "alx.operator_weight_paint_bucket_fill"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    # weight: bpy.props.FloatProperty(name="Weight" default=1.0, min=0.0, max=1.0)  # type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.weight_paint_object is not None)

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        if (context.weight_paint_object is not None):
            wp_object = context.weight_paint_object
            if (wp_object.vertex_groups.active is not None):
                wp_object.vertex_groups.active.add([vert.index for vert in wp_object.data.vertices], weight=1.0, type="ADD")

            else:
                self.report({"INFO"}, "[object][missing] | [active][vertex group]")
        return {"FINISHED"}


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
        ("alx.operator_weight_paint_bucket_fill", {"type": "LEFTMOUSE", "value": "PRESS"},
         {"properties": []}),
    )
