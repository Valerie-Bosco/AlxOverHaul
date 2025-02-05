from pathlib import Path
import json

import bpy


def json_format_keymaps(keymaps: list[bpy.types.KeyMap]):
    json_data = dict()

    attr_whitelist = {"name",
                      "space_type",
                      "region_type",
                      }

    json_data = {
        keymap.name: dict({attr: getattr(keymap, attr)
                           for attr in dir(keymap)
                           if (attr in attr_whitelist) and
                           (not str.startswith(attr, "__") and not str.endswith(attr, "__")) and
                           (type(getattr(keymap, attr)) in {int, str, bool})
                           },

                          **{keymap_item.name: {attr: getattr(keymap_item, attr)
                                                for attr in dir(keymap_item)
                                                if (not str.startswith(attr, "__") and not str.endswith(attr, "__")) and
                                                (type(getattr(keymap_item, attr)) in {int, str, bool})
                                                }
                             for keymap_item in keymap.keymap_items
                             })


        for keymap in keymaps
    }

    return json_data


def json_serialize_keymaps(target_files: list[Path], keymaps: list[bpy.types.KeyMap]):
    for file in target_files:
        if (file.exists()) and (file.suffix) and (file.is_file()):
            with file.open("w") as json_target_file:
                json.dump(json_format_keymaps(keymaps), json_target_file)
                json_target_file.close()
