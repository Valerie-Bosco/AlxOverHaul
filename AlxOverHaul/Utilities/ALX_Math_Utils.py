def AVERAGE_NormalFromVectorList(vector_list: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    average_normal = [0, 0, 0]
    for vector in vector_list:
        average_normal[0] += vector[0]
        average_normal[1] += vector[1]
        average_normal[2] += vector[2]

    return [average_normal[0] / len(vector_list), average_normal[1] / len(vector_list), average_normal[1] / len(vector_list)]
