from typing import Final as const

TD_object_types: const[str] = ["MESH", "CURVE", "SURFACE", "META", "FONT", "CURVES", "POINTCLOUD", "VOLUME",
                               "GPENCIL", "GREASEPENCIL", "ARMATURE", "LATTICE", "EMPTY", "LIGHT", "LIGHT_PROBE", "CAMERA", "SPEAKER"]


TD_modifier_modifiy_types: const[str] = ["DATA_TRANSFER", "MESH_CACHE", "MESH_SEQUENCE_CACHE", "NORMAL_EDIT",
                                         "WEIGHTED_NORMAL", "UV_PROJECT", "UV_WARP", "VERTEX_WEIGHT_EDIT", "VERTEX_WEIGHT_MIX", "VERTEX_WEIGHT_PROXIMITY"]
TD_modifier_generate_types: const[str] = ["ARRAY", "BEVEL", "BOOLEAN", "BUILD", "DECIMATE", "EDGE_SPLIT", "NODES", "MASK", "MIRROR", "MULTIRES",
                                          "REMESH", "SCREW", "SKIN", "SOLIDIFY", "SUBSURF", "TRIANGULATE", "VOLUME_TO_MESH", "WELD", "WIREFRAME"]
TD_modifier_deform_types: const[str] = ["ARMATURE", "CAST", "CURVE", "DISPLACE", "HOOK", "LAPLACIANDEFORM", "LATTICE",
                                        "MESH_DEFORM", "SHRINKWRAP", "SIMPLE_DEFORM", "SMOOTH", "CORRECTIVE_SMOOTH", "LAPLACIANSMOOTH", "SURFACE_DEFORM", "WARP", "WAVE"]
TD_modifier_physics_types: const[str] = ["CLOTH", "COLLISION", "DYNAMIC_PAINT",
                                         "EXPLODE", "FLUID", "OCEAN", "PARTICLE_INSTANCE", "PARTICLE_SYSTEM", "SOFT_BODY"]
