import bpy


def AlxRetirive_ModifierList(TargetObejct, TargetType):
    mod_type_list = bpy.types.Modifier.bl_rna.properties['type'].enum_items

    if (TargetType in mod_type_list):
        return [modifier for modifier in TargetObejct.modifiers if (modifier.type == TargetType)]

    return None


class Alx_OT_Modifier_ManageOnSelected(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_modifier_manage_on_selected"
    bl_options = {"INTERNAL", "REGISTER", "UNDO"}

    object_pointer_reference: bpy.props.StringProperty(name="", default="", options={"HIDDEN"})  # type:ignore
    object_modifier_index: bpy.props.IntProperty(name="", default=0, options={"HIDDEN"})  # type:ignore

    modifier: bpy.types.Modifier = None

    modifier_type: bpy.props.StringProperty(name="", default="NONE", options={"HIDDEN"})  # type:ignore

    create_modifier: bpy.props.BoolProperty(name="", default=False, options={"HIDDEN"})  # type:ignore
    apply_modifier: bpy.props.BoolProperty(name="", default=False, options={"HIDDEN"})  # type:ignore
    remove_modifier: bpy.props.BoolProperty(name="", default=False, options={"HIDDEN"})  # type:ignore

    move_modifier_up: bpy.props.BoolProperty(name="", default=False, options={"HIDDEN"})  # type:ignore
    move_modifier_down: bpy.props.BoolProperty(name="", default=False, options={"HIDDEN"})  # type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def execute(self, context):
        if (self.modifier is None):

            if (self.create_modifier == True):

                for Object in context.selected_objects:
                    if (Object is not None):
                        try:
                            self.modifier = Object.modifiers.new(name="", type=self.modifier_type)

                            match self.modifier.type:
                                case "BEVEL":
                                    self.modifier.width = 0.01
                                    self.modifier.segments = 1
                                    self.modifier.miter_outer = "MITER_ARC"
                                    self.modifier.harden_normals = True

                                case "SUBSURF":
                                    self.modifier.render_levels = 1
                                    self.modifier.quality = 6
                        except:
                            pass

                return {"FINISHED"}

            Object: bpy.types.Object = bpy.data.objects.get(self.object_pointer_reference)

            if (self.apply_modifier == True):
                if (Object is not None):
                    _mode = context.mode if (context.mode[0:4] != "EDIT") else "EDIT" if (context.mode[0:4] == "EDIT") else "OBJECT"

                    bpy.ops.object.mode_set(mode="OBJECT")
                    with context.temp_override(object=Object):
                        bpy.ops.object.modifier_apply(modifier=Object.modifiers[self.object_modifier_index].name)
                    bpy.ops.object.mode_set(mode=_mode)
                return {"FINISHED"}

            if (self.remove_modifier == True):
                if (Object is not None):
                    Object.modifiers.remove(Object.modifiers.get(Object.modifiers[self.object_modifier_index].name))
                return {"FINISHED"}

        try:
            if (self.move_modifier_up == True) and (self.move_modifier_down == False):
                if (Object is not None):
                    if ((self.object_modifier_index - 1) >= 0):
                        Object.modifiers.move(self.object_modifier_index, self.object_modifier_index - 1)
                return {"FINISHED"}

            if (self.move_modifier_up == False) and (self.move_modifier_down == True):
                if (Object is not None):
                    if ((self.object_modifier_index + 1) < len(Object.modifiers)):
                        Object.modifiers.move(self.object_modifier_index, self.object_modifier_index + 1)
                return {"FINISHED"}

        except Exception as error:
            print(error)

        return {"FINISHED"}


class Alx_OT_Modifier_ApplyReplace(bpy.types.Operator):
    """"""

    bl_label = "Modifier Apply Replace"
    bl_idname = "alx.operator_modifier_apply_replace"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def auto_object_modifier(scene, context: bpy.types.Context):
        if (context.object is not None):
            modifier_list = [(modifier.type, modifier.name, "") for modifier in context.object.modifiers]
        return modifier_list

    replace_type: bpy.props.EnumProperty(name="Modifier", items=auto_object_modifier)  # type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def execute(self, context: bpy.types.Context):
        try:
            context.selectable_objects[0]

            for selected_object in context.selected_objects:
                modifiers = AlxRetirive_ModifierList(selected_object, self.replace_type)

                context.view_layer.objects.active = selected_object

                for modifier in modifiers:
                    backup_modifier = dict()
                    for attr in dir(modifier):
                        backup_modifier[attr] = getattr(modifier, attr)

                    modifier_index = selected_object.modifiers.find(modifier.name)
                    _mode = context.mode if (context.mode[0:4] != "EDIT") else "EDIT" if (context.mode[0:4] == "EDIT") else "OBJECT"
                    bpy.ops.object.mode_set(mode="OBJECT")
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                    bpy.ops.object.mode_set(mode=_mode)

                    new_modifier = selected_object.modifiers.new(name=backup_modifier["name"], type=backup_modifier["type"])

                    for mod_setting in dir(new_modifier):
                        try:
                            setattr(new_modifier, mod_setting, backup_modifier[mod_setting])
                        except:
                            pass

                    new_index = selected_object.modifiers.find(new_modifier.name)
                    try:
                        selected_object.modifiers.move(new_index, modifier_index)
                    except Exception as error:
                        print(error)

        except Exception as error:
            print(error)

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class Alx_OT_Modifier_BatchVisibility(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_modifier_batch_visibility"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def auto_retrieve_selection_modifier(scene, context: bpy.types.Context):
        unique_modifier_type_set = set()
        unique_modifier_type_set.add(("NONE", "none", ""))

        if (len(context.selectable_objects) != 0):
            [unique_modifier_type_set.add((modifier.type, modifier.name, "")) for object in context.selectable_objects for modifier in object.modifiers]

        return unique_modifier_type_set

    modifier_type: bpy.props.EnumProperty(name="modifier type", items=auto_retrieve_selection_modifier)  # type:ignore
    show_edit: bpy.props.BoolProperty(name="edit", default=False)  # type:ignore
    show_viewport: bpy.props.BoolProperty(name="viewport", default=False)  # type:ignore
    show_render: bpy.props.BoolProperty(name="render", default=False)  # type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def execute(self, context: bpy.types.Context):
        if (self.modifier_type != ""):
            for object in context.selected_objects:
                modifier = AlxRetirive_ModifierList(object, self.modifier_type)

                for mod in modifier:
                    mod.show_in_editmode = self.show_edit
                    mod.show_viewport = self.show_viewport
                    mod.show_render = self.show_render

        return {"FINISHED"}

    def draw(self, context: bpy.types.Context):
        self.layout.row().prop(self, "modifier_type", text="modifier")
        row = self.layout.row().split(factor=0.33)
        row.prop(self, "show_edit", toggle=True, icon="EDITMODE_HLT")
        row.prop(self, "show_viewport", toggle=True, icon="RESTRICT_VIEW_OFF")
        row.prop(self, "show_render", toggle=True, icon="RESTRICT_RENDER_OFF")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class Alx_PT_Operator_ModifierChangeSettings(bpy.types.Operator):
    """"""

    bl_label = ""
    bl_idname = "alx.operator_modifier_change_settings"

    object_name: bpy.props.StringProperty()  # type:ignore
    modifier_name: bpy.props.StringProperty()  # type:ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def execute(self, context: bpy.types.Context):
        Object = context.scene.objects.get(self.object_name)
        Modifier = Object.alx_modifier_collection.get(
            f"{self.object_name}_{self.modifier_name}")
        Modifier.show_options = not Modifier.show_options
        return {"FINISHED"}
