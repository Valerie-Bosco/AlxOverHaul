import re

import bpy

from .AlxUtilities import (AlxGetBoneNameOpposite, AlxGetIKConstraint,
                           AlxInvertPoleAngle)


def COMPARE_VertexGroups_BoneNames(objects: list[bpy.types.Object], armature: bpy.types.Armature):
    bone_names = [bone.name for bone in armature.bones]
    return [vertex_group for obj in objects for vertex_group in obj.vertex_groups if (obj is not None) if (hasattr(obj, "vertex_groups")) and (vertex_group.name not in bone_names)]


def Get_ActiveObject_Skeleton(context: bpy.types.Context):
    try:
        if (context is not None) and (context.active_object is not None):
            match context.active_object.type:
                case "MESH":
                    return context.active_object.find_armature()

                case "ARMATURE":
                    return context.scene.objects.get(context.active_object.name)

                case _:
                    return None
    except:
        pass
    return None


def Get_PoseBone_Opposite(bone: bpy.types.Bone, skeleton_object: bpy.types.Object) -> bpy.types.PoseBone | None:
    if (bone is not None) and (len(bone.name) > 2):
        if (re.search(r".[LlRr]", bone.name) is not None):
            match bone.name[-1]:
                case "R":
                    return skeleton_object.pose.bones.get(bone.name[0:-1] + "L")
                case "L":
                    return skeleton_object.pose.bones.get(bone.name[0:-1] + "R")
                case "r":
                    return skeleton_object.pose.bones.get(bone.name[0:-1] + "l")
                case "l":
                    return skeleton_object.pose.bones.get(bone.name[0:-1] + "r")
    return None


def Get_PoseBone_Always_Left(bone: bpy.types.Bone, skeleton_object: bpy.types.Object) -> bpy.types.PoseBone | None:
    if (bone is not None) and (len(bone.name) > 2):
        if (re.search(r".[LlRr]", bone.name) is not None):
            if (re.search(r".[LR]") is not None):
                return skeleton_object.pose.bones.get(bone.name[0:-1] + "L")
            elif (re.search(r".[lr]") is not None):
                return skeleton_object.pose.bones.get(bone.name[0:-1] + "l")
        else:
            return skeleton_object.pose.bones.get(bone.name)


def Get_PoseBone_Always_Right(bone: bpy.types.Bone, skeleton_object: bpy.types.Object) -> bpy.types.PoseBone | None:
    if (bone is not None) and (len(bone.name) > 2):
        if (re.search(r".[LlRr]", bone.name) is not None):
            if (re.search(r".[LR]") is not None):
                return skeleton_object.pose.bones.get(bone.name[0:-1] + "R")
            elif (re.search(r".[lr]") is not None):
                return skeleton_object.pose.bones.get(bone.name[0:-1] + "r")
        else:
            return skeleton_object.pose.bones.get(bone.name)


def AlxCloneIKSettings(CheckBone, OppositeBone):
    if (CheckBone is not None) and (OppositeBone is not None):
        CheckBoneIK = AlxGetIKConstraint(CheckBone)
        OppositeBoneIK = AlxGetIKConstraint(OppositeBone)

        if (CheckBoneIK is not None) and (OppositeBoneIK is not None):
            if (CheckBoneIK.target is not None):
                OppositeBoneIK.target = CheckBoneIK.target
                if (CheckBoneIK.target.type == "ARMATURE"):
                    if (CheckBoneIK.subtarget is not None):
                        OppositeBoneIK.subtarget = AlxGetBoneNameOpposite(
                            CheckBoneIK.subtarget)

            if (CheckBoneIK.pole_target is not None):
                OppositeBoneIK.pole_target = CheckBoneIK.pole_target
                if (CheckBoneIK.pole_target.type == "ARMATURE"):
                    if (CheckBoneIK.pole_subtarget is not None):
                        OppositeBoneIK.pole_subtarget = AlxGetBoneNameOpposite(
                            CheckBoneIK.pole_subtarget)
                OppositeBoneIK.pole_angle = AlxInvertPoleAngle(
                    CheckBoneIK.pole_angle)

            OppositeBoneIK.chain_count = CheckBoneIK.chain_count
            OppositeBoneIK.use_tail = CheckBoneIK.use_tail
            OppositeBoneIK.use_stretch = CheckBoneIK.use_stretch

        if (CheckBoneIK is None) and (OppositeBoneIK is not None):
            NewIK = CheckBone.constraints.new("IK")

            try:
                CheckBone.constraints.move(CheckBone.constraints.find(
                    NewIK.name), OppositeBone.constraints.find(OppositeBoneIK.name))

            except:
                pass

            if (OppositeBoneIK.target is not None):
                NewIK.target = OppositeBoneIK.target

                if (OppositeBoneIK.target.type == "ARMATURE"):
                    if (OppositeBoneIK.subtarget is not None):
                        NewIK.subtarget = AlxGetBoneNameOpposite(
                            OppositeBoneIK.subtarget)

            if (OppositeBoneIK.pole_target is not None):
                NewIK.pole_target = OppositeBoneIK.pole_target

                if (OppositeBoneIK.pole_target.type == "ARMATURE"):
                    if (OppositeBoneIK.pole_subtarget is not None):
                        NewIK.pole_subtarget = AlxGetBoneNameOpposite(
                            OppositeBoneIK.pole_subtarget)

                NewIK.pole_angle = AlxInvertPoleAngle(CheckBoneIK.pole_angle)

            NewIK.chain_count = OppositeBoneIK.chain_count
            NewIK.use_tail = OppositeBoneIK.use_tail
            NewIK.use_stretch = OppositeBoneIK.use_stretch

        if (CheckBoneIK is not None) and (OppositeBoneIK is None):
            NewIK = OppositeBone.constraints.new("IK")

            try:
                OppositeBone.constraints.move(OppositeBone.constraints.find(
                    NewIK.name), CheckBone.constraints.find(CheckBoneIK.name))

            except:
                pass

            if (CheckBoneIK.target is not None):
                NewIK.target = CheckBoneIK.target

                if (CheckBoneIK.target.type == "ARMATURE"):
                    if (CheckBoneIK.subtarget is not None):
                        NewIK.subtarget = AlxGetBoneNameOpposite(
                            CheckBoneIK.subtarget)

            if (CheckBoneIK.pole_target is not None):
                NewIK.pole_target = CheckBoneIK.pole_target

                if (CheckBoneIK.pole_target.type == "ARMATURE"):
                    if (CheckBoneIK.pole_subtarget is not None):
                        NewIK.pole_subtarget = AlxGetBoneNameOpposite(
                            CheckBoneIK.pole_subtarget)

                NewIK.pole_angle = AlxInvertPoleAngle(CheckBoneIK.pole_angle)

            NewIK.chain_count = CheckBoneIK.chain_count
            NewIK.use_tail = CheckBoneIK.use_tail
            NewIK.use_stretch = CheckBoneIK.use_stretch

        return {"FINISHED"}


def AlxCloneIKBoneLimitOnChain(IKHead, Armature):
    i = 0

    if (IKHead is not None) and (AlxGetIKConstraint(IKHead) is not None):
        if (AlxGetIKConstraint(IKHead).use_tail == False):
            ChainLength = AlxGetIKConstraint(IKHead).chain_count + 1
        else:
            ChainLength = AlxGetIKConstraint(IKHead).chain_count
        ParentOnChain = None

        IKHeadOpposite = Get_PoseBone_Opposite(IKHead, Armature)

        IKHeadOpposite.use_ik_limit_x = IKHead.use_ik_limit_x
        IKHeadOpposite.ik_min_x = IKHead.ik_min_x
        IKHeadOpposite.ik_max_x = IKHead.ik_max_x

        IKHeadOpposite.use_ik_limit_y = IKHead.use_ik_limit_y
        IKHeadOpposite.ik_min_y = IKHead.ik_min_y
        IKHeadOpposite.ik_max_y = IKHead.ik_max_y

        IKHeadOpposite.use_ik_limit_z = IKHead.use_ik_limit_z
        IKHeadOpposite.ik_min_z = IKHead.ik_max_z * -1
        IKHeadOpposite.ik_max_z = IKHead.ik_min_z * -1

        ParentOnChain = IKHead
        ParentOnChainOpposite = Get_PoseBone_Opposite(IKHead, Armature)
        if (ParentOnChain is not None) and (ParentOnChainOpposite is not None):
            while i < ChainLength:
                if (i < 0):
                    break

                ParentOnChainOpposite.use_ik_limit_x = ParentOnChain.use_ik_limit_x
                ParentOnChainOpposite.ik_min_x = ParentOnChain.ik_min_x
                ParentOnChainOpposite.ik_max_x = ParentOnChain.ik_max_x

                ParentOnChainOpposite.use_ik_limit_y = ParentOnChain.use_ik_limit_y
                ParentOnChainOpposite.ik_min_y = ParentOnChain.ik_min_y
                ParentOnChainOpposite.ik_max_y = ParentOnChain.ik_max_y

                ParentOnChainOpposite.use_ik_limit_z = ParentOnChain.use_ik_limit_z
                ParentOnChainOpposite.ik_min_z = ParentOnChain.ik_max_z * -1
                ParentOnChainOpposite.ik_max_z = ParentOnChain.ik_min_z * -1

                ParentOnChain = ParentOnChain.parent
                ParentOnChainOpposite = ParentOnChainOpposite.parent
                i += 1
