import bpy
from .addon_updater_utils import get_addon_preferences, ui_refresh

addon_name = str.lower(__package__)
addon_updater = None


class AddonUpdaterCheckNow(bpy.types.Operator):
    bl_label = f"Check now for {addon_name} update"
    bl_idname = f"{addon_name}.updater_check_now"
    bl_description = f"Check now for an update to the {addon_name} addon"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        if addon_updater.invalid_updater:
            return {'CANCELLED'}

        if addon_updater.async_checking and addon_updater.error is None:
            # Check already happened.
            # Used here to just avoid constant applying settings below.
            # Ignoring if error, to prevent being stuck on the error screen.
            return {'CANCELLED'}

        # apply the UI settings
        settings = get_addon_preferences(context)
        if not settings:
            addon_updater.print_verbose(
                "Could not get {} preferences, update check skipped".format(
                    __package__))
            return {'CANCELLED'}

        addon_updater.set_check_interval(
            enabled=settings.auto_check_update,
            months=settings.updater_interval_months,
            days=settings.updater_interval_days,
            hours=settings.updater_interval_hours,
            minutes=settings.updater_interval_minutes)

        # Input is an optional callback function. This function should take a
        # bool input. If true: update ready, if false: no update ready.
        addon_updater.check_for_update_now(ui_refresh)

        return {'FINISHED'}
