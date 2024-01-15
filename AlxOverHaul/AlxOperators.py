import bpy
import bmesh

from AlxOverHaul import AlxPreferences, AlxUtils

class Alx_OT_Mode_UnlockedModes(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_mode_unlocked_modes"
    bl_options = {"INTERNAL"}

    DefaultBehaviour : bpy.props.BoolProperty(name="", default=True, options={"HIDDEN"})
    TargetMode : bpy.props.StringProperty(name="", default="OBJECT", options={"HIDDEN"})
    TargetType : bpy.props.StringProperty(name="", default="", options={"HIDDEN"})
    TargetSubMode : bpy.props.StringProperty(name="", default="", options={"HIDDEN"})
    
    TargetObject : bpy.props.StringProperty(name="", options={"HIDDEN"})
    TargetArmature : bpy.props.StringProperty(name="", options={"HIDDEN"})

    @classmethod
    def poll(self, context):
        return (context.area.type == "VIEW_3D")
    
    def execute(self, context):
        if (self.DefaultBehaviour == True):
            match self.TargetMode:
                case "OBJECT":
                    if (context.mode != "OBJECT"):
                        bpy.ops.object.mode_set(mode="OBJECT")
                    return {"FINISHED"}

                case "EDIT":
                    if (len(context.selected_objects) != 0):
                        for Object in context.selected_objects:
                            if (Object is not None):
                                if (Object.type == "MESH") and (self.TargetType == "MESH") and (self.TargetSubMode in ["VERT", "EDGE", "FACE"]):
                                    bpy.context.view_layer.objects.active = Object
                                    bpy.ops.object.mode_set_with_submode(mode="EDIT", mesh_select_mode=set([self.TargetSubMode]))

                                if (Object.type == "ARMATURE") and (self.TargetType == "ARMATURE") and (self.TargetSubMode == ""):
                                    bpy.context.view_layer.objects.active = Object
                                    bpy.ops.object.mode_set(mode="EDIT")

                                if (Object.type == "CURVE") and (self.TargetType == "CURVE") and (self.TargetSubMode == ""):
                                    bpy.context.view_layer.objects.active = Object
                                    bpy.ops.object.mode_set(mode="EDIT")

                                if (Object.type == "SURFACE") and (self.TargetType == "SURFACE") and (self.TargetSubMode == ""):
                                    bpy.context.view_layer.objects.active = Object
                                    bpy.ops.object.mode_set(mode="EDIT")

                                if (Object.type == "META") and (self.TargetType == "META") and (self.TargetSubMode == ""):
                                    bpy.context.view_layer.objects.active = Object
                                    bpy.ops.object.mode_set(mode="EDIT")

                                if (Object.type == "FONT") and (self.TargetType == "FONT") and (self.TargetSubMode == ""):
                                    bpy.context.view_layer.objects.active = Object
                                    bpy.ops.object.mode_set(mode="EDIT")

                                if (Object.type == "GPENCIL") and (self.TargetType == "GPENCIL") and (self.TargetSubMode in ["POINT", "STROKE", "SEGMENT"]):
                                    bpy.context.view_layer.objects.active = Object
                                    bpy.ops.object.mode_set(mode="EDIT_GPENCIL")

                                    context.scene.tool_settings.gpencil_selectmode_edit = self.TargetSubMode

                                if (Object.type == "LATTICE") and (self.TargetType == "LATTICE") and (self.TargetSubMode == ""):
                                    bpy.context.view_layer.objects.active = Object
                                    bpy.ops.object.mode_set(mode="EDIT")
                                else:
                                    print(self.TargetSubMode)

                    return {"FINISHED"}
                
                case "SCULPT":
                    if (context.mode != "SCULPT"):
                        if (context.active_object is not None) and (context.active_object.type == "MESH"):
                            bpy.ops.object.mode_set(mode="SCULPT")
                    
                    return {"FINISHED"}       

        if (self.DefaultBehaviour == False):
            match self.TargetMode:
                case "POSE":
                    if (context.mode != "POSE"):
                        if (self.TargetArmature != "") and (bpy.data.objects[self.TargetArmature] is not None):                       
                            if (context.mode == "PAINT_WEIGHT"):
                                bpy.ops.object.mode_set(mode="OBJECT")

                            bpy.data.objects.get(self.TargetArmature).hide_set(False)
                            bpy.data.objects.get(self.TargetArmature).hide_viewport = False

                            bpy.context.view_layer.objects.active = bpy.data.objects.get(self.TargetArmature)
                            bpy.ops.object.mode_set(mode="POSE")

                    return {"FINISHED"}
                
                case "PAINT_WEIGHT":
                    if (context.mode != "PAINT_WEIGHT"):
                        if (self.TargetObject != "") and (self.TargetArmature != ""):
                            if (bpy.data.objects[self.TargetObject] is not None) and (bpy.data.objects[self.TargetArmature] is not None):
                                if (context.mode == "POSE"):
                                    bpy.ops.object.mode_set(mode="OBJECT")
                                
                                bpy.data.objects.get(self.TargetArmature).hide_set(False)
                                bpy.data.objects.get(self.TargetArmature).hide_viewport = False

                                bpy.data.objects.get(self.TargetArmature).select_set(True)

                                bpy.context.view_layer.objects.active = bpy.data.objects.get(self.TargetObject)
                                bpy.ops.object.mode_set(mode="WEIGHT_PAINT")

                    return {"FINISHED"}

        return {"FINISHED"}

class Alx_OT_Scene_UnlockedSnapping(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_scene_unlocked_snapping"
    bl_options = {"INTERNAL"}

    SourceSnapping : bpy.props.StringProperty(name="", default="NONE", options={"HIDDEN"})
    TargetSnapping : bpy.props.StringProperty(name="", default="NONE", options={"HIDDEN"})
    SubTargetSnapping : bpy.props.StringProperty(name="", default="NONE", options={"HIDDEN"})

    ShouldOffset : bpy.props.BoolProperty(name="", default=False, options={"HIDDEN"})

    @classmethod
    def poll(self, context):
        return context.area.type == "VIEW_3D"
    
    def execute(self, context):
        if (self.SourceSnapping == "ACTIVE"):
            if (self.TargetSnapping == "SELECTED"):
                if (len(context.selected_objects) != 0):
                    for Object in context.selected_objects:
                        if (context.active_object is not None) and (Object is not context.active_object):
                            Object.location = context.active_object.location
                return {"FINISHED"}
            
            if (self.TargetSnapping == "SCENE_CURSOR"):
                if (context.active_object is not None):
                    if (context.mode == "OBJECT"):
                        context.scene.cursor.location = context.active_object.location
                    if (context.mode == "EDIT_MESH"):
                        ContextBmesh = bmesh.from_edit_mesh(context.active_object.data)

                        try:
                            ContextBmesh.select_history[1]

                            UniqueVertex = []
                            SelectionVx_X = []
                            SelectionVx_Y = []
                            SelectionVx_Z = []
                            for SelectedItem in ContextBmesh.select_history:
                                if (SelectedItem.__class__ is bmesh.types.BMVert):
                                    if (SelectedItem not in UniqueVertex):
                                        UniqueVertex.append(SelectedItem)

                                        SelectionVx_X.append(SelectedItem.co.x)
                                        SelectionVx_Y.append(SelectedItem.co.y)
                                        SelectionVx_Z.append(SelectedItem.co.z)

                                if (SelectedItem.__class__ is bmesh.types.BMEdge) or (SelectedItem.__class__ is bmesh.types.BMFace):
                                    for Vertex in SelectedItem.verts:
                                        if Vertex not in UniqueVertex:
                                            UniqueVertex.append(Vertex)

                                            SelectionVx_X.append(Vertex.co.x)
                                            SelectionVx_Y.append(Vertex.co.y)
                                            SelectionVx_Z.append(Vertex.co.z)

                            print(UniqueVertex)

                            AverageX = sum(SelectionVx_X) / len(SelectionVx_X)
                            print(AverageX)
                            AverageY = sum(SelectionVx_Y) / len(SelectionVx_Y)
                            print(AverageY)
                            AverageZ = sum(SelectionVx_Z) / len(SelectionVx_Z)
                            print(AverageZ)

                            AverageCoordinates = [AverageX, AverageY, AverageZ]
                            context.scene.cursor.location = AverageCoordinates

                        except:
                            pass
                            

                return {"FINISHED"}

        if (self.SourceSnapping == "SCENE_CURSOR"):
            if (self.TargetSnapping == "SELECTED"):
                if (self.SubTargetSnapping == "OBJECT"):
                    if (len(context.selected_objects) != 0):
                        for Object in context.selected_objects:
                                Object.location = context.scene.cursor.location
                if (self.SubTargetSnapping == "ORIGIN"):
                    if (len(context.selected_objects) != 0):
                        for Object in context.selected_objects:
                            bpy.context.view_layer.objects.active = Object
                            bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

                    

                    return {"FINISHED"}
        
        if (self.SourceSnapping == "RESET"):
            if (self.TargetSnapping == "SCENE_CURSOR"):
                context.scene.cursor.location = [0.0, 0.0, 0.0]
                return {"FINISHED"}

            return {"FINISHED"}

        return {"FINISHED"}

class Alx_OT_Scene_VisibilityIsolator(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_scene_visibility_isolator"
    bl_options = {"INTERNAL"}

    TargetVisibility : bpy.props.BoolProperty(name="", default=False, options={"HIDDEN"})
    UseObject : bpy.props.BoolProperty(name="", default=False, options={"HIDDEN"})
    UseCollection : bpy.props.BoolProperty(name="", default=False, options={"HIDDEN"})

    @classmethod
    def poll(self, context):
        return context.area.type == "VIEW_3D"

    def execute(self, context):
        if (len(context.scene.alx_addon_properties.SceneIsolatorVisibilityTarget) != 0):
            TargetType = set(Target for Target in context.scene.alx_addon_properties.SceneIsolatorVisibilityTarget)
            SceneCollectionContext = [Object.users_collection[0] for Object in context.selected_objects if (Object.users_collection[0] is not None)]

            IsolatorSelectionSet = [Object for Object in context.scene.objects if ((Object is not None) and (len(context.selected_objects) != 0) and (Object not in context.selected_objects))]
            IsolatorCollectionSet = [Collection for Collection in bpy.data.collections for SceneCollection in SceneCollectionContext if (SceneCollection is not Collection) and (SceneCollection not in Collection.children_recursive)]

            if (self.UseObject == True):
                try:
                    IsolatorSelectionSet[0]

                    bpy.types.Scene.alx_scene_isolator_visibility_object_list = IsolatorSelectionSet

                    if (self.UseObject == True):
                        for Object in IsolatorSelectionSet:
                            if (Object is not None):
                                if ("VIEWPORT" in TargetType):
                                    Object.hide_viewport = not self.TargetVisibility
                                if ("RENDER" in TargetType):
                                    Object.hide_render = not self.TargetVisibility
                except:
                    try:
                        if (self.UseObject == True):
                            context.scene.alx_scene_isolator_visibility_object_list[0]
                            for Object in context.scene.alx_scene_isolator_visibility_object_list:
                                if (Object is not None):
                                    if ("VIEWPORT" in TargetType):
                                        Object.hide_viewport = not self.TargetVisibility
                                    if ("RENDER" in TargetType):
                                        Object.hide_render = not self.TargetVisibility
                    except:
                        pass

            if (self.UseCollection == True):
                try:
                    IsolatorCollectionSet[0]

                    bpy.types.Scene.alx_scene_isolator_visibility_collection_list = IsolatorCollectionSet

                    for Collection in IsolatorCollectionSet:
                        if ("VIEWPORT" in TargetType):
                            Collection.hide_viewport = not self.TargetVisibility
                        if ("RENDER" in TargetType):
                            Collection.hide_render = not self.TargetVisibility
                except:
                    try:
                        bpy.types.Scene.alx_scene_isolator_visibility_collection_list[0]
                        for Collection in bpy.types.Scene.alx_scene_isolator_visibility_collection_list:
                            if ("VIEWPORT" in TargetType):
                                Collection.hide_viewport = not self.TargetVisibility
                            if ("RENDER" in TargetType):
                                Collection.hide_render = not self.TargetVisibility
                    except:
                        pass

        return {"FINISHED"}

class Alx_OT_Modifier_ManageOnSelected(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_modifier_manage_on_selected"
    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    UseCreateDuplicate : bpy.props.BoolProperty(name="Create Duplicates", default=False)
    ModifierTypeSelection : bpy.props.EnumProperty(name="Modifiers Type", options={'ENUM_FLAG'}, items=AlxUtils.AlxModifierEnumItemsPreset)

    @classmethod
    def poll(self, context):
        return context.area.type == "VIEW_3D"

    def execute(self, context):
        for Object in context.selected_objects:
            if (Object is not None):
                for ModType in self.ModifierTypeSelection:
                    if (self.UseCreateDuplicate == False):
                        if (AlxUtils.AlxRetiriveObjectModifier(Object, ModType) is None):
                            Object.modifiers.new(name="", type=ModType)

                    if (self.UseCreateDuplicate == True):
                        Object.modifiers.new(name="", type=ModType)

        return {"FINISHED"}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

class Alx_OT_Mesh_BoundaryMultiTool(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_mesh_boundary_multi_tool"

    KeepDividingEdges : bpy.props.BoolProperty(name="Keep Non-Boundary", default=False)

    UseCrease : bpy.props.BoolProperty(name="Crease", default=False)
    UsePin : bpy.props.BoolProperty(name="Use as Pin", default=False)
    

    @classmethod
    def poll(self, context):
        return context.area.type == "VIEW_3D"
    
    def execute(self, context):
        ContextMesh = None
        ContextBMesh = None

        if (context.mode == "EDIT_MESH") and (context.edit_object.type == "MESH"):
            ContextMesh = context.edit_object.data
            ContextBMesh = bmesh.from_edit_mesh(context.edit_object.data)

            if (ContextBMesh is not None):
                BoundaryVertex = []
                BoundaryEdge = []
                DividingNonBoundaryEdge = []
                for SelectionItem in ContextBMesh.select_history:
                    if (SelectionItem is not None) and (SelectionItem.__class__ is bmesh.types.BMFace):
                        NonBoundaryEdge = []

                        for Edge in SelectionItem.edges:
                            if (Edge.is_boundary == True):
                                BoundaryVertex.extend([Vertex for Vertex in Edge.verts if (Vertex not in BoundaryVertex)])
                                if (Edge not in BoundaryEdge):
                                    BoundaryEdge.append(Edge)

                        for Vertex in BoundaryVertex:
                            for Edge in Vertex.link_edges:
                                if (Edge.is_boundary == False):
                                    if (Edge not in NonBoundaryEdge):
                                        NonBoundaryEdge.append(Edge)
                                    if (Edge in NonBoundaryEdge):
                                        DividingNonBoundaryEdge.append(Edge)

                if (self.UsePin == True):
                    PinGroup = None

                    for VxGroup in context.edit_object.vertex_groups:
                        if (PinGroup is None) and (VxGroup.name.lower() == "pin"):
                            PinGroup = VxGroup
                    else:
                        if (PinGroup is None):
                            PinGroup = context.edit_object.vertex_groups.new(name="Pin")

                    if (PinGroup is not None):
                        PinGroup.name = "Pin"

                    AddVertex = [Vertex.index for Vertex in BoundaryVertex]
                    if (self.KeepDividingEdges == False):
                        RemoveVertex = [Vertex.index for Edge in DividingNonBoundaryEdge for Vertex in Edge.verts]

                if(self.UseCrease == True):
                    CreaseLayer = ContextBMesh.edges.layers.float.get('crease_edge', None)
                    for CreaseEdge in BoundaryEdge:
                        ContextBMesh.edges[CreaseEdge.index][CreaseLayer] = 1.0
                    bmesh.update_edit_mesh(ContextMesh, loop_triangles=False)

                bpy.ops.object.mode_set(mode="OBJECT")
                if (self.UsePin):
                    PinGroup.add(index=AddVertex, weight=1.0, type="REPLACE")
                    if (self.KeepDividingEdges == False):
                        PinGroup.remove(index=RemoveVertex)
                bpy.ops.object.mode_set(mode="EDIT")

        

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

class Alx_OT_Mesh_EditAttributes(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_mesh_edit_attributes"

    AttributeName : bpy.props.StringProperty(name="Attribute Name", default="")
    CreateMissingAttribute : bpy.props.BoolProperty(name="Create Missing Attribute")
    AttributeDomainType : bpy.props.EnumProperty(name="Attribute Type", default=0, items=[("POINT", "Vertex", ""), ("EDGE", "Edge", "")])
    AttributeType : bpy.props.EnumProperty(name="Attribute Type", default=0, items=[("FLOAT_COLOR", "Float Color", "")])
    ColorValue : bpy.props.FloatVectorProperty(name="Color", subtype="COLOR", size=4, default=[0.0,0.0,0.0,0.0], min=0.0, max=1.0)

    @classmethod
    def poll(self, context):
        return context.area.type == "VIEW_3D" and context.mode == "EDIT_MESH"
    
    def execute(self, context):
        if (context.edit_object is not None):
            if (context.mode == "EDIT_MESH") and (context.edit_object.type == "MESH"):
                ContextMesh = context.edit_object.data
                ContextBMesh = bmesh.from_edit_mesh(context.edit_object.data)

                SelectedVertex = [Vertex.index for Vertex in ContextBMesh.verts if Vertex.select == True]

                bpy.ops.object.mode_set(mode="OBJECT")

                ContextAttribute = None

                if (self.CreateMissingAttribute == False):
                    ContextAttribute = ContextMesh.attributes.get(self.AttributeName)
                if (self.CreateMissingAttribute == True):
                    if (ContextMesh.attributes.get(self.AttributeName) is None):
                        ContextMesh.attributes.new(name=self.AttributeName, type=self.AttributeType, domain=self.AttributeDomainType)

                if (ContextAttribute is not None):
                    if (self.AttributeDomainType == "POINT"):
                        for Vertex in SelectedVertex:

                            if (self.AttributeType == "FLOAT_COLOR"):
                                ContextAttribute.data[Vertex].color = self.ColorValue

                    bpy.ops.object.mode_set(mode="EDIT")

    
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)








class Alx_OT_Armature_AssignToSelection(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.armature_assign_to_selection"
    bl_description = "Assigns any [Mesh] in the current selection to the [Armature] within said selection"

    bl_options = {"INTERNAL","REGISTER", "UNDO"}

    # def UpdateUseAutomaticWeight(self, context):
    #     if (self.UseAutomaticWeight == True):
    #         self.UseSingleVxGroup = False
    #         self.UsePurgeOtherGroups = False
    #         self.VxGroupName = ""

    # def UpdateUsePreserveExistingGroups(self, context):
    #     if (self.UsePreserveExistingGroups == True):
    #         self.UseAutomaticWeight = True
    #         self.UseSingleVxGroup = False
    #         self.UsePurgeOtherGroups = False
    #         self.VxGroupName = ""
        
    def UpdateUseSingleVxGroup(self, context):
        # if (self.UseSingleVxGroup == True):
        #     self.UseAutomaticWeight = False
        #     self.UsePreserveExistingGroups = False
        pass

    def UpdateUsePurgeOtherGroups(self, context):
        if (self.UsePurgeOtherGroups == True):
            self.UseSingleVxGroup = True
            #self.UseAutomaticWeight = False
            #self.UsePreserveExistingGroups = False

    def UpdateVxGroupName(self, context):
        if (self.VxGroupName != ""):
            self.UseSingleVxGroup = True

    UseParent : bpy.props.BoolProperty(name="Should Parent", default=False)

    #UseAutomaticWeight : BoolProperty(name="Automatic Weights", default=False, update=UpdateUseAutomaticWeight)
    #UsePreserveExistingGroups : BoolProperty(name="Preserve Existing VxGroups", default=False, update=UpdateUsePreserveExistingGroups)

    UseSingleVxGroup : bpy.props.BoolProperty(name="Single VxGroup", default=False, update=UpdateUseSingleVxGroup)
    CreateMissingVxGroups : bpy.props.BoolProperty(name="Create Missing VxGroups", default=False)
    UsePurgeOtherGroups : bpy.props.BoolProperty(name="PURGE Other VxGroups", description="PURGE any other VxGroup that does not correspon to the specified single VxGroup", default=False, update=UpdateUsePurgeOtherGroups)
    VxGroupName : bpy.props.StringProperty(name="Group", default="", update=UpdateVxGroupName)

    @classmethod
    def poll(self, context):
        return context.area.type == "VIEW_3D"

    def execute(self, context):
        Armature = None

        if (len(context.selected_objects) != 0):
            for SelectedObject in context.selected_objects:
                if (Armature is None) and (SelectedObject.type == "ARMATURE"):
                    Armature = SelectedObject
                    
            for SelectedObject in context.selected_objects:
                if (Armature is not None):
                    if (SelectedObject.type == "MESH"):
                        ArmatureModifier = AlxUtils.AlxRetiriveObjectModifier(SelectedObject, "ARMATURE")

                        if (ArmatureModifier is None):
                            ArmatureModifier = SelectedObject.modifiers.new(name="Armature", type="ARMATURE")

                        if (ArmatureModifier is not None):
                            ArmatureModifier.object = Armature

                        if (self.UseParent == True):
                            SelectedObject.parent = Armature
                            SelectedObject.matrix_parent_inverse = Armature.matrix_world.inverted()

                        # if (self.UseAutomaticWeight == True):
                        #     bpy.ops.alx.automatic_mode_changer(DefaultBehaviour=False, TargetMode="PAINT_WEIGHT", TargetObject=SelectedObject.name, TargetArmature=self.TargetArmature)
                        #     #bpy.ops.paint.weight_from_bones(type='AUTOMATIC')

                        if (self.UseSingleVxGroup == True):
                            if (self.CreateMissingVxGroups == True):
                                if (self.VxGroupName != "") and (self.VxGroupName not in SelectedObject.vertex_groups):
                                    VxGroup = SelectedObject.vertex_groups.new()
                                    VxGroup.name = self.VxGroupName
                            if (self.VxGroupName != "") and (self.VxGroupName in SelectedObject.vertex_groups):
                                VxGroup = SelectedObject.vertex_groups.get(self.VxGroupName)
                                
                                if (VxGroup is not None):
                                    VxGroup.add(range(0, len(SelectedObject.data.vertices)), 1.0, 'REPLACE')
                        
                        if (self.UsePurgeOtherGroups == True):
                            if (self.VxGroupName != "") and (self.VxGroupName in SelectedObject.vertex_groups):
                                for ObjectVxGroup in SelectedObject.vertex_groups:
                                    if (ObjectVxGroup.name != self.VxGroupName):
                                        SelectedObject.vertex_groups.remove(ObjectVxGroup)
                                                
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

class Alx_OT_Armature_MatchIKByMirroredName(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.bone_match_ik_by_mirrored_name"

    bl_description = "Requires [Pose Mode] Mirrors IK Data from the source side to the opposite"

    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    SourceSide : bpy.props.EnumProperty(name="Mirror From", default=1, items=[("LEFT", "Left", "", 1), ("RIGHT", "Right", "", 2)])

    @classmethod
    def poll(self, context):
        return context.area.type == "VIEW_3D" and context.mode == "POSE"

    def execute(self, context):
        if (context.active_object is not None) and (context.active_object.type == "ARMATURE") and (context.mode == "POSE"):

            ContextArmature = context.active_object

            if (ContextArmature is not None):

                PoseBoneData = ContextArmature.pose.bones

                SymmetricPairBones = []
                SymmetricUniqueBones = []
                
                if (self.SourceSide == "LEFT"):
                    SymmetricPairBones = [PoseBone for PoseBone in PoseBoneData if ((PoseBone.name[-1].lower() == "l"))]
                
                if (self.SourceSide == "RIGHT"):
                    SymmetricPairBones = [PoseBone for PoseBone in PoseBoneData if ((PoseBone.name[-1].lower() == "r"))]
                
                for PoseBone in SymmetricPairBones:
                    if (PoseBone not in SymmetricUniqueBones):
                        SymmetricUniqueBones.append(PoseBone)

                for UniquePoseBone in SymmetricUniqueBones:
                    ContextPoseBone = None
                    ContextOppositeBone = None

                    if (self.SourceSide == "LEFT"):
                        ContextPoseBone = AlxUtils.AlxGetBoneAlwaysLeft(UniquePoseBone, ContextArmature)
                        ContextOppositeBone = AlxUtils.AlxGetBoneOpposite(AlxUtils.AlxGetBoneAlwaysLeft(UniquePoseBone, ContextArmature), ContextArmature)
                    
                    if (self.SourceSide == "RIGHT"):
                        ContextPoseBone = AlxUtils.AlxGetBoneAlwaysRight(UniquePoseBone, ContextArmature)
                        ContextOppositeBone = AlxUtils.AlxGetBoneOpposite(AlxUtils.AlxGetBoneAlwaysRight(UniquePoseBone, ContextArmature), ContextArmature)

                    if (ContextPoseBone is not None) and (ContextOppositeBone is not None):
                        AlxUtils.AlxCloneIKSettings(ContextPoseBone, ContextOppositeBone)
                        AlxUtils.AlxCloneIKBoneLimitOnChain(ContextPoseBone, ContextArmature)
        
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

class Alx_OT_Modifier_HideOnSelected(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.modifier_selection_visibility"

    ShowModiferEdit : bpy.props.BoolProperty(name="Show Edit:", default=True)
    ShowModiferViewport : bpy.props.BoolProperty(name="Show Viewport:", default=True)
    ShowModiferRender : bpy.props.BoolProperty(name="Show Render:", default=True)

    BevelMod : bpy.props.BoolProperty(name="Bevel", default=False)
    SubdivisionMod : bpy.props.BoolProperty(name="Subdivision", default=False)
    SolidifyMod : bpy.props.BoolProperty(name="Solidify", default=False)

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

    def execute(self, context):
        ModifiersList = []

        if (self.BevelMod == True):
            ModifiersList.append("BEVEL")
        if (self.SubdivisionMod == True):
            ModifiersList.append("SUBSURF")
        if (self.SolidifyMod == True):
            ModifiersList.append("SOLIDIFY")

        for Object in bpy.context.selected_objects:
            if (Object is not None) and (len(Object.modifiers) != 0) and (Object.type in ["MESH", "ARMATURE", "CURVE"]):
                ObjectModfiers = getattr(Object, "modifiers", [])

                for ObjectModifier in ObjectModfiers:
                    if (ObjectModifier is not None) and (ObjectModifier.type in ModifiersList):
                        ObjectModifier.show_in_editmode = self.ShowModiferEdit
                        ObjectModifier.show_viewport = self.ShowModiferViewport
                        ObjectModifier.show_render = self.ShowModiferRender                
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
   