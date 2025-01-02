import random

import bpy
import bmesh

from ..AlxGpuUI import draw_unlocked_modeling_ui


class Alx_PG_PropertyGroup_UnlockedModelingProperties(bpy.types.PropertyGroup):
    """"""

    leftclick_selection_mode: bpy.props.EnumProperty(name="Left Click", default="NONE",
                                                     items=[
                                                          ("NONE", "Standard", "", 1),
                                                          ("LOOP_SELECTION", "Loop", "", 1 << 1),
                                                          ("LINKED_SELECTION", "Linked", "", 1 << 2)
                                                     ])  # type:ignore

    leftclick_selection_state_mode: bpy.props.EnumProperty(name="Extend", default="NONE",
                                                           items=[
                                                                ("NONE", "Single", "", 1),
                                                                ("EXTEND", "Extend", "", 1 << 1)
                                                           ])  # type:ignore

    rightclick_mode: bpy.props.EnumProperty(name="Right Click", default="NONE",
                                            items=[
                                                 ("NONE", "Standard", "", 1),
                                                ("POLY_MARK", "Mark Mode", "", 1 << 1),
                                                ("POLY_DELETE", "Delete Mode", "", 1 << 2),
                                                ("POLY_PAINT", "Paint Mode", "", 1 << 3)
                                            ])  # type:ignore

    edge_mark_type: bpy.props.EnumProperty(name="Mark Type", default={"NONE"}, options={"ENUM_FLAG"},
                                           items=[
        ("NONE", "None", "", 1),
        ("seam_edge", "Seam", "", 1 << 1),
        ("sharp_edge", "Sharp", "", 1 << 2),
        ("bevel_weight_edge", "Bevel", "", 1 << 3),
        ("crease_edge", "Crease", "", 1 << 4)
    ])  # type:ignore

    poly_dissolve: bpy.props.BoolProperty(name="Dissolve", default=False)  # type:ignore

    poly_delete_type: bpy.props.EnumProperty(name="Delete Type", default="NONE",
                                             items=[
                                                  ("NONE", "None", "", 1),
                                                 ("VERTS", "Vertex", "", 1 << 1),
                                                 ("EDGES", "Edge", "", 1 << 2),
                                                 ("FACES", "Face", "", 1 << 3),
                                             ])  # type:ignore

    poly_paint_mode: bpy.props.EnumProperty(name="Delete Type", default="NONE",
                                            items=[
                                                 ("NONE", "Normal", "", 1),
                                                ("COLOR_RANDOM", "Random", "", 1 << 1)
                                            ])  # type:ignore

    def auto_paint_layers(scene, context: bpy.types.Context):
        color_layers = [("NONE_COLOR", "none color", "")]
        color_layers.extend([(color.name, color.name, "") for color in context.edit_object.data.color_attributes])
        return color_layers

    poly_paint_layers: bpy.props.EnumProperty(name="Delete Type", items=auto_paint_layers)  # type:ignore

    poly_paint_color: bpy.props.FloatVectorProperty(name="Paint Color", subtype="COLOR", size=4, default=(1.0, 1.0, 1.0, 1.0), min=0.0, max=1.0)  # type:ignore


class Alx_PT_Panel_UnlockedModeling(bpy.types.Panel):
    """"""

    bl_label = ""
    bl_idname = "ALX_PT_panel_tool_unlocked_modeling"

    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context: bpy.types.Context):
        if (context is not None):
            return (context.area.type == "VIEW_3D") and (context.mode == "EDIT_MESH")
        else:
            return False

    def draw(self, context: bpy.types.Context):
        Properties: Alx_PG_PropertyGroup_UnlockedModelingProperties = context.scene.alx_tool_unlocked_modeling_properties

        AlxLayout = self.layout
        AlxLayout.ui_units_x = 12.0

        row = AlxLayout.split(factor=0.5)
        row.label(text="Left Click")
        row.prop(Properties, "leftclick_selection_mode", text="")

        row = AlxLayout.split(factor=0.5)
        row.label(text="Extend")
        row.prop(Properties, "leftclick_selection_state_mode", text="")

        row = AlxLayout.split(factor=0.5)
        row.label(text="Right Click")
        row.prop(Properties, "rightclick_mode", text="")

        if (Properties.rightclick_mode == "POLY_MARK"):
            row = AlxLayout.split(factor=0.3)
            row.label(text="MarkType")
            row.grid_flow(columns=3, align=True).prop(Properties, "edge_mark_type", expand=True)

        if (Properties.rightclick_mode == "POLY_DELETE"):
            row = AlxLayout.split(factor=0.5)
            row.label(text="Dissolve")
            row.prop(Properties, "poly_dissolve", text="")
            row = AlxLayout.split(factor=0.5)
            row.label(text="Delete Type")
            row.prop(Properties, "poly_delete_type", text="")

        if (Properties.rightclick_mode == "POLY_PAINT"):
            row = AlxLayout.split(factor=0.5)
            row.label(text="Paint")
            row.prop(Properties, "poly_paint_mode", text="")

            row = AlxLayout.split(factor=0.5)
            row.label(text="Layer")
            row.prop(Properties, "poly_paint_layers", text="")

            if (Properties.poly_paint_mode == "NONE"):
                row = AlxLayout.split(factor=0.5)
                row.label(text="Paint")
                row.prop(Properties, "poly_paint_color", text="")


class Alx_OT_Tool_UnlockedModeling(bpy.types.Operator):
    """"""

    bl_label = "Unlocked Modeling"
    bl_idname = "alx.operator_unlocked_modeling_tool"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    bIsRunning: bpy.props.BoolProperty(name="", default=False)  # type:ignore
    ContextBmesh: bmesh.types.BMesh = None
    bmesh_selection: list = []
    # average_bevel_weight: float = 0.00
    # average_crease_weight: float = 0.00

    @classmethod
    def poll(self, context: bpy.types.Context):
        return (context.area is not None) and (context.area.type == "VIEW_3D") and (context.mode == "EDIT_MESH")

    def CancelModal(self, context: bpy.types.Context):
        self.bIsRunning = False
        if (self.ContextBmesh is not None):
            self.ContextBmesh.free()

        self.bmesh_selection = []
        self.average_bevel_weight = 0.00
        self.average_crease_weight = 0.00

        try:
            bpy.types.SpaceView3D.draw_handler_remove(context.scene.alx_draw_handler_unlocked_modeling, "WINDOW")
            bpy.types.Scene.alx_draw_handler_unlocked_modeling = None

        except Exception as error:
            print(f"info-cancel: unlocked modeling ui {error}")

        if (context.area is not None):
            context.area.tag_redraw()

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):
        if (event.type == "ESC"):
            self.CancelModal(context)
            return {"CANCELLED"}
        if (context.area is not None) and (context.area.type != "VIEW_3D"):
            self.CancelModal(context)
            return {"CANCELLED"}
        if (context.mode != "EDIT_MESH"):
            self.CancelModal(context)
            return {"CANCELLED"}
        if (context.mode == "EDIT_MESH") and (context.workspace.tools.from_space_view3d_mode("EDIT_MESH", create=False).idname != "alx.workspace_unlocked_modeling_tool"):
            self.CancelModal(context)
            return {"CANCELLED"}

        if (context.area is not None) and (context.area.type == "VIEW_3D") and (context.mode == "EDIT_MESH"):

            if (context.mode == "EDIT_MESH") and (context.edit_object.type == "MESH"):
                self.ContextMesh = context.edit_object.data
                if (self.ContextBmesh is None) or (not self.ContextBmesh.is_valid):
                    self.ContextBmesh = bmesh.from_edit_mesh(self.ContextMesh)

                self.ContextBmesh.edges.ensure_lookup_table()

                self.bevel_mark_layer = self.ContextBmesh.edges.layers.float.get('bevel_weight_edge', None)
                if (self.bevel_mark_layer is None):
                    self.bevel_mark_layer = self.ContextBmesh.edges.layers.float.new('bevel_weight_edge')

                self.crease_mark_layer = self.ContextBmesh.edges.layers.float.get('crease_edge', None)
                if (self.crease_mark_layer is None):
                    self.crease_mark_layer = self.ContextBmesh.edges.layers.float.new('crease_edge')

                self.ContextBmesh.edges.ensure_lookup_table()

            if (event.type == "RIGHTMOUSE") and (event.shift == False) and (event.ctrl == False) and (event.alt == True):
                bpy.ops.wm.call_panel(name=Alx_PT_Panel_UnlockedModeling.bl_idname, keep_open=True)
                return {"RUNNING_MODAL"}

            if (event.type == "Z") and (event.shift == False) and (event.ctrl == True) and (event.value == "CLICK"):
                print("key undo")
                try:
                    bpy.ops.ed.undo()
                    print("undo")
                except Exception as error:
                    print(error)

                return {"RUNNING_MODAL"}

            if (event.type == "Z") and (event.shift == True) and (event.ctrl == True) and (event.value == "CLICK"):
                print("key redo")
                try:
                    bpy.ops.ed.redo()
                    print("redo")
                except Exception as error:
                    print(error)

                return {"RUNNING_MODAL"}

            operator_properties: Alx_PG_PropertyGroup_UnlockedModelingProperties = context.scene.alx_tool_unlocked_modeling_properties

            leftclick_selection_mode = operator_properties.leftclick_selection_mode
            leftclick_extend_selection = (operator_properties.leftclick_selection_state_mode == "EXTEND")

            rightclick_mode = operator_properties.rightclick_mode
            edge_mark_type = operator_properties.edge_mark_type
            poly_delete_type = operator_properties.poly_delete_type
            poly_dissolve = operator_properties.poly_dissolve

            poly_paint_mode = operator_properties.poly_paint_mode
            poly_paint_color = operator_properties.poly_paint_color
            poly_paint_layers = operator_properties.poly_paint_layers

            if (event.type == "LEFTMOUSE") and (event.ctrl == False) and (event.value == "CLICK"):
                if (context.mode == "EDIT_MESH"):
                    override_window = context.window
                    override_screen = override_window.screen
                    override_area = [area for area in override_screen.areas if area.type == "VIEW_3D"]
                    override_region = [region for region in override_area[0].regions if region.type == 'WINDOW']

                    with context.temp_override(window=override_window, area=override_area[0], region=override_region[0]):

                        if (leftclick_selection_mode == "NONE"):
                            if (event.shift == False):
                                bpy.ops.view3d.select("INVOKE_DEFAULT", extend=(event.shift == True) or (leftclick_extend_selection == True), toggle=True)
                                bpy.ops.ed.undo_push(message=f"AlxUM Standard Select [extend:{leftclick_extend_selection}]")
                                return {"RUNNING_MODAL"}

                            elif (event.shift == True):
                                bpy.ops.mesh.select_all("INVOKE_DEFAULT", action="DESELECT")
                                bpy.ops.ed.undo_push(message=f"AlxUM Standard Select [deselect all]")
                                return {"RUNNING_MODAL"}

                        elif (leftclick_selection_mode == "LOOP_SELECTION"):
                            bpy.ops.mesh.loop_select("INVOKE_DEFAULT", extend=leftclick_extend_selection, deselect=False, toggle=False, ring=False)
                            bpy.ops.ed.undo_push(message=f"AlxUM Loop Select extend:{leftclick_extend_selection}")
                            return {"RUNNING_MODAL"}

                        elif (leftclick_selection_mode == "LINKED_SELECTION"):
                            bpy.ops.view3d.select("INVOKE_DEFAULT", deselect=False, extend=leftclick_extend_selection)
                            bpy.ops.mesh.select_linked("INVOKE_DEFAULT", delimit={"SEAM"})
                            bpy.ops.ed.undo_push(message=f"AlxUM Linked Select extend:{leftclick_extend_selection}")
                            return {"RUNNING_MODAL"}

                return {"RUNNING_MODAL"}

            if (event.type == "LEFTMOUSE") and (event.ctrl == True) and (event.value == "CLICK"):
                override_window = context.window
                override_screen = override_window.screen
                override_area = [area for area in override_screen.areas if area.type == "VIEW_3D"]
                override_region = [region for region in override_area[0].regions if region.type == 'WINDOW']

                with context.temp_override(window=override_window, area=override_area[0], region=override_region[0]):
                    if (leftclick_selection_mode == "NONE"):
                        bpy.ops.view3d.select("INVOKE_DEFAULT", extend=False, deselect=True, toggle=True)
                        bpy.ops.ed.undo_push(message=f"AlxUM De-Select extend:{leftclick_extend_selection}")
                        return {"RUNNING_MODAL"}

                    elif (leftclick_selection_mode == "LOOP_SELECTION"):
                        bpy.ops.mesh.loop_select("INVOKE_DEFAULT", extend=False, deselect=True, toggle=True, ring=False)
                        bpy.ops.ed.undo_push(message=f"AlxUM Loop De-Select extend:{leftclick_extend_selection}")
                        return {"RUNNING_MODAL"}

                return {"RUNNING_MODAL"}

            if (event.type == "RIGHTMOUSE") and (event.ctrl == False) and (event.value == "PRESS"):

                if (rightclick_mode == "POLY_MARK"):
                    for selected_edge in [mesh_edge.index for mesh_edge in self.ContextBmesh.edges if (mesh_edge.select == True)]:
                        if ("bevel_weight_edge" in edge_mark_type):
                            self.ContextBmesh.edges[selected_edge][self.bevel_mark_layer] = 1.0
                        if ("crease_edge" in edge_mark_type):
                            self.ContextBmesh.edges[selected_edge][self.crease_mark_layer] = 1.0
                        if ("seam_edge" in edge_mark_type):
                            self.ContextBmesh.edges[selected_edge].seam = True
                        if ("sharp_edge" in edge_mark_type):
                            self.ContextBmesh.edges[selected_edge].smooth = False

                    bmesh.update_edit_mesh(self.ContextMesh, loop_triangles=True, destructive=False)
                    bpy.ops.ed.undo_push(message=f"AlxUM Mark Selection: {edge_mark_type}")
                    return {"RUNNING_MODAL"}

                if (rightclick_mode == "POLY_DELETE"):
                    if (poly_dissolve == False):
                        if (poly_delete_type in ["VERTS", "EDGES", "FACES"]):
                            delete_selection = [mesh_poly for mesh_poly in getattr(self.ContextBmesh, f"{str.lower(poly_delete_type)}") if (mesh_poly.select == True)]
                            bmesh.ops.delete(self.ContextBmesh, geom=delete_selection, context=poly_delete_type)
                            bmesh.update_edit_mesh(self.ContextMesh, loop_triangles=True, destructive=True)
                            match poly_delete_type:
                                case "VERTS":
                                    self.ContextBmesh.verts.ensure_lookup_table()
                                case "EDGES":
                                    self.ContextBmesh.edges.ensure_lookup_table()
                                case "FACES":
                                    self.ContextBmesh.faces.ensure_lookup_table()
                            bpy.ops.ed.undo_push(message=f"AlxUM Delete Selection {poly_delete_type}")
                            return {"RUNNING_MODAL"}

                    if (poly_dissolve == True):
                        if (poly_delete_type in ["VERTS", "EDGES", "FACES"]):
                            dissolve_selection = [mesh_poly for mesh_poly in getattr(self.ContextBmesh, f"{str.lower(poly_delete_type)}") if (mesh_poly.select == True)]
                            match poly_delete_type:
                                case "VERTS":
                                    bmesh.ops.dissolve_verts(self.ContextBmesh, verts=dissolve_selection)
                                    self.ContextBmesh.verts.ensure_lookup_table()
                                case "EDGES":
                                    bmesh.ops.dissolve_edges(self.ContextBmesh, edges=dissolve_selection, use_verts=True)
                                    self.ContextBmesh.edges.ensure_lookup_table()
                                case "FACES":
                                    bmesh.ops.dissolve_faces(self.ContextBmesh, faces=dissolve_selection, use_verts=False)
                                    self.ContextBmesh.faces.ensure_lookup_table()
                            bmesh.update_edit_mesh(self.ContextMesh, loop_triangles=True, destructive=True)
                            bpy.ops.ed.undo_push(message=f"AlxUM Dissolve Selection {poly_delete_type}")
                            return {"RUNNING_MODAL"}

                    return {"PASS_THROUGH"}

                if (rightclick_mode == "POLY_PAINT"):
                    if (poly_paint_layers is not None):
                        if (context.edit_object is not None) and (context.edit_object.type == "MESH") and (context.edit_object.data is not None):
                            object_layer = context.edit_object.data.color_attributes.get(poly_paint_layers)

                            if (object_layer is not None):
                                layer_domain = "verts" if (object_layer.domain == "POINT") else "loops" if (object_layer.domain == "CORNER") else ""
                                layer_data = "float_color" if (object_layer.data_type == "FLOAT_COLOR") else "color" if (object_layer.data_type == "BYTE_COLOR") else ""

                                if (layer_domain != "") and (layer_data != ""):
                                    self.color_layer = getattr(getattr(self.ContextBmesh, layer_domain).layers, layer_data).get(poly_paint_layers, None)

                                    paint_color = (random.random(), random.random(), random.random(), 1.0) if (poly_paint_mode == "COLOR_RANDOM") else poly_paint_color

                                    if (self.color_layer is not None):
                                        if (layer_domain == "loops"):
                                            loop_selection = [[mesh_face.index, mesh_loop.index] for mesh_face in self.ContextBmesh.faces for mesh_loop in mesh_face.loops if (all([vert.select for vert in mesh_loop.face.verts]))]

                                            unique_loop_selection = []
                                            for loop in loop_selection:
                                                if (loop not in unique_loop_selection):
                                                    unique_loop_selection.append(loop)

                                            for selected_loop in unique_loop_selection:
                                                self.ContextBmesh.faces[selected_loop[0]].loops[(selected_loop[1] % len(self.ContextBmesh.faces[selected_loop[0]].verts)) - 1][self.color_layer] = paint_color
                                            bmesh.update_edit_mesh(self.ContextMesh, loop_triangles=True, destructive=False)
                                        elif (layer_domain == "verts"):
                                            verts_selection = [vert.index for vert in self.ContextBmesh.verts if (vert.select == True)]

                                            for vert in verts_selection:
                                                self.ContextBmesh.verts[vert][self.color_layer] = paint_color
                                            bmesh.update_edit_mesh(self.ContextMesh, loop_triangles=True, destructive=False)
                                        else:
                                            self.report(type={"WARNING"}, message="Domain Failure")

                                    else:
                                        self.report(type={"WARNING"}, message="Failed To Retieve Color Attribute")
                        else:
                            self.report(type={"WARNING"}, message=f"Layer Incompatible {layer_domain}, {layer_data}")
                    else:
                        self.report(type={"WARNING"}, message="Failed To Retieve Color Layers")
                    return {"RUNNING_MODAL"}

            if (event.type == "RIGHTMOUSE") and (event.ctrl == True) and (event.value == "PRESS"):

                if (rightclick_mode == "POLY_MARK"):
                    for selected_edge in [mesh_edge.index for mesh_edge in self.ContextBmesh.edges if (mesh_edge.select == True)]:
                        if ("bevel_weight_edge" in edge_mark_type):
                            self.ContextBmesh.edges[selected_edge][self.bevel_mark_layer] = 0.0
                        if ("crease_edge" in edge_mark_type):
                            self.ContextBmesh.edges[selected_edge][self.crease_mark_layer] = 0.0
                        if ("seam_edge" in edge_mark_type):
                            self.ContextBmesh.edges[selected_edge].seam = False
                        if ("sharp_edge" in edge_mark_type):
                            self.ContextBmesh.edges[selected_edge].smooth = True

                    bmesh.update_edit_mesh(self.ContextMesh, loop_triangles=True, destructive=False)
                    bpy.ops.ed.undo_push(message=f"AlxUM Mark Selection: {edge_mark_type}")
                    return {"RUNNING_MODAL"}

            self.bmesh_selection = [bmesh_edge.index for bmesh_edge in self.ContextBmesh.edges if (bmesh_edge.select == True)]

            weight_values = [self.ContextBmesh.edges[selected_edge][self.bevel_mark_layer] for selected_edge in self.bmesh_selection]
            self.average_bevel_weight = round(sum(weight_values) / float(len(weight_values)), 2) if (len(weight_values) > 0) else 0.00

            crease_values = [self.ContextBmesh.edges[selected_edge][self.crease_mark_layer] for selected_edge in self.bmesh_selection]
            self.average_crease_weight = round(sum(crease_values) / float(len(crease_values)), 2) if (len(crease_values) > 0) else 0.00

            return {"PASS_THROUGH"}
        else:
            return {"PASS_THROUGH"}

    def invoke(self, context, event):
        # print("invoke called")
        # self.bIsRunning = True

        # position_x = 100
        # position_y = 100

        # if (context.scene.alx_draw_handler_unlocked_modeling is None):
        #     bpy.types.Scene.alx_draw_handler_unlocked_modeling = bpy.types.SpaceView3D.draw_handler_add(draw_unlocked_modeling_ui, (position_x, position_y, self), "WINDOW", 'POST_PIXEL')
        # else:
        #     print("From Invoke: alx_draw_handler_unlocked_modeling is not None")

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


class Alx_WT_WorkSpaceTool_UnlockedModeling(bpy.types.WorkSpaceTool):
    """"""

    bl_space_type = "VIEW_3D"
    bl_context_mode = "EDIT_MESH"
    bl_icon = "ops.gpencil.draw.poly"

    bl_idname = "alx.workspace_unlocked_modeling_tool"
    bl_label = "Alx Unlocked Modeling"

    after = "None"
    separator = True
    group = False

    bl_keymap = (
        ("alx.operator_unlocked_modeling_tool", {"type": "RIGHTMOUSE", "value": "PRESS"},
         {"properties": []}),
    )
