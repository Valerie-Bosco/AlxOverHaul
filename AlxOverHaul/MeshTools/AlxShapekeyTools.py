import bmesh
import bpy
from mathutils import kdtree

vrm0_blend_shapes_names = [
    "Neutral",
    "A",
    "I",
    "U",
    "E",
    "O",
    "Blink",
    "Blink_L",
    "Blink_R",
    "Joy",
    "Angry",
    "Sorrow",
    "Fun",
    "LookUp",
    "LookDown",
    "LookLeft",
    "LookRight"
]

arkit_blend_shape_names = [
    "eyeBlinkLeft",
    "eyeLookDownLeft",
    "eyeLookInLeft",
    "eyeLookOutLeft",
    "eyeLookUpLeft",
    "eyeSquintLeft",
    "eyeWideLeft",
    "eyeBlinkRight",
    "eyeLookDownRight",
    "eyeLookInRight",
    "eyeLookOutRight",
    "eyeLookUpRight",
    "eyeSquintRight",
    "eyeWideRight",
    "jawForward",
    "jawLeft",
    "jawRight",
    "jawOpen",
    "mouthClose",
    "mouthFunnel",
    "mouthPucker",
    "mouthRight",
    "mouthLeft",
    "mouthSmileLeft",
    "mouthSmileRight",
    "mouthFrownRight",
    "mouthFrownLeft",
    "mouthDimpleLeft",
    "mouthDimpleRight",
    "mouthStretchLeft",
    "mouthStretchRight",
    "mouthRollLower",
    "mouthRollUpper",
    "mouthShrugLower",
    "mouthShrugUpper",
    "mouthPressLeft",
    "mouthPressRight",
    "mouthLowerDownLeft",
    "mouthLowerDownRight",
    "mouthUpperUpLeft",
    "mouthUpperUpRight",
    "browDownLeft",
    "browDownRight",
    "browInnerUp",
    "browOuterUpLeft",
    "browOuterUpRight",
    "cheekPuff",
    "cheekSquintLeft",
    "cheekSquintRight",
    "noseSneerLeft",
    "noseSneerRight",
    "tongueOut"
]


class ALX_OT_Shapekey_RemoveUnlockedShapekey(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_shapekey_remove_unlocked_shapekey"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.active_object is not None) and (context.active_object.type == "MESH")

    def execute(self, context: bpy.types.Context):
        if (context.active_object is not None) and (context.active_object.type == "MESH"):
            mesh_object: bpy.types.Object = context.active_object
            keyblocks = mesh_object.data.shape_keys.key_blocks
            [mesh_object.shape_key_remove(shapekey)
             for shapekey in keyblocks
             if ((shapekey.lock_shape == False) and
                 (shapekey.name != "Basis"))
             ]

        return {"FINISHED"}


class ALX_OT_Shapekey_RemoveNameDuplicateShapekey(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_shapekey_remove_name_duplicate_shapekey"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.active_object is not None) and (context.active_object.type == "MESH")

    def execute(self, context: bpy.types.Context):
        if (context.active_object is not None) and (context.active_object.type == "MESH"):
            mesh_object: bpy.types.Object = context.active_object
            keyblocks = mesh_object.data.shape_keys.key_blocks
            [mesh_object.shape_key_remove(shapekey)
             for shapekey in keyblocks
             if ((shapekey.lock_shape == False) and
                 (keyblocks.keys().count(shapekey.name)))
             ]

        return {"FINISHED"}


class Alx_OT_Shapekey_TransferShapekeysToTarget(bpy.types.Operator):
    """"""

    bl_label = "Alx Shapekeys - transfer shapekeys by vertex position"
    bl_idname = "alx.operator_shapekey_transfer_shapekeys_to_target"
    bl_options = {"REGISTER", "UNDO"}

    source_mesh: bpy.types.Mesh = None
    source_bmesh: bmesh.types.BMesh = None

    target_mesh: bpy.types.Mesh = None
    target_bmesh: bmesh.types.BMesh = None

    shapekey_source_kdtree: kdtree.KDTree
    shapekey_target_kdtree: kdtree.KDTree

    # margin_of_error : bpy.props.FloatProperty(name="margin of error", subtype="DISTANCE") #type:ignore

    def auto_retrieve_shapekeys(self, context: bpy.types.Context):
        unique_shapekey_set = {("NONE", "none", "")}

        shape_key_object: bpy.types.Object = context.window_manager.alx_session_properties.shapekey_transfer_source_object

        if (shape_key_object is not None) and (shape_key_object.data.shape_keys is not None) and (len(shape_key_object.data.shape_keys.key_blocks) != 0):
            key_blocks = shape_key_object.data.shape_keys.key_blocks

            _retriever = [unique_shapekey_set.add((shapekey.name, shapekey.name, "")) for shapekey in key_blocks if (shapekey.name not in ["", "Basis"])]

            del _retriever

        return unique_shapekey_set

    shapekey_source_name: bpy.props.EnumProperty(name="source shapekeys", items=auto_retrieve_shapekeys)  # type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def execute(self, context: bpy.types.Context):
        properties = context.window_manager.alx_session_properties

        if (self.shapekey_source_name not in ["", "NONE"]):

            if (properties.shapekey_transfer_source_object is not None) and (properties.shapekey_transfer_source_object.type == "MESH"):
                source_object: bpy.types.Object = properties.shapekey_transfer_source_object
                self.source_mesh: bpy.types.Mesh = source_object.data

                if (self.source_bmesh is None) or (not self.source_bmesh.is_valid):
                    if (self.source_bmesh is None):
                        self.source_bmesh = bmesh.new()
                    self.source_bmesh.from_mesh(self.source_mesh)

                self.source_bmesh.verts.ensure_lookup_table()
                self.source_bmesh.edges.ensure_lookup_table()
                self.source_bmesh.faces.ensure_lookup_table()

                source_tree_size = len(self.source_bmesh.verts)
                self.shapekey_source_kdtree = kdtree.KDTree(source_tree_size)

                for index, vert in enumerate(self.source_bmesh.verts):
                    self.shapekey_source_kdtree.insert(vert.co, index)

                self.shapekey_source_kdtree.balance()

            if (properties.shapekey_transfer_target_object is not None) and (properties.shapekey_transfer_target_object.type == "MESH"):
                target_object: bpy.types.Object = properties.shapekey_transfer_target_object
                self.target_mesh: bpy.types.Mesh = target_object.data

                if (self.target_bmesh is None) or (not self.target_bmesh.is_valid):
                    if (self.target_bmesh is None):
                        self.target_bmesh = bmesh.new()
                    self.target_bmesh.from_mesh(self.target_mesh)

                self.target_bmesh.verts.ensure_lookup_table()
                self.target_bmesh.edges.ensure_lookup_table()
                self.target_bmesh.faces.ensure_lookup_table()

                target_tree_size = len(self.target_bmesh.verts)
                self.shapekey_target_kdtree = kdtree.KDTree(target_tree_size)

                for index, vert in enumerate(self.target_bmesh.verts):
                    self.shapekey_target_kdtree.insert(vert.co, index)

                self.shapekey_target_kdtree.balance()

            if (self.shapekey_source_kdtree is not None) and (self.shapekey_target_kdtree is not None):

                shapekey_layer = self.source_bmesh.verts.layers.shape.get(self.shapekey_source_name)

                shape_key_co_set = dict()

                for source_vert in self.source_bmesh.verts:
                    original_co = source_vert.co
                    co, target_index, distance = self.shapekey_target_kdtree.find(original_co)

                    vert_co = source_vert[shapekey_layer]
                    shape_key_co_set.update({target_index: vert_co})

                if (self.target_bmesh.verts.layers.shape.get(self.shapekey_source_name) is None):
                    properties.shapekey_transfer_target_object.shape_key_add(name=self.shapekey_source_name)

                self.target_bmesh.free()

                target_object: bpy.types.Object = properties.shapekey_transfer_target_object
                self.target_mesh: bpy.types.Mesh = target_object.data

                if (self.target_bmesh is None) or (not self.target_bmesh.is_valid):
                    self.target_bmesh = bmesh.new()
                    self.target_bmesh.from_mesh(self.target_mesh)

                self.target_bmesh.verts.ensure_lookup_table()
                self.target_bmesh.edges.ensure_lookup_table()
                self.target_bmesh.faces.ensure_lookup_table()

                self.target_shapekey_layer = self.target_bmesh.verts.layers.shape.get(self.shapekey_source_name)

                if (self.target_shapekey_layer is not None):
                    for target_index_key in shape_key_co_set:
                        self.target_bmesh.verts[target_index_key][self.target_shapekey_layer] = shape_key_co_set[target_index_key]
                else:
                    self.report({"WARNING"}, "Layer is not present")

                self.target_bmesh.to_mesh(self.target_mesh)
        else:
            self.report({"ERROR"}, message="selected shapekey layer is invalid")

        return {"FINISHED"}

    def draw(self, context: bpy.types.Context):
        properties = context.window_manager.alx_session_properties

        self.layout.prop(properties, "shapekey_transfer_source_object", text="source")
        self.layout.prop(properties, "shapekey_transfer_target_object", text="target")
        self.layout.prop(self, "shapekey_source_name", text="source")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class Alx_OT_Shapekey_AddEmptyShapeKeys(bpy.types.Operator):
    """"""

    bl_label = "Alx Shapekeys - add empty VRM_0/ARKit shapekeys"
    bl_idname = "alx.operator_shapekey_vrm_add_empty_shape_keys"
    bl_options = {"REGISTER", "UNDO"}

    blendshape_target_type: bpy.props.EnumProperty(name="blendshapes type:", default="VRM0", items=[
        ("VRM0", "VRM 0", "", 1),
        ("ARKIT", "ARKit", "", 1 << 1)
    ])  # type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.object is not None) and (context.object.type == "MESH")

    def execute(self, context: bpy.types.Context):
        if (context.object is not None) and (context.object.type == "MESH"):
            object = context.object
            mesh: bpy.types.Mesh = object.data

            blendshapes_target_type_names: list[str]

            match self.blendshape_target_type:
                case "VRM0":
                    blendshapes_target_type_names = vrm0_blend_shapes_names
                case "ARKIT":
                    blendshapes_target_type_names = arkit_blend_shape_names

            _mode = context.mode if (context.mode[0:4] != "EDIT") else "EDIT" if (context.mode[0:4] == "EDIT") else "OBJECT"
            bpy.ops.object.mode_set(mode="OBJECT")
            for blendshape_name in blendshapes_target_type_names:
                if (mesh.shape_keys is not None):
                    if (mesh.shape_keys.key_blocks.get(blendshape_name) is None):
                        object.shape_key_add(name=blendshape_name, from_mix=False)
                else:
                    if (mesh.shape_keys is None):
                        object.shape_key_add(name=blendshape_name, from_mix=False)

            bpy.ops.object.mode_set(mode=_mode)
        else:
            return {"CANCELLED"}
        return {"FINISHED"}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        return context.window_manager.invoke_props_dialog(self, width=300)
