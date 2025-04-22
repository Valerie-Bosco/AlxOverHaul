import gpu


class RGBColor:
    r: int = 255
    g: int = 255
    b: int = 255

    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b

    def black(self):
        return RGBColor(0, 0, 0)


class ScreenCoord:
    x: int = 0
    y: int = 0

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def zero_co(self):
        return ScreenCoord(0, 0)


class GPU_Rectangle:
    def __init__(self, co_x: int, co_y: int, width: int, height: int):
        indices = ((0, 1, 2), (0, 2, 3))

        # co_x, co_y
        # co_x, co_y + width
        # co_x +

        # vertices = (
        #     (self.x_screen, y_screen_flip),
        #     (self.x_screen, y_screen_flip - self.height),
        #     (self.x_screen + self.width, y_screen_flip - self.height),
        #     (self.x_screen + self.width, y_screen_flip))
        return


class ALX_GPU_Widget:

    b_is_visible: bool = False

    widget_co: ScreenCoord = ScreenCoord.zero_co()
    color: RGBColor = RGBColor.black()

    def __init__(self, co_x: int, co_y: int, width: int, height: int):
        self.widget_co = ScreenCoord(co_x, co_y)

    def set_color(self, color: RGBColor):
        self.color = color

    def draw(self):
        if (self.b_is_visible):
            gpu.state.blend_set("ALPHA")

        else:
            return
