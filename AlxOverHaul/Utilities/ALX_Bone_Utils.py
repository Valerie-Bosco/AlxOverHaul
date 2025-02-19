import re

import bpy


def bIsLeft(bone: bpy.types.Bone, check_name=False):
    return (bone.head_local[0] > 0.001) and (
        re.search(
            r"(?<![\S+\s+])L_(?!\s+) | (?<![\S+\s+])L\.(?!\s+) | (?<![\S+\s+])_L(?!\s+) | (?<![\S+\s+])\.L(?!\s+) | \
            (?<![\S+\s+])LEFT_(?!\s+) | (?<![\S+\s+])LEFT\.(?!\s+) | (?<![\S+\s+])_LEFT(?!\s+) | (?<![\S+\s+])\.LEFT(?!\s+) | \
            (?<![\S+\s+])LEFT(?!\s+) | (?<!\s+)LEFT(?![\S+\s+])",
            bone.name,
            re.IGNORECASE
        ) != None
    ) if check_name else True
