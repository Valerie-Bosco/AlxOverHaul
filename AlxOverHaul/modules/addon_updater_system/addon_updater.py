# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


"""
See documentation for usage
https://github.com/CGCookie/blender-addon-updater
"""


from bpy.app.handlers import persistent
import addon_utils
import bpy
from datetime import datetime, timedelta
import fnmatch
import threading
import shutil
import zipfile
import json
import os
import urllib
import urllib.request
import ssl
import platform
import traceback
import errno
from typing import Optional
from contextlib import redirect_stdout


from bpy.app.handlers import persistent
import os
import traceback


from .addon_updater_utils import get_addon_preferences
from . import addon_updater_operators
from .addon_updater_operators import AddonUpdaterCheckNow

import bpy

###
addon_name = ""
addon_updater = None
###


class AddonUpdaterUpdateTarget(bpy.types.Operator):
    bl_label = f"{addon_name} version target"
    bl_idname = f"{addon_name}.updater_update_target"
    bl_description = f"Install a targeted version of the {addon_name} addon"
    bl_options = {'REGISTER', 'INTERNAL'}

    def target_version(self, context):
        # In case of error importing updater.
        if addon_updater.invalid_updater:
            ret = []

        ret = []
        i = 0
        for tag in addon_updater.tags:
            ret.append((tag, tag, "Select to install " + tag))
            i += 1
        return ret

    target = bpy.props.EnumProperty(
        name="Target version to install",
        description="Select the version to install",
        items=target_version
    )

    # If true, run clean install - ie remove all files before adding new
    # equivalent to deleting the addon and reinstalling, except the
    # updater folder/backup folder remains.
    clean_install = bpy.props.BoolProperty(
        name="Clean install",
        description=("If enabled, completely clear the addon's folder before "
                     "installing new update, creating a fresh install"),
        default=False,
        options={'HIDDEN'}
    )

    @classmethod
    def poll(cls, context):
        if addon_updater.invalid_updater:
            return False
        return addon_updater.update_ready is not None and len(addon_updater.tags) > 0

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if addon_updater.invalid_updater:
            layout.label(text="Updater error")
            return
        split = layout.split(factor=0.5)
        sub_col = split.column()
        sub_col.label(text="Select install version")
        sub_col = split.column()
        sub_col.prop(self, "target", text="")

    def execute(self, context):
        # In case of error importing updater.
        if addon_updater.invalid_updater:
            return {'CANCELLED'}

        res = addon_updater.run_update(
            force=False,
            revert_tag=self.target,
            callback=post_update_callback,
            clean=self.clean_install)

        # Should return 0, if not something happened.
        if res == 0:
            addon_updater.print_verbose("Updater returned successful")
        else:
            addon_updater.print_verbose(
                "Updater returned {}, , error occurred".format(res))
            return {'CANCELLED'}

        return {'FINISHED'}


class AddonUpdaterInstallManually(bpy.types.Operator):
    """As a fallback, direct the user to download the addon manually"""
    bl_label = "Install update manually"
    bl_idname = f"{addon_name}.updater_install_manually"
    bl_description = "Proceed to manually install update"
    bl_options = {'REGISTER', 'INTERNAL'}

    error = bpy.props.StringProperty(
        name="Error Occurred",
        default="",
        options={'HIDDEN'}
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        layout = self.layout

        if addon_updater.invalid_updater:
            layout.label(text="Updater error")
            return

        # Display error if a prior autoamted install failed.
        if self.error != "":
            col = layout.column()
            col.scale_y = 0.7
            col.label(text="There was an issue trying to auto-install",
                      icon="ERROR")
            col.label(text="Press the download button below and install",
                      icon="BLANK1")
            col.label(text="the zip file like a normal addon.", icon="BLANK1")
        else:
            col = layout.column()
            col.scale_y = 0.7
            col.label(text="Install the addon manually")
            col.label(text="Press the download button below and install")
            col.label(text="the zip file like a normal addon.")

        # If check hasn't happened, i.e. accidentally called this menu,
        # allow to check here.

        row = layout.row()

        if addon_updater.update_link is not None:
            row.operator(
                "wm.url_open",
                text="Direct download").url = addon_updater.update_link
        else:
            row.operator(
                "wm.url_open",
                text="(failed to retrieve direct download)")
            row.enabled = False

            if addon_updater.website is not None:
                row = layout.row()
                ops = row.operator("wm.url_open", text="Open website")
                ops.url = addon_updater.website
            else:
                row = layout.row()
                row.label(text="See source website to download the update")

    def execute(self, context):
        return {'FINISHED'}


class AddonUpdaterUpdatedSuccessful(bpy.types.Operator):
    """Addon in place, popup telling user it completed or what went wrong"""
    bl_label = "Installation Report"
    bl_idname = f"{addon_name}.updater_update_successful"
    bl_description = "Update installation response"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    error = bpy.props.StringProperty(
        name="Error Occurred",
        default="",
        options={'HIDDEN'}
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)

    def draw(self, context):
        layout = self.layout

        if addon_updater.invalid_updater:
            layout.label(text="Updater error")
            return

        saved = addon_updater.json
        if self.error != "":
            col = layout.column()
            col.scale_y = 0.7
            col.label(text="Error occurred, did not install", icon="ERROR")
            if addon_updater.error_msg:
                msg = addon_updater.error_msg
            else:
                msg = self.error
            col.label(text=str(msg), icon="BLANK1")
            rw = col.row()
            rw.scale_y = 2
            rw.operator(
                "wm.url_open",
                text="Click for manual download.",
                icon="BLANK1").url = addon_updater.website
        elif not addon_updater.auto_reload_post_update:
            # Tell user to restart blender after an update/restore!
            if "just_restored" in saved and saved["just_restored"]:
                col = layout.column()
                col.label(text="Addon restored", icon="RECOVER_LAST")
                alert_row = col.row()
                alert_row.alert = True
                alert_row.operator(
                    "wm.quit_blender",
                    text="Restart blender to reload",
                    icon="BLANK1")
                addon_updater.json_reset_restore()
            else:
                col = layout.column()
                col.label(
                    text="Addon successfully installed", icon="FILE_TICK")
                alert_row = col.row()
                alert_row.alert = True
                alert_row.operator(
                    "wm.quit_blender",
                    text="Restart blender to reload",
                    icon="BLANK1")

        else:
            # reload addon, but still recommend they restart blender
            if "just_restored" in saved and saved["just_restored"]:
                col = layout.column()
                col.scale_y = 0.7
                col.label(text="Addon restored", icon="RECOVER_LAST")
                col.label(
                    text="Consider restarting blender to fully reload.",
                    icon="BLANK1")
                addon_updater.json_reset_restore()
            else:
                col = layout.column()
                col.scale_y = 0.7
                col.label(
                    text="Addon successfully installed", icon="FILE_TICK")
                col.label(
                    text="Consider restarting blender to fully reload.",
                    icon="BLANK1")

    def execute(self, context):
        return {'FINISHED'}


class AddonUpdaterRestoreBackup(bpy.types.Operator):
    """Restore addon from backup"""
    bl_label = "Restore backup"
    bl_idname = f"{addon_name}.updater_restore_backup"
    bl_description = "Restore addon from backup"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        try:
            return os.path.isdir(os.path.join(addon_updater.stage_path, "backup"))
        except:
            return False

    def execute(self, context):
        # in case of error importing updater
        if addon_updater.invalid_updater:
            return {'CANCELLED'}
        addon_updater.restore_backup()
        return {'FINISHED'}


class AddonUpdaterIgnore(bpy.types.Operator):
    """Ignore update to prevent future popups"""
    bl_label = "Ignore update"
    bl_idname = f"{addon_name}.updater_ignore"
    bl_description = "Ignore update to prevent future popups"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if addon_updater.invalid_updater:
            return False
        elif addon_updater.update_ready:
            return True
        else:
            return False

    def execute(self, context):
        # in case of error importing updater
        if addon_updater.invalid_updater:
            return {'CANCELLED'}
        addon_updater.ignore_update()
        self.report({"INFO"}, "Open addon preferences for updater options")
        return {'FINISHED'}


class AddonUpdaterEndBackground(bpy.types.Operator):
    """Stop checking for update in the background"""
    bl_label = "End background check"
    bl_idname = f"{addon_name}.end_background_check"
    bl_description = "Stop checking for update in the background"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        # in case of error importing updater
        if addon_updater.invalid_updater:
            return {'CANCELLED'}
        addon_updater.stop_async_check_update()
        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Handler related, to create popups
# -----------------------------------------------------------------------------


@persistent
def updater_run_install_popup_handler(scene):
    global ran_auto_check_install_popup
    ran_auto_check_install_popup = True
    addon_updater.print_verbose("Running the install popup handler.")

    # in case of error importing updater
    if addon_updater.invalid_updater:
        return

    try:
        if "scene_update_post" in dir(bpy.app.handlers):
            bpy.app.handlers.scene_update_post.remove(
                updater_run_install_popup_handler)
        else:
            bpy.app.handlers.depsgraph_update_post.remove(
                updater_run_install_popup_handler)
    except:
        pass

    if "ignore" in addon_updater.json and addon_updater.json["ignore"]:
        return  # Don't do popup if ignore pressed.
    elif "version_text" in addon_updater.json and addon_updater.json["version_text"].get("version"):
        version = addon_updater.json["version_text"]["version"]
        ver_tuple = addon_updater.version_tuple_from_text(version)

        if ver_tuple < addon_updater.current_version:
            # User probably manually installed to get the up to date addon
            # in here. Clear out the update flag using this function.
            addon_updater.print_verbose(
                "{} updater: appears user updated, clearing flag".format(
                    addon_updater.addon))
            addon_updater.json_reset_restore()
            return
    atr = AddonUpdaterInstallPopup.bl_idname.split(".")
    getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')


def background_update_callback(update_ready):
    """Passed into the updater, background thread updater"""
    global ran_auto_check_install_popup
    addon_updater.print_verbose("Running background update callback")

    # In case of error importing updater.
    if addon_updater.invalid_updater:
        return
    if not addon_updater.show_popups:
        return
    if not update_ready:
        return

    # See if we need add to the update handler to trigger the popup.
    handlers = []
    if "scene_update_post" in dir(bpy.app.handlers):  # 2.7x
        handlers = bpy.app.handlers.scene_update_post
    else:  # 2.8+
        handlers = bpy.app.handlers.depsgraph_update_post
    in_handles = updater_run_install_popup_handler in handlers

    if in_handles or ran_auto_check_install_popup:
        return

    if "scene_update_post" in dir(bpy.app.handlers):  # 2.7x
        bpy.app.handlers.scene_update_post.append(
            updater_run_install_popup_handler)
    else:  # 2.8+
        bpy.app.handlers.depsgraph_update_post.append(
            updater_run_install_popup_handler)
    ran_auto_check_install_popup = True
    addon_updater.print_verbose("Attempted popup prompt")


def post_update_callback(module_name, res=None):
    """Callback for once the run_update function has completed.

    Only makes sense to use this if "auto_reload_post_update" == False,
    i.e. don't auto-restart the addon.

    Arguments:
        module_name: returns the module name from updater, but unused here.
        res: If an error occurred, this is the detail string.
    """

    # In case of error importing updater.
    if addon_updater.invalid_updater:
        return

    if res is None:
        # This is the same code as in conditional at the end of the register
        # function, ie if "auto_reload_post_update" == True, skip code.
        addon_updater.print_verbose(
            "{} updater: Running post update callback".format(addon_updater.addon))

        atr = AddonUpdaterUpdatedSuccessful.bl_idname.split(".")
        getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')
        global ran_update_success_popup
        ran_update_success_popup = True
    else:
        # Some kind of error occurred and it was unable to install, offer
        # manual download instead.
        atr = AddonUpdaterUpdatedSuccessful.bl_idname.split(".")
        getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT', error=res)
    return


def check_for_update_background():
    """Function for asynchronous background check.

    *Could* be called on register, but would be bad practice as the bare
    minimum code should run at the moment of registration (addon ticked).
    """
    if addon_updater.invalid_updater:
        return
    global ran_background_check
    if ran_background_check:
        # Global var ensures check only happens once.
        return
    elif addon_updater.update_ready is not None or addon_updater.async_checking:
        # Check already happened.
        # Used here to just avoid constant applying settings below.
        return

    # Apply the UI settings.
    settings = get_addon_preferences(bpy.context)
    if not settings:
        return
    addon_updater.set_check_interval(enabled=settings.auto_check_update,
                                     months=settings.updater_interval_months,
                                     days=settings.updater_interval_days,
                                     hours=settings.updater_interval_hours,
                                     minutes=settings.updater_interval_minutes)

    # Input is an optional callback function. This function should take a bool
    # input, if true: update ready, if false: no update ready.
    addon_updater.check_for_update_async(background_update_callback)
    ran_background_check = True


def check_for_update_nonthreaded(self, context):
    """Can be placed in front of other operators to launch when pressed"""
    if addon_updater.invalid_updater:
        return

    # Only check if it's ready, ie after the time interval specified should
    # be the async wrapper call here.
    settings = get_addon_preferences(bpy.context)
    if not settings:
        if addon_updater.verbose:
            print("Could not get {} preferences, update check skipped".format(
                __package__))
        return
    addon_updater.set_check_interval(enabled=settings.auto_check_update,
                                     months=settings.updater_interval_months,
                                     days=settings.updater_interval_days,
                                     hours=settings.updater_interval_hours,
                                     minutes=settings.updater_interval_minutes)

    (update_ready, version, link) = addon_updater.check_for_update(now=False)
    if update_ready:
        atr = AddonUpdaterInstallPopup.bl_idname.split(".")
        getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')
    else:
        addon_updater.print_verbose("No update ready")
        self.report({'INFO'}, "No update ready")


# -----------------------------------------------------------------------------
# Example UI integrations
# -----------------------------------------------------------------------------
def update_notice_box_ui(self, context):
    """Update notice draw, to add to the end or beginning of a panel.

    After a check for update has occurred, this function will draw a box
    saying an update is ready, and give a button for: update now, open website,
    or ignore popup. Ideal to be placed at the end / beginning of a panel.
    """

    if addon_updater.invalid_updater:
        return

    saved_state = addon_updater.json
    if not addon_updater.auto_reload_post_update:
        if "just_updated" in saved_state and saved_state["just_updated"]:
            layout = self.layout
            box = layout.box()
            col = box.column()
            alert_row = col.row()
            alert_row.alert = True
            alert_row.operator(
                "wm.quit_blender",
                text="Restart blender",
                icon="ERROR")
            col.label(text="to complete update")
            return

    # If user pressed ignore, don't draw the box.
    if "ignore" in addon_updater.json and addon_updater.json["ignore"]:
        return
    if not addon_updater.update_ready:
        return

    layout = self.layout
    box = layout.box()
    col = box.column(align=True)
    col.alert = True
    col.label(text="Update ready!", icon="ERROR")
    col.alert = False
    col.separator()
    row = col.row(align=True)
    split = row.split(align=True)
    colL = split.column(align=True)
    colL.scale_y = 1.5
    colL.operator(AddonUpdaterIgnore.bl_idname, icon="X", text="Ignore")
    colR = split.column(align=True)
    colR.scale_y = 1.5
    if not addon_updater.manual_only:
        colR.operator(AddonUpdaterUpdateNow.bl_idname,
                      text="Update", icon="LOOP_FORWARDS")
        col.operator("wm.url_open", text="Open website").url = addon_updater.website
        # ops = col.operator("wm.url_open",text="Direct download")
        # ops.url=updater.update_link
        col.operator(AddonUpdaterInstallManually.bl_idname,
                     text="Install manually")
    else:
        # ops = col.operator("wm.url_open", text="Direct download")
        # ops.url=updater.update_link
        col.operator("wm.url_open", text="Get it now").url = addon_updater.website


def update_settings_ui_condensed(self, context, element=None):
    """Preferences - Condensed drawing within preferences.

    Alternate draw for user preferences or other places, does not draw a box.
    """

    # Element is a UI element, such as layout, a row, column, or box.
    if element is None:
        element = self.layout
    row = element.row()

    # In case of error importing updater.
    if addon_updater.invalid_updater:
        row.label(text="Error initializing updater code:")
        row.label(text=addon_updater.error_msg)
        return
    settings = get_addon_preferences(context)
    if not settings:
        row.label(text="Error getting updater preferences", icon='ERROR')
        return

    # Special case to tell user to restart blender, if set that way.
    if not addon_updater.auto_reload_post_update:
        saved_state = addon_updater.json
        if "just_updated" in saved_state and saved_state["just_updated"]:
            row.alert = True  # mark red
            row.operator(
                "wm.quit_blender",
                text="Restart blender to complete update",
                icon="ERROR")
            return

    col = row.column()
    if addon_updater.error is not None:
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.scale_y = 2
        if "ssl" in addon_updater.error_msg.lower():
            split.enabled = True
            split.operator(AddonUpdaterInstallManually.bl_idname,
                           text=addon_updater.error)
        else:
            split.enabled = False
            split.operator(AddonUpdaterCheckNow.bl_idname,
                           text=addon_updater.error)
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="", icon="FILE_REFRESH")

    elif addon_updater.update_ready is None and not addon_updater.async_checking:
        col.scale_y = 2
        col.operator(AddonUpdaterCheckNow.bl_idname)
    elif addon_updater.update_ready is None:  # Async is running.
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.enabled = False
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname, text="Checking...")
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterEndBackground.bl_idname, text="", icon="X")

    elif addon_updater.include_branches and \
            len(addon_updater.tags) == len(addon_updater.include_branch_list) and not \
            addon_updater.manual_only:
        # No releases found, but still show the appropriate branch.
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.scale_y = 2
        now_txt = "Update directly to " + str(addon_updater.include_branch_list[0])
        split.operator(AddonUpdaterUpdateNow.bl_idname, text=now_txt)
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="", icon="FILE_REFRESH")

    elif addon_updater.update_ready and not addon_updater.manual_only:
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterUpdateNow.bl_idname,
                       text="Update now to " + str(addon_updater.update_version))
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="", icon="FILE_REFRESH")

    elif addon_updater.update_ready and addon_updater.manual_only:
        col.scale_y = 2
        dl_txt = "Download " + str(addon_updater.update_version)
        col.operator("wm.url_open", text=dl_txt).url = addon_updater.website
    else:  # i.e. that updater.update_ready == False.
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.enabled = False
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="Addon is up to date")
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="", icon="FILE_REFRESH")

    row = element.row()
    row.prop(settings, "auto_check_update")

    row = element.row()
    row.scale_y = 0.7
    last_check = addon_updater.json["last_check"]
    if addon_updater.error is not None and addon_updater.error_msg is not None:
        row.label(text=addon_updater.error_msg)
    elif last_check != "" and last_check is not None:
        last_check = last_check[0: last_check.index(".")]
        row.label(text="Last check: " + last_check)
    else:
        row.label(text="Last check: Never")


def skip_tag_function(self, tag):
    """A global function for tag skipping.

    A way to filter which tags are displayed, e.g. to limit downgrading too
    long ago.

    Args:
        self: The instance of the singleton addon update.
        tag: the text content of a tag from the repo, e.g. "v1.2.3".

    Returns:
        bool: True to skip this tag name (ie don't allow for downloading this
            version), or False if the tag is allowed.
    """

    # In case of error importing updater.
    if self.invalid_updater:
        return False

    # ---- write any custom code here, return true to disallow version ---- #
    #
    # # Filter out e.g. if 'beta' is in name of release
    # if 'beta' in tag.lower():
    # 	return True
    # ---- write any custom code above, return true to disallow version --- #

    if self.include_branches:
        for branch in self.include_branch_list:
            if tag["name"].lower() == branch:
                return False

    # Function converting string to tuple, ignoring e.g. leading 'v'.
    # Be aware that this strips out other text that you might otherwise
    # want to be kept and accounted for when checking tags (e.g. v1.1a vs 1.1b)
    tupled = self.version_tuple_from_text(tag["name"])
    if not isinstance(tupled, tuple):
        return True

    # Select the min tag version - change tuple accordingly.
    if self.version_min_update is not None:
        if tupled < self.version_min_update:
            return True  # Skip if current version below this.

    # Select the max tag version.
    if self.version_max_update is not None:
        if tupled >= self.version_max_update:
            return True  # Skip if current version at or above this.

    # In all other cases, allow showing the tag for updating/reverting.
    # To simply and always show all tags, this return False could be moved
    # to the start of the function definition so all tags are allowed.
    return False


def select_link_function(self, tag):
    """Only customize if trying to leverage "attachments" in *GitHub* releases.

    A way to select from one or multiple attached downloadable files from the
    server, instead of downloading the default release/tag source code.
    """

    # -- Default, universal case (and is the only option for GitLab/Bitbucket)
    link = tag["zipball_url"]

    # -- Example: select the first (or only) asset instead source code --
    # if "assets" in tag and "browser_download_url" in tag["assets"][0]:
    # 	link = tag["assets"][0]["browser_download_url"]

    # -- Example: select asset based on OS, where multiple builds exist --
    # # not tested/no error checking, modify to fit your own needs!
    # # assume each release has three attached builds:
    # #		release_windows.zip, release_OSX.zip, release_linux.zip
    # # This also would logically not be used with "branches" enabled
    # if platform.system() == "Darwin": # ie OSX
    # 	link = [asset for asset in tag["assets"] if 'OSX' in asset][0]
    # elif platform.system() == "Windows":
    # 	link = [asset for asset in tag["assets"] if 'windows' in asset][0]
    # elif platform.system() == "Linux":
    # 	link = [asset for asset in tag["assets"] if 'linux' in asset][0]

    return link


# -----------------------------------------------------------------------------
# Register, should be run in the register module itself
# -----------------------------------------------------------------------------


class AddonUpdaterInstallPopup(bpy.types.Operator):
    """Check and install update if available"""
    bl_label = f"Update {addon_name} addon"
    bl_idname = f"{addon_name}.updater_install_popup"
    bl_description = "Popup to check and display current updates available"
    bl_options = {'REGISTER', 'INTERNAL'}

    # if true, run clean install - ie remove all files before adding new
    # equivalent to deleting the addon and reinstalling, except the
    # updater folder/backup folder remains
    clean_install = bpy.props.BoolProperty(
        name="Clean install",
        description=("If enabled, completely clear the addon's folder before "
                     "installing new update, creating a fresh install"),
        default=False,
        options={'HIDDEN'}
    )

    ignore_enum = bpy.props.EnumProperty(
        name="Process update",
        description="Decide to install, ignore, or defer new addon update",
        items=[
            ("install", "Update Now", "Install update now"),
            ("ignore", "Ignore", "Ignore this update to prevent future popups"),
            ("defer", "Defer", "Defer choice till next blender session")
        ],
        options={'HIDDEN'}
    )

    def check(self, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if addon_updater.invalid_updater:
            layout.label(text="Updater module error")
            return
        elif addon_updater.update_ready:
            col = layout.column()
            col.scale_y = 0.7
            col.label(text="Update {} ready!".format(addon_updater.update_version),
                      icon="LOOP_FORWARDS")
            col.label(text="Choose 'Update Now' & press OK to install, ",
                      icon="BLANK1")
            col.label(text="or click outside window to defer", icon="BLANK1")
            row = col.row()
            row.prop(self, "ignore_enum", expand=True)
            col.split()
        elif not addon_updater.update_ready:
            col = layout.column()
            col.scale_y = 0.7
            col.label(text="No updates available")
            col.label(text="Press okay to dismiss dialog")
            # add option to force install
        else:
            # Case: updater.update_ready = None
            # we have not yet checked for the update.
            layout.label(text="Check for update now?")

        # Potentially in future, UI to 'check to select/revert to old version'.

    def execute(self, context):
        # In case of error importing updater.
        if addon_updater.invalid_updater:
            return {'CANCELLED'}

        if addon_updater.manual_only:
            bpy.ops.wm.url_open(url=addon_updater.website)
        elif addon_updater.update_ready:

            # Action based on enum selection.
            if self.ignore_enum == 'defer':
                return {'FINISHED'}
            elif self.ignore_enum == 'ignore':
                addon_updater.ignore_update()
                return {'FINISHED'}

            res = addon_updater.run_update(force=False,
                                           callback=post_update_callback,
                                           clean=self.clean_install)

            # Should return 0, if not something happened.
            if addon_updater.verbose:
                if res == 0:
                    print("Updater returned successful")
                else:
                    print("Updater returned {}, error occurred".format(res))
        elif addon_updater.update_ready is None:
            _ = addon_updater.check_for_update(now=True)

            # Re-launch this dialog.
            atr = AddonUpdaterInstallPopup.bl_idname.split(".")
            getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')
        else:
            addon_updater.print_verbose("Doing nothing, not ready for update")
        return {'FINISHED'}


# class SingletonUpdaterNone(object):
#     """Fake, bare minimum fields and functions for the updater object."""

#     def __init__(self):
#         self.invalid_updater = True  # Used to distinguish bad install.

#         self.addon = None
#         self.verbose = False
#         self.use_print_traces = True
#         self.error = None
#         self.error_msg = None
#         self.async_checking = None

#     def clear_state(self):
#         self.addon = None
#         self.verbose = False
#         self.invalid_updater = True
#         self.error = None
#         self.error_msg = None
#         self.async_checking = None

#     def run_update(self, force, callback, clean):
#         pass

#     def check_for_update(self, now):
#         pass

# updater = SingletonUpdaterNone()
# updater.error = "Error initializing updater module"
# updater.error_msg = str(e)

# Must declare this before classes are loaded, otherwise the bl_idname's will
# not match and have errors. Must be all lowercase and no spaces! Should also
# be unique among any other addons that could exist (using this updater code),
# to avoid clashes in operator registration.
# updater.addon = ""


# -----------------------------------------------------------------------------
# Updater operators
# -----------------------------------------------------------------------------


# Simple popup to prompt use to check for update & offer install if available.


# User preference check-now operator


def update_settings_ui(self, context, element=None):
    """Preferences - for drawing with full width inside user preferences

    A function that can be run inside user preferences panel for prefs UI.
    Place inside UI draw using:
        addon_updater_ops.update_settings_ui(self, context)
    or by:
        addon_updater_ops.update_settings_ui(context)
    """

    # Element is a UI element, such as layout, a row, column, or box.
    if element is None:
        element = self.layout
    box = element.box()

    # In case of error importing updater.
    if addon_updater.invalid_updater:
        box.label(text="Error initializing updater code:")
        box.label(text=addon_updater.error_msg)
        return
    settings = get_addon_preferences(context, addon_name)
    if not settings:
        box.label(text="Error getting updater preferences", icon='ERROR')
        return

    # auto-update settings
    box.label(text="Updater Settings")
    row = box.row()

    # special case to tell user to restart blender, if set that way
    if not addon_updater.auto_reload_post_update:
        saved_state = addon_updater.json
        if "just_updated" in saved_state and saved_state["just_updated"]:
            row.alert = True
            row.operator("wm.quit_blender",
                         text="Restart blender to complete update",
                         icon="ERROR")
            return

    split = row.split(factor=0.4)
    sub_col = split.column()
    sub_col.prop(settings, "auto_check_update")
    sub_col = split.column()

    if not settings.auto_check_update:
        sub_col.enabled = False
    sub_row = sub_col.row()
    sub_row.label(text="Interval between checks")
    sub_row = sub_col.row(align=True)
    check_col = sub_row.column(align=True)
    check_col.prop(settings, "updater_interval_months")
    check_col = sub_row.column(align=True)
    check_col.prop(settings, "updater_interval_days")
    check_col = sub_row.column(align=True)

    # Consider un-commenting for local dev (e.g. to set shorter intervals)
    # check_col.prop(settings,"updater_interval_hours")
    # check_col = sub_row.column(align=True)
    # check_col.prop(settings,"updater_interval_minutes")

    # Checking / managing updates.
    row = box.row()
    col = row.column()
    if addon_updater.error is not None:
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.scale_y = 2
        if "ssl" in addon_updater.error_msg.lower():
            split.enabled = True
            split.operator(AddonUpdaterInstallManually.bl_idname,
                           text=addon_updater.error)
        else:
            split.enabled = False
            split.operator(AddonUpdaterCheckNow.bl_idname,
                           text=addon_updater.error)
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="", icon="FILE_REFRESH")

    elif addon_updater.update_ready is None and not addon_updater.async_checking:
        col.scale_y = 2
        col.operator(AddonUpdaterCheckNow.bl_idname)
    elif addon_updater.update_ready is None:  # async is running
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.enabled = False
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname, text="Checking...")
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterEndBackground.bl_idname, text="", icon="X")

    elif addon_updater.include_branches and \
            len(addon_updater.tags) == len(addon_updater.include_branch_list) and not \
            addon_updater.manual_only:
        # No releases found, but still show the appropriate branch.
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.scale_y = 2
        update_now_txt = "Update directly to {}".format(
            addon_updater.include_branch_list[0])
        split.operator(AddonUpdaterUpdateNow.bl_idname, text=update_now_txt)
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="", icon="FILE_REFRESH")

    elif addon_updater.update_ready and not addon_updater.manual_only:
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterUpdateNow.bl_idname,
                       text="Update now to " + str(addon_updater.update_version))
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="", icon="FILE_REFRESH")

    elif addon_updater.update_ready and addon_updater.manual_only:
        col.scale_y = 2
        dl_now_txt = "Download " + str(addon_updater.update_version)
        col.operator("wm.url_open",
                     text=dl_now_txt).url = addon_updater.website
    else:  # i.e. that updater.update_ready == False.
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.enabled = False
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="Addon is up to date")
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="", icon="FILE_REFRESH")

    if not addon_updater.manual_only:
        col = row.column(align=True)
        if addon_updater.include_branches and len(addon_updater.include_branch_list) > 0:
            branch = addon_updater.include_branch_list[0]
            col.operator(AddonUpdaterUpdateTarget.bl_idname,
                         text="Install {} / old version".format(branch))
        else:
            col.operator(AddonUpdaterUpdateTarget.bl_idname,
                         text="(Re)install addon version")
        last_date = "none found"
        backup_path = os.path.join(addon_updater.stage_path, "backup")
        if "backup_date" in addon_updater.json and os.path.isdir(backup_path):
            if addon_updater.json["backup_date"] == "":
                last_date = "Date not found"
            else:
                last_date = addon_updater.json["backup_date"]
        backup_text = "Restore addon backup ({})".format(last_date)
        col.operator(AddonUpdaterRestoreBackup.bl_idname, text=backup_text)

    row = box.row()
    row.scale_y = 0.7
    last_check = addon_updater.json["last_check"]
    if addon_updater.error is not None and addon_updater.error_msg is not None:
        row.label(text=addon_updater.error_msg)
    elif last_check:
        last_check = last_check[0: last_check.index(".")]
        row.label(text="Last update check: " + last_check)
    else:
        row.label(text="Last update check: Never")


class AddonUpdaterUpdateNow(bpy.types.Operator):
    bl_label = f"Update {addon_name} addon now"
    bl_idname = f"{addon_name}.updater_update_now"
    bl_description = f"Update to the latest version of the {addon_name} addon"
    bl_options = {'REGISTER', 'INTERNAL'}

    # If true, run clean install - ie remove all files before adding new
    # equivalent to deleting the addon and reinstalling, except the updater
    # folder/backup folder remains.
    clean_install = bpy.props.BoolProperty(
        name="Clean install",
        description=("If enabled, completely clear the addon's folder before "
                     "installing new update, creating a fresh install"),
        default=False,
        options={'HIDDEN'}
    )

    def execute(self, context):

        # in case of error importing updater
        if addon_updater.invalid_updater:
            return {'CANCELLED'}

        if addon_updater.manual_only:
            bpy.ops.wm.url_open(url=addon_updater.website)
        if addon_updater.update_ready:
            # if it fails, offer to open the website instead
            try:
                res = addon_updater.run_update(force=False,
                                               callback=post_update_callback,
                                               clean=self.clean_install)

                # Should return 0, if not something happened.
                if addon_updater.verbose:
                    if res == 0:
                        print("Updater returned successful")
                    else:
                        print("Updater error response: {}".format(res))
            except Exception as expt:
                addon_updater._error = "Error trying to run update"
                addon_updater._error_msg = str(expt)
                addon_updater.print_trace()
                atr = AddonUpdaterInstallManually.bl_idname.split(".")
                getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')
        elif addon_updater.update_ready is None:
            (update_ready, version, link) = addon_updater.check_for_update(now=True)
            # Re-launch this dialog.
            atr = AddonUpdaterInstallPopup.bl_idname.split(".")
            getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')

        elif not addon_updater.update_ready:
            self.report({'INFO'}, "Nothing to update")
            return {'CANCELLED'}
        else:
            self.report(
                {'ERROR'}, "Encountered a problem while trying to update")
            return {'CANCELLED'}

        return {'FINISHED'}


class __Addon_Updater_System:
    """Addon updater service class.

    This is the singleton class to instance once and then reference where
    needed throughout the addon. It implements all the interfaces for running
    updates.
    """

    def __init__(self):

        self._engine = GithubEngine()
        self._user = None
        self._repo = None
        self._website = None
        self._current_version = None
        self._subfolder_path = None
        self._tags = list()
        self._tag_latest = None
        self._tag_names = list()
        self._latest_release = None
        self._use_releases = False
        self._include_branches = False
        self._include_branch_list = ['master']
        self._include_branch_auto_check = False
        self._manual_only = False
        self._version_min_update = None
        self._version_max_update = None

        # By default, backup current addon on update/target install.
        self._backup_current = True
        self._backup_ignore_patterns = None

        # Set patterns the files to overwrite during an update.
        self._overwrite_patterns = ["*.py", "*.pyc"]
        self._remove_pre_update_patterns = list()

        # By default, don't auto disable+re-enable the addon after an update,
        # as this is less stable/often won't fully reload all modules anyways.
        self._auto_reload_post_update = False

        # Settings for the frequency of automated background checks.
        self._check_interval_enabled = False
        self._check_interval_months = 0
        self._check_interval_days = 7
        self._check_interval_hours = 0
        self._check_interval_minutes = 0

        # runtime variables, initial conditions
        self._verbose = False
        self._use_print_traces = True
        self._fake_install = False
        self._async_checking = False  # only true when async daemon started
        self._update_ready = None
        self._update_link = None
        self._update_version = None
        self._source_zip = None
        self._check_thread = None
        self._select_link = None
        self.skip_tag = None

        # Get data from the running blender module (addon).
        self._addon = __package__.lower()
        self._addon_package = __package__  # Must not change.
        self._updater_path = os.path.join(
            os.path.dirname(__file__), self._addon + "_updater")
        self._addon_root = os.path.dirname(__file__)
        self._json = dict()
        self._error = None
        self._error_msg = None
        self._prefiltered_tag_count = 0

        # UI properties, not used within this module but still useful to have.

        # to verify a valid import, in place of placeholder import
        self.show_popups = True  # UI uses to show popups or not.
        self.invalid_updater = False

        # pre-assign basic select-link function
        def select_link_function(self, tag):
            return tag["zipball_url"]

        self._select_link = select_link_function

    def print_trace(self):
        """Print handled exception details when use_print_traces is set"""
        if self._use_print_traces:
            traceback.print_exc()

    def print_verbose(self, msg):
        """Print out a verbose logging message if verbose is true."""
        if not self._verbose:
            return
        print("{} addon: ".format(self.addon) + msg)

    # -------------------------------------------------------------------------
    # Getters and setters
    # -------------------------------------------------------------------------
    @property
    def addon(self):
        return self._addon

    @addon.setter
    def addon(self, value):
        self._addon = str(value)

    @property
    def api_url(self):
        return self._engine.api_url

    @api_url.setter
    def api_url(self, value):
        if not self.check_is_url(value):
            raise ValueError("Not a valid URL: " + value)
        self._engine.api_url = value

    @property
    def async_checking(self):
        return self._async_checking

    @property
    def auto_reload_post_update(self):
        return self._auto_reload_post_update

    @auto_reload_post_update.setter
    def auto_reload_post_update(self, value):
        try:
            self._auto_reload_post_update = bool(value)
        except:
            raise ValueError("auto_reload_post_update must be a boolean value")

    @property
    def backup_current(self):
        return self._backup_current

    @backup_current.setter
    def backup_current(self, value):
        if value is None:
            self._backup_current = False
        else:
            self._backup_current = value

    @property
    def backup_ignore_patterns(self):
        return self._backup_ignore_patterns

    @backup_ignore_patterns.setter
    def backup_ignore_patterns(self, value):
        if value is None:
            self._backup_ignore_patterns = None
        elif not isinstance(value, list):
            raise ValueError("Backup pattern must be in list format")
        else:
            self._backup_ignore_patterns = value

    @property
    def check_interval(self):
        return (self._check_interval_enabled,
                self._check_interval_months,
                self._check_interval_days,
                self._check_interval_hours,
                self._check_interval_minutes)

    @property
    def current_version(self):
        return self._current_version

    @current_version.setter
    def current_version(self, tuple_values):
        if tuple_values is None:
            self._current_version = None
            return
        elif type(tuple_values) is not tuple:
            try:
                tuple(tuple_values)
            except:
                raise ValueError(
                    "current_version must be a tuple of integers")
        for i in tuple_values:
            if type(i) is not int:
                raise ValueError(
                    "current_version must be a tuple of integers")
        self._current_version = tuple(tuple_values)

    @property
    def engine(self):
        return self._engine.name

    @engine.setter
    def engine(self, value):
        engine = value.lower()
        if engine == "github":
            self._engine = GithubEngine()
        elif engine == "gitlab":
            self._engine = GitlabEngine()
        elif engine == "bitbucket":
            self._engine = BitbucketEngine()
        else:
            raise ValueError("Invalid engine selection")

    @property
    def error(self):
        return self._error

    @property
    def error_msg(self):
        return self._error_msg

    @property
    def fake_install(self):
        return self._fake_install

    @fake_install.setter
    def fake_install(self, value):
        if not isinstance(value, bool):
            raise ValueError("fake_install must be a boolean value")
        self._fake_install = bool(value)

    # not currently used
    @property
    def include_branch_auto_check(self):
        return self._include_branch_auto_check

    @include_branch_auto_check.setter
    def include_branch_auto_check(self, value):
        try:
            self._include_branch_auto_check = bool(value)
        except:
            raise ValueError("include_branch_autocheck must be a boolean")

    @property
    def include_branch_list(self):
        return self._include_branch_list

    @include_branch_list.setter
    def include_branch_list(self, value):
        try:
            if value is None:
                self._include_branch_list = ['master']
            elif not isinstance(value, list) or len(value) == 0:
                raise ValueError(
                    "include_branch_list should be a list of valid branches")
            else:
                self._include_branch_list = value
        except:
            raise ValueError(
                "include_branch_list should be a list of valid branches")

    @property
    def include_branches(self):
        return self._include_branches

    @include_branches.setter
    def include_branches(self, value):
        try:
            self._include_branches = bool(value)
        except:
            raise ValueError("include_branches must be a boolean value")

    @property
    def json(self):
        if len(self._json) == 0:
            self.set_updater_json()
        return self._json

    @property
    def latest_release(self):
        if self._latest_release is None:
            return None
        return self._latest_release

    @property
    def manual_only(self):
        return self._manual_only

    @manual_only.setter
    def manual_only(self, value):
        try:
            self._manual_only = bool(value)
        except:
            raise ValueError("manual_only must be a boolean value")

    @property
    def overwrite_patterns(self):
        return self._overwrite_patterns

    @overwrite_patterns.setter
    def overwrite_patterns(self, value):
        if value is None:
            self._overwrite_patterns = ["*.py", "*.pyc"]
        elif not isinstance(value, list):
            raise ValueError("overwrite_patterns needs to be in a list format")
        else:
            self._overwrite_patterns = value

    @property
    def private_token(self):
        return self._engine.token

    @private_token.setter
    def private_token(self, value):
        if value is None:
            self._engine.token = None
        else:
            self._engine.token = str(value)

    @property
    def remove_pre_update_patterns(self):
        return self._remove_pre_update_patterns

    @remove_pre_update_patterns.setter
    def remove_pre_update_patterns(self, value):
        if value is None:
            self._remove_pre_update_patterns = list()
        elif not isinstance(value, list):
            raise ValueError(
                "remove_pre_update_patterns needs to be in a list format")
        else:
            self._remove_pre_update_patterns = value

    @property
    def repo(self):
        return self._repo

    @repo.setter
    def repo(self, value):
        try:
            self._repo = str(value)
        except:
            raise ValueError("repo must be a string value")

    @property
    def select_link(self):
        return self._select_link

    @select_link.setter
    def select_link(self, value):
        # ensure it is a function assignment, with signature:
        # input self, tag; returns link name
        if not hasattr(value, "__call__"):
            raise ValueError("select_link must be a function")
        self._select_link = value

    @property
    def stage_path(self):
        return self._updater_path

    @stage_path.setter
    def stage_path(self, value):
        if value is None:
            self.print_verbose("Aborting assigning stage_path, it's null")
            return
        elif value is not None and not os.path.exists(value):
            try:
                os.makedirs(value)
            except:
                self.print_verbose("Error trying to staging path")
                self.print_trace()
                return
        self._updater_path = value

    @property
    def subfolder_path(self):
        return self._subfolder_path

    @subfolder_path.setter
    def subfolder_path(self, value):
        self._subfolder_path = value

    @property
    def tags(self):
        if len(self._tags) == 0:
            return list()
        tag_names = list()
        for tag in self._tags:
            tag_names.append(tag["name"])
        return tag_names

    @property
    def tag_latest(self):
        if self._tag_latest is None:
            return None
        return self._tag_latest["name"]

    @property
    def update_link(self):
        return self._update_link

    @property
    def update_ready(self):
        return self._update_ready

    @property
    def update_version(self):
        return self._update_version

    @property
    def use_releases(self):
        return self._use_releases

    @use_releases.setter
    def use_releases(self, value):
        try:
            self._use_releases = bool(value)
        except:
            raise ValueError("use_releases must be a boolean value")

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        try:
            self._user = str(value)
        except:
            raise ValueError("User must be a string value")

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        try:
            self._verbose = bool(value)
            self.print_verbose("Verbose is enabled")
        except:
            raise ValueError("Verbose must be a boolean value")

    @property
    def use_print_traces(self):
        return self._use_print_traces

    @use_print_traces.setter
    def use_print_traces(self, value):
        try:
            self._use_print_traces = bool(value)
        except:
            raise ValueError("use_print_traces must be a boolean value")

    @property
    def version_max_update(self):
        return self._version_max_update

    @version_max_update.setter
    def version_max_update(self, value):
        if value is None:
            self._version_max_update = None
            return
        if not isinstance(value, tuple):
            raise ValueError("Version maximum must be a tuple")
        for subvalue in value:
            if type(subvalue) is not int:
                raise ValueError("Version elements must be integers")
        self._version_max_update = value

    @property
    def version_min_update(self):
        return self._version_min_update

    @version_min_update.setter
    def version_min_update(self, value):
        if value is None:
            self._version_min_update = None
            return
        if not isinstance(value, tuple):
            raise ValueError("Version minimum must be a tuple")
        for subvalue in value:
            if type(subvalue) != int:
                raise ValueError("Version elements must be integers")
        self._version_min_update = value

    @property
    def website(self):
        return self._website

    @website.setter
    def website(self, value):
        if not self.check_is_url(value):
            raise ValueError("Not a valid URL: " + value)
        self._website = value

    # -------------------------------------------------------------------------
    # Parameter validation related functions
    # -------------------------------------------------------------------------
    @staticmethod
    def check_is_url(url):
        if not ("http://" in url or "https://" in url):
            return False
        if "." not in url:
            return False
        return True

    def _get_tag_names(self):
        tag_names = list()
        self.get_tags()
        for tag in self._tags:
            tag_names.append(tag["name"])
        return tag_names

    def set_check_interval(self, enabled=False,
                           months=0, days=14, hours=0, minutes=0):
        """Set the time interval between automated checks, and if enabled.

        Has enabled = False as default to not check against frequency,
        if enabled, default is 2 weeks.
        """

        if type(enabled) is not bool:
            raise ValueError("Enable must be a boolean value")
        if type(months) is not int:
            raise ValueError("Months must be an integer value")
        if type(days) is not int:
            raise ValueError("Days must be an integer value")
        if type(hours) is not int:
            raise ValueError("Hours must be an integer value")
        if type(minutes) is not int:
            raise ValueError("Minutes must be an integer value")

        if not enabled:
            self._check_interval_enabled = False
        else:
            self._check_interval_enabled = True

        self._check_interval_months = months
        self._check_interval_days = days
        self._check_interval_hours = hours
        self._check_interval_minutes = minutes

    def __repr__(self):
        return "<Module updater from {a}>".format(a=__file__)

    def __str__(self):
        return "Updater, with user: {a}, repository: {b}, url: {c}".format(
            a=self._user, b=self._repo, c=self.form_repo_url())

    # -------------------------------------------------------------------------
    # API-related functions
    # -------------------------------------------------------------------------
    def form_repo_url(self):
        return self._engine.form_repo_url(self)

    def form_tags_url(self):
        return self._engine.form_tags_url(self)

    def form_branch_url(self, branch):
        return self._engine.form_branch_url(branch, self)

    def get_tags(self):
        request = self.form_tags_url()
        self.print_verbose("Getting tags from server")

        # get all tags, internet call
        all_tags = self._engine.parse_tags(self.get_api(request), self)
        if all_tags is not None:
            self._prefiltered_tag_count = len(all_tags)
        else:
            self._prefiltered_tag_count = 0
            all_tags = list()

        # pre-process to skip tags
        if self.skip_tag is not None:
            self._tags = [tg for tg in all_tags if not self.skip_tag(self, tg)]
        else:
            self._tags = all_tags

        # get additional branches too, if needed, and place in front
        # Does NO checking here whether branch is valid
        if self._include_branches:
            temp_branches = self._include_branch_list.copy()
            temp_branches.reverse()
            for branch in temp_branches:
                request = self.form_branch_url(branch)
                include = {
                    "name": branch.title(),
                    "zipball_url": request
                }
                self._tags = [include] + self._tags  # append to front

        if self._tags is None:
            # some error occurred
            self._tag_latest = None
            self._tags = list()

        elif self._prefiltered_tag_count == 0 and not self._include_branches:
            self._tag_latest = None
            if self._error is None:  # if not None, could have had no internet
                self._error = "No releases found"
                self._error_msg = "No releases or tags found in repository"
            self.print_verbose("No releases or tags found in repository")

        elif self._prefiltered_tag_count == 0 and self._include_branches:
            if not self._error:
                self._tag_latest = self._tags[0]
            branch = self._include_branch_list[0]
            self.print_verbose("{} branch found, no releases: {}".format(
                branch, self._tags[0]))

        elif ((len(self._tags) - len(self._include_branch_list) == 0
                and self._include_branches)
                or (len(self._tags) == 0 and not self._include_branches)
                and self._prefiltered_tag_count > 0):
            self._tag_latest = None
            self._error = "No releases available"
            self._error_msg = "No versions found within compatible version range"
            self.print_verbose(self._error_msg)

        else:
            if not self._include_branches:
                self._tag_latest = self._tags[0]
                self.print_verbose(
                    "Most recent tag found:" + str(self._tags[0]['name']))
            else:
                # Don't return branch if in list.
                n = len(self._include_branch_list)
                self._tag_latest = self._tags[n]  # guaranteed at least len()=n+1
                self.print_verbose(
                    "Most recent tag found:" + str(self._tags[n]['name']))

    def get_raw(self, url):
        """All API calls to base url."""
        request = urllib.request.Request(url)
        try:
            context = ssl._create_unverified_context()
        except:
            # Some blender packaged python versions don't have this, largely
            # useful for local network setups otherwise minimal impact.
            context = None

        # Setup private request headers if appropriate.
        if self._engine.token is not None:
            if self._engine.name == "gitlab":
                request.add_header('PRIVATE-TOKEN', self._engine.token)
            else:
                self.print_verbose("Tokens not setup for engine yet")

        # Always set user agent.
        request.add_header(
            'User-Agent', "Python/" + str(platform.python_version()))

        # Run the request.
        try:
            if context:
                result = urllib.request.urlopen(request, context=context)
            else:
                result = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            if str(e.code) == "403":
                self._error = "HTTP error (access denied)"
                self._error_msg = str(e.code) + " - server error response"
                print(self._error, self._error_msg)
            else:
                self._error = "HTTP error"
                self._error_msg = str(e.code)
                print(self._error, self._error_msg)
            self.print_trace()
            self._update_ready = None
        except urllib.error.URLError as e:
            reason = str(e.reason)
            if "TLSV1_ALERT" in reason or "SSL" in reason.upper():
                self._error = "Connection rejected, download manually"
                self._error_msg = reason
                print(self._error, self._error_msg)
            else:
                self._error = "URL error, check internet connection"
                self._error_msg = reason
                print(self._error, self._error_msg)
            self.print_trace()
            self._update_ready = None
            return None
        else:
            result_string = result.read()
            result.close()
            return result_string.decode()

    def get_api(self, url):
        """Result of all api calls, decoded into json format."""
        get = None
        get = self.get_raw(url)
        if get is not None:
            try:
                return json.JSONDecoder().decode(get)
            except Exception as e:
                self._error = "API response has invalid JSON format"
                self._error_msg = str(e.reason)
                self._update_ready = None
                print(self._error, self._error_msg)
                self.print_trace()
                return None
        else:
            return None

    def stage_repository(self, url):
        """Create a working directory and download the new files"""

        local = os.path.join(self._updater_path, "update_staging")
        error = None

        # Make/clear the staging folder, to ensure the folder is always clean.
        self.print_verbose(
            "Preparing staging folder for download:\n" + str(local))
        if os.path.isdir(local):
            try:
                shutil.rmtree(local)
                os.makedirs(local)
            except:
                error = "failed to remove existing staging directory"
                self.print_trace()
        else:
            try:
                os.makedirs(local)
            except:
                error = "failed to create staging directory"
                self.print_trace()

        if error is not None:
            self.print_verbose("Error: Aborting update, " + error)
            self._error = "Update aborted, staging path error"
            self._error_msg = "Error: {}".format(error)
            return False

        if self._backup_current:
            self.create_backup()

        self.print_verbose("Now retrieving the new source zip")
        self._source_zip = os.path.join(local, "source.zip")
        self.print_verbose("Starting download update zip")
        try:
            request = urllib.request.Request(url)
            context = ssl._create_unverified_context()

            # Setup private token if appropriate.
            if self._engine.token is not None:
                if self._engine.name == "gitlab":
                    request.add_header('PRIVATE-TOKEN', self._engine.token)
                else:
                    self.print_verbose(
                        "Tokens not setup for selected engine yet")

            # Always set user agent
            request.add_header(
                'User-Agent', "Python/" + str(platform.python_version()))

            self.url_retrieve(urllib.request.urlopen(request, context=context),
                              self._source_zip)
            # Add additional checks on file size being non-zero.
            self.print_verbose("Successfully downloaded update zip")
            return True
        except Exception as e:
            self._error = "Error retrieving download, bad link?"
            self._error_msg = "Error: {}".format(e)
            print("Error retrieving download, bad link?")
            print("Error: {}".format(e))
            self.print_trace()
            return False

    def create_backup(self):
        """Save a backup of the current installed addon prior to an update."""
        self.print_verbose("Backing up current addon folder")
        local = os.path.join(self._updater_path, "backup")
        tempdest = os.path.join(
            self._addon_root, os.pardir, self._addon + "_updater_backup_temp")

        self.print_verbose("Backup destination path: " + str(local))

        if os.path.isdir(local):
            try:
                shutil.rmtree(local)
            except:
                self.print_verbose(
                    "Failed to removed previous backup folder, continuing")
                self.print_trace()

        # Remove the temp folder.
        # Shouldn't exist but could if previously interrupted.
        if os.path.isdir(tempdest):
            try:
                shutil.rmtree(tempdest)
            except:
                self.print_verbose(
                    "Failed to remove existing temp folder, continuing")
                self.print_trace()

        # Make a full addon copy, temporarily placed outside the addon folder.
        if self._backup_ignore_patterns is not None:
            try:
                shutil.copytree(self._addon_root, tempdest,
                                ignore=shutil.ignore_patterns(
                                    *self._backup_ignore_patterns))
            except:
                print("Failed to create backup, still attempting update.")
                self.print_trace()
                return
        else:
            try:
                shutil.copytree(self._addon_root, tempdest)
            except:
                print("Failed to create backup, still attempting update.")
                self.print_trace()
                return
        shutil.move(tempdest, local)

        # Save the date for future reference.
        now = datetime.now()
        self._json["backup_date"] = "{m}-{d}-{yr}".format(
            m=now.strftime("%B"), d=now.day, yr=now.year)
        self.save_updater_json()

    def restore_backup(self):
        """Restore the last backed up addon version, user initiated only"""
        self.print_verbose("Restoring backup, backing up current addon folder")
        backuploc = os.path.join(self._updater_path, "backup")
        tempdest = os.path.join(
            self._addon_root, os.pardir, self._addon + "_updater_backup_temp")
        tempdest = os.path.abspath(tempdest)

        # Move instead contents back in place, instead of copy.
        shutil.move(backuploc, tempdest)
        shutil.rmtree(self._addon_root)
        os.rename(tempdest, self._addon_root)

        self._json["backup_date"] = ""
        self._json["just_restored"] = True
        self._json["just_updated"] = True
        self.save_updater_json()

        self.reload_addon()

    def unpack_staged_zip(self, clean=False):
        """Unzip the downloaded file, and validate contents"""
        if not os.path.isfile(self._source_zip):
            self.print_verbose("Error, update zip not found")
            self._error = "Install failed"
            self._error_msg = "Downloaded zip not found"
            return -1

        # Clear the existing source folder in case previous files remain.
        outdir = os.path.join(self._updater_path, "source")
        try:
            shutil.rmtree(outdir)
            self.print_verbose("Source folder cleared")
        except:
            self.print_trace()

        # Create parent directories if needed, would not be relevant unless
        # installing addon into another location or via an addon manager.
        try:
            os.mkdir(outdir)
        except Exception as err:
            print("Error occurred while making extract dir:")
            print(str(err))
            self.print_trace()
            self._error = "Install failed"
            self._error_msg = "Failed to make extract directory"
            return -1

        if not os.path.isdir(outdir):
            print("Failed to create source directory")
            self._error = "Install failed"
            self._error_msg = "Failed to create extract directory"
            return -1

        self.print_verbose(
            "Begin extracting source from zip:" + str(self._source_zip))
        with zipfile.ZipFile(self._source_zip, "r") as zfile:

            if not zfile:
                self._error = "Install failed"
                self._error_msg = "Resulting file is not a zip, cannot extract"
                self.print_verbose(self._error_msg)
                return -1

            # Now extract directly from the first subfolder (not root)
            # this avoids adding the first subfolder to the path length,
            # which can be too long if the download has the SHA in the name.
            zsep = '/'  # Not using os.sep, always the / value even on windows.
            for name in zfile.namelist():
                if zsep not in name:
                    continue
                top_folder = name[:name.index(zsep) + 1]
                if name == top_folder + zsep:
                    continue  # skip top level folder
                sub_path = name[name.index(zsep) + 1:]
                if name.endswith(zsep):
                    try:
                        os.mkdir(os.path.join(outdir, sub_path))
                        self.print_verbose(
                            "Extract - mkdir: " + os.path.join(outdir, sub_path))
                    except OSError as exc:
                        if exc.errno != errno.EEXIST:
                            self._error = "Install failed"
                            self._error_msg = "Could not create folder from zip"
                            self.print_trace()
                            return -1
                else:
                    with open(os.path.join(outdir, sub_path), "wb") as outfile:
                        data = zfile.read(name)
                        outfile.write(data)
                        self.print_verbose(
                            "Extract - create: " + os.path.join(outdir, sub_path))

        self.print_verbose("Extracted source")

        unpath = os.path.join(self._updater_path, "source")
        if not os.path.isdir(unpath):
            self._error = "Install failed"
            self._error_msg = "Extracted path does not exist"
            print("Extracted path does not exist: ", unpath)
            return -1

        if self._subfolder_path:
            self._subfolder_path.replace('/', os.path.sep)
            self._subfolder_path.replace('\\', os.path.sep)

        # Either directly in root of zip/one subfolder, or use specified path.
        if not os.path.isfile(os.path.join(unpath, "__init__.py")):
            dirlist = os.listdir(unpath)
            if len(dirlist) > 0:
                if self._subfolder_path == "" or self._subfolder_path is None:
                    unpath = os.path.join(unpath, dirlist[0])
                else:
                    unpath = os.path.join(unpath, self._subfolder_path)

            # Smarter check for additional sub folders for a single folder
            # containing the __init__.py file.
            if not os.path.isfile(os.path.join(unpath, "__init__.py")):
                print("Not a valid addon found")
                print("Paths:")
                print(dirlist)
                self._error = "Install failed"
                self._error_msg = "No __init__ file found in new source"
                return -1

        # Merge code with the addon directory, using blender default behavior,
        # plus any modifiers indicated by user (e.g. force remove/keep).
        self.deep_merge_directory(self._addon_root, unpath, clean)

        # Now save the json state.
        # Change to True to trigger the handler on other side if allowing
        # reloading within same blender session.
        self._json["just_updated"] = True
        self.save_updater_json()
        self.reload_addon()
        self._update_ready = False
        return 0

    def deep_merge_directory(self, base, merger, clean=False):
        """Merge folder 'merger' into 'base' without deleting existing"""
        if not os.path.exists(base):
            self.print_verbose("Base path does not exist:" + str(base))
            return -1
        elif not os.path.exists(merger):
            self.print_verbose("Merger path does not exist")
            return -1

        # Path to be aware of and not overwrite/remove/etc.
        staging_path = os.path.join(self._updater_path, "update_staging")

        # If clean install is enabled, clear existing files ahead of time
        # note: will not delete the update.json, update folder, staging, or
        # staging but will delete all other folders/files in addon directory.
        error = None
        if clean:
            try:
                # Implement clearing of all folders/files, except the updater
                # folder and updater json.
                # Careful, this deletes entire subdirectories recursively...
                # Make sure that base is not a high level shared folder, but
                # is dedicated just to the addon itself.
                self.print_verbose(
                    "clean=True, clearing addon folder to fresh install state")

                # Remove root files and folders (except update folder).
                files = [f for f in os.listdir(base)
                         if os.path.isfile(os.path.join(base, f))]
                folders = [f for f in os.listdir(base)
                           if os.path.isdir(os.path.join(base, f))]

                for f in files:
                    os.remove(os.path.join(base, f))
                    self.print_verbose(
                        "Clean removing file {}".format(os.path.join(base, f)))
                for f in folders:
                    if os.path.join(base, f) is self._updater_path:
                        continue
                    shutil.rmtree(os.path.join(base, f))
                    self.print_verbose(
                        "Clean removing folder and contents {}".format(
                            os.path.join(base, f)))

            except Exception as err:
                error = "failed to create clean existing addon folder"
                print(error, str(err))
                self.print_trace()

        # Walk through the base addon folder for rules on pre-removing
        # but avoid removing/altering backup and updater file.
        for path, dirs, files in os.walk(base):
            # Prune ie skip updater folder.
            dirs[:] = [d for d in dirs
                       if os.path.join(path, d) not in [self._updater_path]]
            for file in files:
                for pattern in self.remove_pre_update_patterns:
                    if fnmatch.filter([file], pattern):
                        try:
                            fl = os.path.join(path, file)
                            os.remove(fl)
                            self.print_verbose("Pre-removed file " + file)
                        except OSError:
                            print("Failed to pre-remove " + file)
                            self.print_trace()

        # Walk through the temp addon sub folder for replacements
        # this implements the overwrite rules, which apply after
        # the above pre-removal rules. This also performs the
        # actual file copying/replacements.
        for path, dirs, files in os.walk(merger):
            # Verify structure works to prune updater sub folder overwriting.
            dirs[:] = [d for d in dirs
                       if os.path.join(path, d) not in [self._updater_path]]
            rel_path = os.path.relpath(path, merger)
            dest_path = os.path.join(base, rel_path)
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            for file in files:
                # Bring in additional logic around copying/replacing.
                # Blender default: overwrite .py's, don't overwrite the rest.
                dest_file = os.path.join(dest_path, file)
                srcFile = os.path.join(path, file)

                # Decide to replace if file already exists, and copy new over.
                if os.path.isfile(dest_file):
                    # Otherwise, check each file for overwrite pattern match.
                    replaced = False
                    for pattern in self._overwrite_patterns:
                        if fnmatch.filter([file], pattern):
                            replaced = True
                            break
                    if replaced:
                        os.remove(dest_file)
                        os.rename(srcFile, dest_file)
                        self.print_verbose(
                            "Overwrote file " + os.path.basename(dest_file))
                    else:
                        self.print_verbose(
                            "Pattern not matched to {}, not overwritten".format(
                                os.path.basename(dest_file)))
                else:
                    # File did not previously exist, simply move it over.
                    os.rename(srcFile, dest_file)
                    self.print_verbose(
                        "New file " + os.path.basename(dest_file))

        # now remove the temp staging folder and downloaded zip
        try:
            shutil.rmtree(staging_path)
        except:
            error = ("Error: Failed to remove existing staging directory, "
                     "consider manually removing ") + staging_path
            self.print_verbose(error)
            self.print_trace()

    def reload_addon(self):
        # if post_update false, skip this function
        # else, unload/reload addon & trigger popup
        if not self._auto_reload_post_update:
            print("Restart blender to reload addon and complete update")
            return

        self.print_verbose("Reloading addon...")
        addon_utils.modules(refresh=True)
        bpy.utils.refresh_script_paths()

        # not allowed in restricted context, such as register module
        # toggle to refresh
        if "addon_disable" in dir(bpy.ops.wm):  # 2.7
            bpy.ops.wm.addon_disable(module=self._addon_package)
            bpy.ops.wm.addon_refresh()
            bpy.ops.wm.addon_enable(module=self._addon_package)
            print("2.7 reload complete")
        else:  # 2.8
            bpy.ops.preferences.addon_disable(module=self._addon_package)
            bpy.ops.preferences.addon_refresh()
            bpy.ops.preferences.addon_enable(module=self._addon_package)
            print("2.8 reload complete")

    # -------------------------------------------------------------------------
    # Other non-api functions and setups
    # -------------------------------------------------------------------------
    def clear_state(self):
        self._update_ready = None
        self._update_link = None
        self._update_version = None
        self._source_zip = None
        self._error = None
        self._error_msg = None

    def url_retrieve(self, url_file, filepath):
        """Custom urlretrieve implementation"""
        chunk = 1024 * 8
        f = open(filepath, "wb")
        while 1:
            data = url_file.read(chunk)
            if not data:
                # print("done.")
                break
            f.write(data)
            # print("Read %s bytes" % len(data))
        f.close()

    def version_tuple_from_text(self, text):
        """Convert text into a tuple of numbers (int).

        Should go through string and remove all non-integers, and for any
        given break split into a different section.
        """
        if text is None:
            return ()

        segments = list()
        tmp = ''
        for char in str(text):
            if not char.isdigit():
                if len(tmp) > 0:
                    segments.append(int(tmp))
                    tmp = ''
            else:
                tmp += char
        if len(tmp) > 0:
            segments.append(int(tmp))

        if len(segments) == 0:
            self.print_verbose("No version strings found text: " + str(text))
            if not self._include_branches:
                return ()
            else:
                return (text)
        return tuple(segments)

    def check_for_update_async(self, callback=None):
        """Called for running check in a background thread"""
        is_ready = (
            self._json is not None
            and "update_ready" in self._json
            and self._json["version_text"] != dict()
            and self._json["update_ready"])

        if is_ready:
            self._update_ready = True
            self._update_link = self._json["version_text"]["link"]
            self._update_version = str(self._json["version_text"]["version"])
            # Cached update.
            callback(True)
            return

        # do the check
        if not self._check_interval_enabled:
            return
        elif self._async_checking:
            self.print_verbose("Skipping async check, already started")
            # already running the bg thread
        elif self._update_ready is None:
            print("{} updater: Running background check for update".format(
                  self.addon))
            self.start_async_check_update(False, callback)

    def check_for_update_now(self, callback=None):
        self._error = None
        self._error_msg = None
        self.print_verbose(
            "Check update pressed, first getting current status")
        if self._async_checking:
            self.print_verbose("Skipping async check, already started")
            return  # already running the bg thread
        elif self._update_ready is None:
            self.start_async_check_update(True, callback)
        else:
            self._update_ready = None
            self.start_async_check_update(True, callback)

    def check_for_update(self, now=False):
        """Check for update not in a syncrhonous manner.

        This function is not async, will always return in sequential fashion
        but should have a parent which calls it in another thread.
        """
        self.print_verbose("Checking for update function")

        # clear the errors if any
        self._error = None
        self._error_msg = None

        # avoid running again in, just return past result if found
        # but if force now check, then still do it
        if self._update_ready is not None and not now:
            return (self._update_ready,
                    self._update_version,
                    self._update_link)

        if self._current_version is None:
            raise ValueError("current_version not yet defined")

        if self._repo is None:
            raise ValueError("repo not yet defined")

        if self._user is None:
            raise ValueError("username not yet defined")

        self.set_updater_json()  # self._json

        if not now and not self.past_interval_timestamp():
            self.print_verbose(
                "Aborting check for updated, check interval not reached")
            return (False, None, None)

        # check if using tags or releases
        # note that if called the first time, this will pull tags from online
        if self._fake_install:
            self.print_verbose(
                "fake_install = True, setting fake version as ready")
            self._update_ready = True
            self._update_version = "(999,999,999)"
            self._update_link = "http://127.0.0.1"

            return (self._update_ready,
                    self._update_version,
                    self._update_link)

        # Primary internet call, sets self._tags and self._tag_latest.
        self.get_tags()

        self._json["last_check"] = str(datetime.now())
        self.save_updater_json()

        # Can be () or ('master') in addition to branches, and version tag.
        new_version = self.version_tuple_from_text(self.tag_latest)

        if len(self._tags) == 0:
            self._update_ready = False
            self._update_version = None
            self._update_link = None
            return (False, None, None)

        if not self._include_branches:
            link = self.select_link(self, self._tags[0])
        else:
            n = len(self._include_branch_list)
            if len(self._tags) == n:
                # effectively means no tags found on repo
                # so provide the first one as default
                link = self.select_link(self, self._tags[0])
            else:
                link = self.select_link(self, self._tags[n])

        if new_version == ():
            self._update_ready = False
            self._update_version = None
            self._update_link = None
            return (False, None, None)
        elif str(new_version).lower() in self._include_branch_list:
            # Handle situation where master/whichever branch is included
            # however, this code effectively is not triggered now
            # as new_version will only be tag names, not branch names.
            if not self._include_branch_auto_check:
                # Don't offer update as ready, but set the link for the
                # default branch for installing.
                self._update_ready = False
                self._update_version = new_version
                self._update_link = link
                self.save_updater_json()
                return (True, new_version, link)
            else:
                # Bypass releases and look at timestamp of last update from a
                # branch compared to now, see if commit values match or not.
                raise ValueError("include_branch_autocheck: NOT YET DEVELOPED")

        else:
            # Situation where branches not included.
            if new_version > self._current_version:

                self._update_ready = True
                self._update_version = new_version
                self._update_link = link
                self.save_updater_json()
                return (True, new_version, link)

        # If no update, set ready to False from None to show it was checked.
        self._update_ready = False
        self._update_version = None
        self._update_link = None
        return (False, None, None)

    def set_tag(self, name):
        """Assign the tag name and url to update to"""
        tg = None
        for tag in self._tags:
            if name == tag["name"]:
                tg = tag
                break
        if tg:
            new_version = self.version_tuple_from_text(self.tag_latest)
            self._update_version = new_version
            self._update_link = self.select_link(self, tg)
        elif self._include_branches and name in self._include_branch_list:
            # scenario if reverting to a specific branch name instead of tag
            tg = name
            link = self.form_branch_url(tg)
            self._update_version = name  # this will break things
            self._update_link = link
        if not tg:
            raise ValueError("Version tag not found: " + name)

    def run_update(self, force=False, revert_tag=None, clean=False, callback=None):
        """Runs an install, update, or reversion of an addon from online source

        Arguments:
            force: Install assigned link, even if self.update_ready is False
            revert_tag: Version to install, if none uses detected update link
            clean: not used, but in future could use to totally refresh addon
            callback: used to run function on update completion
        """
        self._json["update_ready"] = False
        self._json["ignore"] = False  # clear ignore flag
        self._json["version_text"] = dict()

        if revert_tag is not None:
            self.set_tag(revert_tag)
            self._update_ready = True

        # clear the errors if any
        self._error = None
        self._error_msg = None

        self.print_verbose("Running update")

        if self._fake_install:
            # Change to True, to trigger the reload/"update installed" handler.
            self.print_verbose("fake_install=True")
            self.print_verbose(
                "Just reloading and running any handler triggers")
            self._json["just_updated"] = True
            self.save_updater_json()
            if self._backup_current is True:
                self.create_backup()
            self.reload_addon()
            self._update_ready = False
            res = True  # fake "success" zip download flag

        elif not force:
            if not self._update_ready:
                self.print_verbose("Update stopped, new version not ready")
                if callback:
                    callback(
                        self._addon_package,
                        "Update stopped, new version not ready")
                return "Update stopped, new version not ready"
            elif self._update_link is None:
                # this shouldn't happen if update is ready
                self.print_verbose("Update stopped, update link unavailable")
                if callback:
                    callback(self._addon_package,
                             "Update stopped, update link unavailable")
                return "Update stopped, update link unavailable"

            if revert_tag is None:
                self.print_verbose("Staging update")
            else:
                self.print_verbose("Staging install")

            res = self.stage_repository(self._update_link)
            if not res:
                print("Error in staging repository: " + str(res))
                if callback is not None:
                    callback(self._addon_package, self._error_msg)
                return self._error_msg
            res = self.unpack_staged_zip(clean)
            if res < 0:
                if callback:
                    callback(self._addon_package, self._error_msg)
                return res

        else:
            if self._update_link is None:
                self.print_verbose("Update stopped, could not get link")
                return "Update stopped, could not get link"
            self.print_verbose("Forcing update")

            res = self.stage_repository(self._update_link)
            if not res:
                print("Error in staging repository: " + str(res))
                if callback:
                    callback(self._addon_package, self._error_msg)
                return self._error_msg
            res = self.unpack_staged_zip(clean)
            if res < 0:
                return res
            # would need to compare against other versions held in tags

        # run the front-end's callback if provided
        if callback:
            callback(self._addon_package)

        # return something meaningful, 0 means it worked
        return 0

    def past_interval_timestamp(self):
        if not self._check_interval_enabled:
            return True  # ie this exact feature is disabled

        if "last_check" not in self._json or self._json["last_check"] == "":
            return True

        now = datetime.now()
        last_check = datetime.strptime(
            self._json["last_check"], "%Y-%m-%d %H:%M:%S.%f")
        offset = timedelta(
            days=self._check_interval_days + 30 * self._check_interval_months,
            hours=self._check_interval_hours,
            minutes=self._check_interval_minutes)

        delta = (now - offset) - last_check
        if delta.total_seconds() > 0:
            self.print_verbose("Time to check for updates!")
            return True

        self.print_verbose("Determined it's not yet time to check for updates")
        return False

    def get_json_path(self):
        """Returns the full path to the JSON state file used by this updater.

        Will also rename old file paths to addon-specific path if found.
        """
        json_path = os.path.join(
            self._updater_path,
            "{}_updater_status.json".format(self._addon_package))
        old_json_path = os.path.join(self._updater_path, "updater_status.json")

        # Rename old file if it exists.
        try:
            os.rename(old_json_path, json_path)
        except FileNotFoundError:
            pass
        except Exception as err:
            print("Other OS error occurred while trying to rename old JSON")
            print(err)
            self.print_trace()
        return json_path

    def set_updater_json(self):
        """Load or initialize JSON dictionary data for updater state"""
        if self._updater_path is None:
            raise ValueError("updater_path is not defined")
        elif not os.path.isdir(self._updater_path):
            os.makedirs(self._updater_path)

        jpath = self.get_json_path()
        if os.path.isfile(jpath):
            with open(jpath) as data_file:
                self._json = json.load(data_file)
                self.print_verbose("Read in JSON settings from file")
        else:
            self._json = {
                "last_check": "",
                "backup_date": "",
                "update_ready": False,
                "ignore": False,
                "just_restored": False,
                "just_updated": False,
                "version_text": dict()
            }
            self.save_updater_json()

    def save_updater_json(self):
        """Trigger save of current json structure into file within addon"""
        if self._update_ready:
            if isinstance(self._update_version, tuple):
                self._json["update_ready"] = True
                self._json["version_text"]["link"] = self._update_link
                self._json["version_text"]["version"] = self._update_version
            else:
                self._json["update_ready"] = False
                self._json["version_text"] = dict()
        else:
            self._json["update_ready"] = False
            self._json["version_text"] = dict()

        jpath = self.get_json_path()
        if not os.path.isdir(os.path.dirname(jpath)):
            print("State error: Directory does not exist, cannot save json: ",
                  os.path.basename(jpath))
            return
        try:
            with open(jpath, 'w') as outf:
                data_out = json.dumps(self._json, indent=4)
                outf.write(data_out)
        except:
            print("Failed to open/save data to json: ", jpath)
            self.print_trace()
        self.print_verbose("Wrote out updater JSON settings with content:")
        self.print_verbose(str(self._json))

    def json_reset_postupdate(self):
        self._json["just_updated"] = False
        self._json["update_ready"] = False
        self._json["version_text"] = dict()
        self.save_updater_json()

    def json_reset_restore(self):
        self._json["just_restored"] = False
        self._json["update_ready"] = False
        self._json["version_text"] = dict()
        self.save_updater_json()
        self._update_ready = None  # Reset so you could check update again.

    def ignore_update(self):
        self._json["ignore"] = True
        self.save_updater_json()

    # -------------------------------------------------------------------------
    # ASYNC related methods
    # -------------------------------------------------------------------------
    def start_async_check_update(self, now=False, callback=None):
        """Start a background thread which will check for updates"""
        if self._async_checking:
            return
        self.print_verbose("Starting background checking thread")
        check_thread = threading.Thread(target=self.async_check_update,
                                        args=(now, callback,))
        check_thread.daemon = True
        self._check_thread = check_thread
        check_thread.start()

    def async_check_update(self, now, callback=None):
        """Perform update check, run as target of background thread"""
        self._async_checking = True
        self.print_verbose("Checking for update now in background")

        try:
            self.check_for_update(now=now)
        except Exception as exception:
            print("Checking for update error:")
            print(exception)
            self.print_trace()
            if not self._error:
                self._update_ready = False
                self._update_version = None
                self._update_link = None
                self._error = "Error occurred"
                self._error_msg = "Encountered an error while checking for updates"

        self._async_checking = False
        self._check_thread = None

        if callback:
            self.print_verbose("Finished check update, doing callback")
            callback(self._update_ready)
        self.print_verbose("BG thread: Finished check update, no callback")

    def stop_async_check_update(self):
        """Method to give impression of stopping check for update.

        Currently does nothing but allows user to retry/stop blocking UI from
        hitting a refresh button. This does not actually stop the thread, as it
        will complete after the connection timeout regardless. If the thread
        does complete with a successful response, this will be still displayed
        on next UI refresh (ie no update, or update available).
        """
        if self._check_thread is not None:
            self.print_verbose("Thread will end in normal course.")
            # however, "There is no direct kill method on a thread object."
            # better to let it run its course
            # self._check_thread.stop()
        self._async_checking = False
        self._error = None
        self._error_msg = None


class BitbucketEngine:
    """Integration to Bitbucket API for git-formatted repositories"""

    def __init__(self):
        self.api_url = 'https://api.bitbucket.org'
        self.token = None
        self.name = "bitbucket"

    def form_repo_url(self, updater):
        return "{}/2.0/repositories/{}/{}".format(
            self.api_url, updater.user, updater.repo)

    def form_tags_url(self, updater):
        return self.form_repo_url(updater) + "/refs/tags?sort=-name"

    def form_branch_url(self, branch, updater):
        return self.get_zip_url(branch, updater)

    def get_zip_url(self, name, updater):
        return "https://bitbucket.org/{user}/{repo}/get/{name}.zip".format(
            user=updater.user,
            repo=updater.repo,
            name=name)

    def parse_tags(self, response, updater):
        if response is None:
            return list()
        return [
            {
                "name": tag["name"],
                "zipball_url": self.get_zip_url(tag["name"], updater)
            } for tag in response["values"]]


class GithubEngine:
    """Integration to Github API"""

    def __init__(self):
        self.api_url = 'https://api.github.com'
        self.token = None
        self.name = "github"

    def form_repo_url(self, updater):
        return "{}/repos/{}/{}".format(
            self.api_url, updater.user, updater.repo)

    def form_tags_url(self, updater):
        if updater.use_releases:
            return "{}/releases".format(self.form_repo_url(updater))
        else:
            return "{}/tags".format(self.form_repo_url(updater))

    def form_branch_list_url(self, updater):
        return "{}/branches".format(self.form_repo_url(updater))

    def form_branch_url(self, branch, updater):
        return "{}/zipball/{}".format(self.form_repo_url(updater), branch)

    def parse_tags(self, response, updater):
        if response is None:
            return list()
        return response


class GitlabEngine:
    """Integration to GitLab API"""

    def __init__(self):
        self.api_url = 'https://gitlab.com'
        self.token = None
        self.name = "gitlab"

    def form_repo_url(self, updater):
        return "{}/api/v4/projects/{}".format(self.api_url, updater.repo)

    def form_tags_url(self, updater):
        return "{}/repository/tags".format(self.form_repo_url(updater))

    def form_branch_list_url(self, updater):
        # does not validate branch name.
        return "{}/repository/branches".format(
            self.form_repo_url(updater))

    def form_branch_url(self, branch, updater):
        # Could clash with tag names and if it does, it will download TAG zip
        # instead of branch zip to get direct path, would need.
        return "{}/repository/archive.zip?sha={}".format(
            self.form_repo_url(updater), branch)

    def get_zip_url(self, sha, updater):
        return "{base}/repository/archive.zip?sha={sha}".format(
            base=self.form_repo_url(updater),
            sha=sha)

    # def get_commit_zip(self, id, updater):
    # 	return self.form_repo_url(updater)+"/repository/archive.zip?sha:"+id

    def parse_tags(self, response, updater):
        if response is None:
            return list()
        return [
            {
                "name": tag["name"],
                "zipball_url": self.get_zip_url(tag["commit"]["id"], updater)
            } for tag in response]


ran_auto_check_install_popup = False
ran_update_success_popup = False

ran_background_check = False


def make_annotations(cls):
    """Add annotation attribute to fields to avoid Blender 2.8+ warnings"""
    if not hasattr(bpy.app, "version") or bpy.app.version < (2, 80):
        return cls
    if bpy.app.version < (2, 93, 0):
        bl_props = {k: v for k, v in cls.__dict__.items()
                    if isinstance(v, tuple)}
    else:
        bl_props = {k: v for k, v in cls.__dict__.items()
                    if isinstance(v, bpy.props._PropertyDeferred)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls


classes = (
    AddonUpdaterInstallPopup,
    AddonUpdaterCheckNow,
    AddonUpdaterUpdateNow,
    AddonUpdaterUpdateTarget,
    AddonUpdaterInstallManually,
    AddonUpdaterUpdatedSuccessful,
    AddonUpdaterRestoreBackup,
    AddonUpdaterIgnore,
    AddonUpdaterEndBackground
)

__Addon_Updater_System()


class Alx_Addon_Updater():
    """
    addon : __ package __
    addon_current_version :
    addon_minimum_update_version : tuple(x, x, x)
    addon_maximum_update_version : tuple(x, x, x)

    engine : github / gitlab / bitbucket
    engine_user_name : str "example username"
    engine_repo_name : str "example_repo_name"

    manual_download_website : str "https://github.com/example_username/example_repo/releases"
    """

    __addon_minimum_update_version: Optional[tuple[int, int, int]] = None

    def __init__(self, path=None,
                 bl_info=None,
                 engine="Github", engine_user_name="", engine_repo_name="",
                 manual_download_website=""):

        if (self.__addon_minimum_update_version is None):
            self.__addon_minimum_update_version = bl_info["version"]

        self.init_updater()

    def init_updater(self):
        global addon_updater
        # addon_updater =

        addon_updater_operators.addon_updater = addon_updater

        # self.__internal_updater = __Addon_Updater_System()

        # self.__addon_name = addon_name
        # self.__addon_current_version = bl_info["version"]
        # self.__addon_minimum_update_version = None
        # self.__addon_maximum_update_version = None

        # self.__engine = engine
        # self.__engine_private_token = None
        # self.__engine_user_name = engine_user_name
        # self.__engine_repo_name = engine_repo_name

        # self.__manual_download_website = manual_download_website

        # self.__updater_data_path

        # self.__verbose = False
        # self.__backup_current = True

        # self.__backup_ignore_patterns = ["__pycache__"]
        # # self.backup_ignore_patterns = [".git", "__pycache__", "*.bat", ".gitignore", "*.exe"]

        # # updater.backup_ignore_patterns = [".git", "__pycache__", "*.bat", ".gitignore", "*.exe"]

        # updater.overwrite_patterns = ["*.png", "*.jpg", "README.md", "LICENSE.txt"]
        # updater.remove_pre_update_patterns = ["*.py", "*.pyc"]
        # updater.use_releases = True
        # updater.include_branches = False

    # def init_updater(self):
    #     updater = self.__internal_updater

    #     updater.addon = self.__addon_name
    #     updater.current_version = self.__addon_current_version
    #     updater.version_min_update = self.__addon_minimum_update_version
    #     updater.version_max_update = self.__addon_maximum_update_version

    #     updater.engine = self.__engine
    #     updater.user = self.__engine_user_name
    #     updater.repo = self.__engine_repo_name
    #     updater.private_token = self.__engine_private_token

    #     updater.website = self.__manual_download_website

    #     updater.subfolder_path = ""

    #     updater.verbose = False
    #     updater.show_popups = True
    #     updater.manual_only = False
    #     updater.fake_install = False
    #     updater.backup_current = True
    #     updater.overwrite_patterns = ["*.png", "*.jpg", "README.md", "LICENSE.txt"]
    #     updater.remove_pre_update_patterns = ["*.py", "*.pyc"]
    #     updater.backup_ignore_patterns = [".git", "__pycache__", "*.bat", ".gitignore", "*.exe"]
    #     updater.set_check_interval(enabled=False, months=0, days=1, hours=0, minutes=0)

    #     updater.use_releases = True
    #     updater.include_branches = False
    #     updater.include_branch_list = ['master']

    #     updater.auto_reload_post_update = True

    # def set_version_target(self, minimum_version: Optional[tuple[int, int, int]] = None, maximum_version: Optional[tuple[int, int, int]] = None):
    #     if (minimum_version is not None):
    #         self.__addon_minimum_update_version = minimum_version
    #     if (maximum_version is not None):
    #         self.__addon_maximum_update_version = maximum_version

    # def set_check_interval(self, enabled=False, months=0, days=0, hours=0, minutes=2):
    #     updater = self.__internal_updater
    #     updater.set_check_interval(enabled, months, days, hours, minutes)

    def __register_addon_classes(self, addon_classes: list[object], mute: Optional[bool] = True):
        for addon_class in addon_classes:
            try:
                if (mute):
                    with open(os.devnull, 'w') as print_discard_bin:
                        with redirect_stdout(print_discard_bin):
                            if ("WorkSpaceTool" in [base.__name__ for base in addon_class.__bases__]):
                                bpy.utils.register_tool(addon_class,
                                                        after=eval(addon_class.after, self.__init_globals),
                                                        separator=addon_class.separator,
                                                        group=addon_class.group)
                            else:
                                bpy.utils.register_class(addon_class)
                else:
                    if ("WorkSpaceTool" in [base.__name__ for base in addon_class.__bases__]):
                        bpy.utils.register_tool(addon_class,
                                                after=eval(addon_class.after, self.__init_globals),
                                                separator=addon_class.separator,
                                                group=addon_class.group)
                    else:
                        bpy.utils.register_class(addon_class)

            except Exception as error:
                print(error)

    def unregister(self):
        updater = self.__internal_updater

        for cls in classes:
            try:
                bpy.utils.unregister_class(cls)
            except:
                pass

        updater.clear_state()

        global ran_auto_check_install_popup
        ran_auto_check_install_popup = False

        global ran_update_success_popup
        ran_update_success_popup = False

        global ran_background_check
        ran_background_check = False
