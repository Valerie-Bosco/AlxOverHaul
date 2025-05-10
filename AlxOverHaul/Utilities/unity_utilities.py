import bpy

from ..definitions import unity_definitions


def HAS_RequiredHumanoidBones(object: bpy.types.Object) -> bool | set[str]:
    if (object is not None) and (object.type == "ARMATURE"):
        armature: bpy.types.Armature = object.data

    result = set(unity_definitions.TD_UNITY_required_humanoid_bones).difference({bone.name for bone in armature.bones})

    try:
        return result.add(result.pop())
    except:
        return True
