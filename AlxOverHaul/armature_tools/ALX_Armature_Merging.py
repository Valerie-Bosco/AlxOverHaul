import bpy


class ALX_OT_Armature_MergeArmature(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_armature_merge_armature"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def execute(self, context: bpy.types.Context):
        session_properties = context.window_manager.alx_session_properties

        source = session_properties.operator_armature_merge_source
        source_data = source.data
        source_bones = [bone for bone in source_data.bones]

        transfer_target = session_properties.operator_armature_merge_target
        transfer_target_data = transfer_target.data
        transfer_target_bones = [bone for bone in transfer_target_data.bones]

        if (source is not None) and (transfer_target is not None):
            bone_transfer_list = [bone.name for bone in source_bones if (bone.name not in {target_bone.name for target_bone in transfer_target_bones})]

            bpy.ops.object.mode_set(mode="OBJECT")
            for selected_object in context.selected_objects:
                selected_object.select_set(False)
            context.view_layer.objects.active = transfer_target
            bpy.ops.object.mode_set(mode="EDIT")

            print([bone for bone in bone_transfer_list])

            for bone_name in bone_transfer_list:
                if (source_bones[source_bones.index(bone_name)].parent is not None) and (source_bones[source_bones.index(bone_name)].parent.name in transfer_target_bones):
                    name = bone_transfer_list.pop(bone_name)

                    bone = transfer_target_data.edit_bones.new(bone_name)

                    #             bone.parent = transfer_target.data.bones.get(source.data.bones.get(bone_name).parent.name)
                    #             bone.use_connect = source.data.bones.get(bone_name).use_connect
                    #             bone.head = source.bones.get(bone_name).head
                    #             bone.tail = source.bones.get(bone_name).tail

        return {"FINISHED"}

    def draw(self, context: bpy.types.Context):
        layout: bpy.types.UILayout = self.layout

        session_properties = context.window_manager.alx_session_properties

        layout.prop(session_properties, "operator_armature_merge_source", text="Source")
        layout.prop(session_properties, "operator_armature_merge_target", text="Target")

    def invoke(self, context: bpy.types.Context, event):
        wm: bpy.types.WindowManager = context.window_manager
        return wm.invoke_props_dialog(self)
