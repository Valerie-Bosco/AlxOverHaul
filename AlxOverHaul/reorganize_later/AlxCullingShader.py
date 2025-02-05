# import bpy
# import gpu

# vertex_shader = '''
#     in vec3 position;
#     in vec4 in_color;
#     in vec3 normal;

#     out vec4 color;
#     void main()
#     {
#         color = in_color;
#     }
# '''

# fragment_shader = '''
#     void main()
#     {
#     }
# '''



# culling_shader = gpu.types.GPUShader(vertex_shader, fragment_shader) #type:ignore

# def vertex_culling_handler(context: bpy.types.Context, vcolor: tuple[1.0, 1.0, 1.0, 0.0]):

#     gpu.state.face_culling_set("BACK")

#     camera_pos = context.region_data.view_matrix.inverted().translation
#     matrix = context.region_data.perspective_matrix

#     culling_shader.bind()

# bpy.types.SpaceView3D.draw_handler_add(vertex_culling_handler, (bpy.context, (1.0, 1.0, 1.0, 0.0)), 'WINDOW', 'POST_PIXEL')


# class Alx_OT_Shader_PolygonCulling(bpy.types.Operator):
#     """"""

#     bl_label = ""
#     bl_idname = "alx.operator_shader_polygon_culling"

#     @classmethod
#     def poll(self, context: bpy.types.Context):
#         return True
    
#     def execute(self, context: bpy.types.Context):
        
        
#         return {"FINISHED"}