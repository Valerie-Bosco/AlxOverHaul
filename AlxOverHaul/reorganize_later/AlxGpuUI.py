import math
import gpu
from gpu_extras import batch as gpu_batch
from .import Alx_STAL_GPU_utils

import blf


def rectangle(position_x: int, position_y: int, width: int, height: int):
    vertex_set = [(position_x, position_y), (position_x + width, position_y), (position_x + width, position_y + height), (position_x, position_y + height)]
    index_set = [(0, 1, 2), (0, 2, 3)]

    return index_set, vertex_set


def AlxRange(start=0.0, stop=100.0, step=1.0):
    value = start
    iterator = [value]
    while value <= stop:
        if (value + step <= stop):
            value += step
            iterator.append(value)
        else:
            break
    return iterator


def create_poly_fan(center_point: tuple[int, int] = (0, 0), radius_px: int = 10, quadrants: tuple[bool, bool, bool, bool] = (False, False, False, False), quadrant_resolution: int = 1):
    quadrant_displacement = [[1, 1], [-1, 1], [-1, -1], [1, -1]]
    vertex_quadrant_set = []
    vertex_set = [(center_point[0], center_point[1])]
    index_set = []

    step = 90 * (1 / quadrant_resolution)

    quadrant_i = 0
    for quadrant in quadrants:
        local_set = []
        for point in AlxRange(0.0, 91.0, step):
            if (quadrant == True):
                vertex_co = ((center_point[0] + (quadrant_displacement[quadrant_i][0] * radius_px) * math.cos(point * math.pi / 180)), (center_point[1] + (quadrant_displacement[quadrant_i][1] * radius_px) * math.sin(point * math.pi / 180)))
                local_set.append(vertex_co)

        vertex_quadrant_set.append(local_set)
        quadrant_i += 1

    co_i = 0
    for co in range(0, 4):

        if ((co_i + 2) <= (len(vertex_set) - 1)):
            index_set.append((0, co_i + 1, co_i + 2))
        else:
            pass
        co_i += 1
        # if (quadrant_i-1 >=0) and (quadrants[quadrant_i] == True) and (quadrants[quadrant_i-1] == False):
        #     co_i+=1

    return index_set, vertex_set


def draw_unlocked_modeling_ui(position_x, position_y, operator):

    indices, vertices = rectangle(position_x, position_y, 150, 100)
    # create_poly_fan((position_x, position_y), radius_px=50, quadrants=(False, True, False, True), quadrant_resolution=1)

    # gpu.state.blend_set("ALPHA")
    shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    batch = gpu_batch.batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
    # gpu.state.blend_set("ALPHA")
    gpu.state.line_width_set(1)

    shader.bind()
    shader.uniform_float("color", (0.815, 0.305, 0.195, 1.0))
    batch.draw(shader)

    # blf.position(0, position_x + 5, position_y + 45, 0)
    # blf.size(0, 24.0)
    # blf.dimensions()

    OT_running_status_text = f"{'Active' if operator.bIsRunning else 'Right-Click To Start'}"
    OT_bevel_average_text = f"bevel weight: {operator.average_bevel_weight}"
    OT_crease_average_text = f"crease weight: {operator.average_crease_weight}"

    text_order = dict()
    text_order.update({"OT_running_status_text": 32.0})
    text_order.update({"OT_bevel_average_text": 16.0})
    text_order.update({"OT_crease_average_text": 16.0})

    position_dict = Alx_STAL_GPU_utils.Alx_text_columnflow(text_order, padding=10)

    for text in position_dict:
        blf.size(0, position_dict[text][0])
        blf.position(0, position_x + 5, position_y + position_dict[text][1], 0)
        blf.draw(0, eval(list(position_dict.keys())[list(position_dict.keys()).index(text)]))

    gpu.state.line_width_set(1)
    gpu.state.blend_set("NONE")


# def draw_callback_px(self, context):
#     x, y = self.mouse_path[-1]

#     vertices = (
#         (x, y-50), (x+100, y-50),
#         (x, y), (x+100, y))

#     indices = (
#         (0, 1, 2), (2, 1, 3))

#     bgl.glEnable(bgl.GL_BLEND)
#     bgl.glEnable(bgl.GL_LINE_SMOOTH)
#     shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
#     batch = gpu.batch.batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
#     bgl.glEnable(bgl.GL_BLEND)
#     bgl.glLineWidth(1) # Set the line width
#     shader.bind()
#     shader.uniform_float("color", (0.2, 0.7, 0.2, 0.5))
#     batch.draw(shader)

#     font_id = 0  #, need to find out how best to get this.

#     # draw some text
#     font_offset = 10

#     blf.position(font_id, x+font_offset, y-font_offset*2, 0)
#     blf.size(font_id, 20, 72)
#     blf.draw(font_id, "{:.2f}".format(self.bevel_mod.width))

#     # restore opengl defaults
#     bgl.glLineWidth(1)
#     bgl.glDisable(bgl.GL_BLEND)
