import bmesh


def GET_selected_verts(bmesh: bmesh.types.BMesh) -> list[int]:
    return [vert.index for vert in bmesh.verts[:] if (vert.select == True)]
