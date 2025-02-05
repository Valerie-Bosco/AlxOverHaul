import bpy
import bpy_extras
import blf

def Alx_text_columnflow(text: dict, padding:int):
    """
    text: [(text_string, font_size)]
    """
    position_index = dict()

    remaining_text = text
    complete_text = []

    for text_strip in text.keys():
        complete_text.append(text_strip)

        dimension_set = [blf.dimensions(0, key)[1] for key in remaining_text.keys() if (key not in complete_text)]
        position = sum(dimension_set) + (((len(remaining_text)+1) - len(complete_text)) * padding)

        position_index[text_strip] = [text[text_strip], position]

    return position_index



def Alx_billboard(context: bpy.types.Context, coords_view3d: tuple[tuple[int,int,int]] = [[0,0,0]]):
    override_window = context.window
    override_screen = override_window.screen
    override_area = [area for area in override_screen.areas if area.type == "VIEW_3D"]
    override_region = [region for region in override_area[0].regions if region.type == 'WINDOW']

    coords_view2d = list()

    with context.temp_override(window=override_window, area=override_area[0], region=override_region[0]):
        space_data = context.space_data
        region_view3d = space_data.region_3d if (space_data is not None) and (hasattr(space_data, "region_3d")) else None
        
        for coord_3d in coords_view3d:
            coords = bpy_extras.view3d_utils.location_3d_to_region_2d(region=override_region[0], rv3d=region_view3d, coord=coord_3d, default=(0.0,0.0,0.0)) if (region_view3d is not None) else (0.0,0.0,0.0)
            coords_view2d.append(coords)

    return coords_view2d