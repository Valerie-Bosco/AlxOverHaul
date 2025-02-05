import bpy
import bmesh

class Alx_OT_Sculpt_ConditionMasking(bpy.types.Operator):
    """"""

    bl_label = "Sculpt Mask By Condition"
    bl_idname = "alx.operator_sculpt_mask_by_condition"

    ContextMesh : bpy.types.Mesh = None
    ContextBMesh : bmesh.types.BMesh = None

    mask_condition : bpy.props.EnumProperty(name="", default="EDGE_SEAM", 
        items=[
            ("EDGE_SEAM", "edge seam", "", 1),
            ("BOUNDARY", "boundary", "", 1<<1),
            ("SELECTION", "selection", "", 1<<2)
        ]) #type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.area is not None) and (context.area.type == "VIEW_3D") and (context.object is not None)
    
    def execute(self, context: bpy.types.Context):
        if (context.object is not None) and (context.object.type == "MESH"):
            self.ContextMesh = context.object.data

            if (self.ContextBMesh is None):
                self.ContextBMesh = bmesh.new()
                self.ContextBMesh.from_mesh(self.ContextMesh)

            if (self.ContextBMesh.is_valid == False):
                self.ContextBMesh.from_mesh(self.ContextMesh)

            self.ContextBMesh.verts.ensure_lookup_table()
            self.ContextBMesh.edges.ensure_lookup_table()
            self.ContextBMesh.faces.ensure_lookup_table()

            vert : bmesh.types.BMVert
            edge : bmesh.types.BMEdge
            face : bmesh.types.BMFace
            loop : bmesh.types.BMLoop


            condition_vertex = None
            match self.mask_condition:
                case "EDGE_SEAM":
                    condition_vertex = set(vert.index for edge in self.ContextBMesh.edges if (edge.seam == True) for vert in edge.verts)
                case "SELECTION":
                    condition_vertex = set(vert.index for vert in self.ContextBMesh.verts if (vert.select == True))
                case _:
                    self.report({"WARNING"}, message="condition selection failed")

            if (condition_vertex is not None):
                if (len(condition_vertex) == 0):
                    self.report({"WARNING"}, message="no vertex matching condition")
                    return {"FINISHED"}

                sculpt_mask_layer = self.ContextBMesh.verts.layers.float.get(".sculpt_mask")
                if (sculpt_mask_layer is None):
                    sculpt_mask_layer = self.ContextBMesh.verts.layers.float.new(".sculpt_mask")

                for vert in self.ContextBMesh.verts:
                    if (vert.index in condition_vertex):
                        self.ContextBMesh.verts[vert.index][sculpt_mask_layer] = 1.0
                    else:
                        self.ContextBMesh.verts[vert.index][sculpt_mask_layer] = 0.0

                if (context.mode in ["OBJECT", "SCULPT"]):
                    self.ContextBMesh.to_mesh(self.ContextMesh)
                    print("to_mesh")
                if (context.mode == "EDIT_MESH"):
                    bmesh.update_edit_mesh(self.ContextMesh)
                    print("update_edit_mesh")

                if (context.area is not None) and (context.area.type == "VIEW_3D"):
                    context.area.tag_redraw()
            else:
                self.report({"WARNING"}, message="no vertex matching condition")

        return {"FINISHED"}
    
    def draw(self, context: bpy.types.Context):
        self.layout.prop(self, "mask_condition", text="condition")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)