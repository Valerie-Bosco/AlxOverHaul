import bpy

from ..utilities.Alx_Armature_Utils import (AlxCloneIKBoneLimitOnChain,
                                            AlxCloneIKSettings,
                                            Get_ActiveObject_Skeleton,
                                            Get_PoseBone_Always_Left,
                                            Get_PoseBone_Always_Right,
                                            Get_PoseBone_Opposite)


class Alx_OT_Armature_Pose_SetPosePosition(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_armature_pose_set_pose_position"

    optional_skeleton_target_name: bpy.props.StringProperty()  # type:ignore
    b_pose: bpy.props.BoolProperty()  # type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def execute(self, context: bpy.types.Context):
        armature: bpy.types.Armature = Get_ActiveObject_Skeleton(context) if self.optional_skeleton_target_name == "" else bpy.data.armatures.get(self.optional_skeleton_target_name)
        if (armature is not None):
            if (self.b_pose):
                armature.pose_position = "POSE"
            else:
                armature.pose_position = "REST"
        return {"FINISHED"}


class Alx_OT_Armature_Pose_ToggleConstraints(bpy.types.Operator):
    """"""

    bl_label = "Alx Pose - toggle armature pose constraints"
    bl_idname = "alx.operator_armature_pose_toggle_constraints"

    bl_options = {"REGISTER", "UNDO"}

    enabled: bpy.props.BoolProperty()  # type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.area is not None) and (context.area.type == "VIEW_3D") and (context.object is not None)

    def execute(self, context: bpy.types.Context):
        if (context.object is not None) and (context.object.type == "ARMATURE"):
            armature: bpy.types.Object = context.object

            bone: bpy.types.PoseBone
            constraint: bpy.types.Constraint
            for bone in armature.pose.bones:
                for constraint in bone.constraints:
                    constraint.enabled = self.enabled
        else:
            self.report({"WARNING"}, message="Type: is not ARMATURE")

        return {"FINISHED"}

    def draw(self, context: bpy.types.Context):
        self.layout.row().prop(self, "enabled", text="global enabled")

    def invoke(self, context: bpy.types.Context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class Alx_OT_Armature_MatchIKByMirroredName(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_armature_pose_match_ik_by_mirrored_name"

    bl_description = "Requires [Pose Mode] Mirrors IK Data from the source side to the opposite"

    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    SourceSide: bpy.props.EnumProperty(name="Mirror From", default=1, items=[(
        "LEFT", "Left", "", 1), ("RIGHT", "Right", "", 2)])  # type:ignore

    @classmethod
    def poll(self, context):
        return (context.area.type == "VIEW_3D") and (context.mode == "POSE")

    def execute(self, context):
        if (context.active_object is not None) and (context.active_object.type == "ARMATURE") and (context.mode == "POSE"):

            ContextArmature = context.active_object

            if (ContextArmature is not None):

                PoseBoneData = ContextArmature.pose.bones

                SymmetricPairBones = []
                SymmetricUniqueBones = []

                if (self.SourceSide == "LEFT"):
                    SymmetricPairBones = [PoseBone for PoseBone in PoseBoneData if (
                        (PoseBone.name[-1].lower() == "l"))]

                if (self.SourceSide == "RIGHT"):
                    SymmetricPairBones = [PoseBone for PoseBone in PoseBoneData if (
                        (PoseBone.name[-1].lower() == "r"))]

                for PoseBone in SymmetricPairBones:
                    if (PoseBone not in SymmetricUniqueBones):
                        SymmetricUniqueBones.append(PoseBone)

                for UniquePoseBone in SymmetricUniqueBones:
                    ContextPoseBone = None
                    ContextOppositeBone = None

                    if (self.SourceSide == "LEFT"):
                        ContextPoseBone = Get_PoseBone_Always_Left(
                            UniquePoseBone, ContextArmature)
                        ContextOppositeBone = Get_PoseBone_Opposite(
                            Get_PoseBone_Always_Left(UniquePoseBone, ContextArmature), ContextArmature)

                    if (self.SourceSide == "RIGHT"):
                        ContextPoseBone = Get_PoseBone_Always_Right(
                            UniquePoseBone, ContextArmature)
                        ContextOppositeBone = Get_PoseBone_Opposite(
                            Get_PoseBone_Always_Right(UniquePoseBone, ContextArmature), ContextArmature)

                    if (ContextPoseBone is not None) and (ContextOppositeBone is not None):
                        AlxCloneIKSettings(
                            ContextPoseBone, ContextOppositeBone)
                        AlxCloneIKBoneLimitOnChain(
                            ContextPoseBone, ContextArmature)

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
