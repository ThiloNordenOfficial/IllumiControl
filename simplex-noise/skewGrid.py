import math

import numpy as np
from PIL import Image

# Constants
skewfactor = 0.5 * (math.sqrt(3.0) - 1.0)  # 0.3660254037844386
unskewfactor = (3.0 - math.sqrt(3.0)) / 6.0  # 0.21132486540518713

GRAD3 = [
    [1, 1, 0], [1, -1, 0], [-1, 1, 0], [-1, -1, 0],
    [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1],
    [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1],
    [1, 0, -1], [-1, 0, -1], [0, -1, 1], [0, 1, 1]
]
PERM = [
    151, 160, 137, 91, 90, 15, 131, 13, 201, 95, 96, 53, 194, 233, 7, 225, 140,
    36, 103, 30, 69, 142, 8, 99, 37, 240, 21, 10, 23, 190, 6, 148, 247, 120,
    234, 75, 0, 26, 197, 62, 94, 252, 219, 203, 117, 35, 11, 32, 57, 177, 33,
    88, 237, 149, 56, 87, 174, 20, 125, 136, 171, 168, 68, 175, 74, 165, 71,
    134, 139, 48, 27, 166, 77, 146, 158, 231, 83, 111, 229, 122, 60, 211, 133,
    230, 220, 105, 92, 41, 55, 46, 245, 40, 244, 102, 143, 54, 65, 25, 63, 161,
    1, 216, 80, 73, 209, 76, 132, 187, 208, 89, 18, 169, 200, 196, 135, 130,
    116, 188, 159, 86, 164, 100, 109, 198, 173, 186, 3, 64, 52, 217, 226, 250,
    124, 123, 5, 202, 38, 147, 118, 126, 255, 82, 85, 212, 207, 206, 59, 227,
    47, 16, 58, 17, 182, 189, 28, 42, 223, 183, 170, 213, 119, 248, 152, 2, 44,
    154, 163, 70, 221, 153, 101, 155, 167, 43, 172, 9, 129, 22, 39, 253, 19, 98,
    108, 110, 79, 113, 224, 232, 178, 185, 112, 104, 218, 246, 97, 228, 251, 34,
    242, 193, 238, 210, 144, 12, 191, 179, 162, 241, 81, 51, 145, 235, 249, 14,
    239, 107, 49, 192, 214, 31, 181, 199, 106, 157, 184, 84, 204, 176, 115, 121,
    50, 45, 127, 4, 150, 254, 138, 236, 205, 93, 222, 114, 67, 29, 24, 72, 243,
    141, 128, 195, 78, 66, 215, 61, 156, 180, 151, 160, 137, 91, 90, 15, 131,
    13, 201, 95, 96, 53, 194, 233, 7, 225, 140, 36, 103, 30, 69, 142, 8, 99, 37,
    240, 21, 10, 23, 190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62, 94, 252,
    219, 203, 117, 35, 11, 32, 57, 177, 33, 88, 237, 149, 56, 87, 174, 20, 125,
    136, 171, 168, 68, 175, 74, 165, 71, 134, 139, 48, 27, 166, 77, 146, 158,
    231, 83, 111, 229, 122, 60, 211, 133, 230, 220, 105, 92, 41, 55, 46, 245,
    40, 244, 102, 143, 54, 65, 25, 63, 161, 1, 216, 80, 73, 209, 76, 132, 187,
    208, 89, 18, 169, 200, 196, 135, 130, 116, 188, 159, 86, 164, 100, 109, 198,
    173, 186, 3, 64, 52, 217, 226, 250, 124, 123, 5, 202, 38, 147, 118, 126,
    255, 82, 85, 212, 207, 206, 59, 227, 47, 16, 58, 17, 182, 189, 28, 42, 223,
    183, 170, 213, 119, 248, 152, 2, 44, 154, 163, 70, 221, 153, 101, 155, 167,
    43, 172, 9, 129, 22, 39, 253, 19, 98, 108, 110, 79, 113, 224, 232, 178, 185,
    112, 104, 218, 246, 97, 228, 251, 34, 242, 193, 238, 210, 144, 12, 191, 179,
    162, 241, 81, 51, 145, 235, 249, 14, 239, 107, 49, 192, 214, 31, 181, 199,
    106, 157, 184, 84, 204, 176, 115, 121, 50, 45, 127, 4, 150, 254, 138, 236,
    205, 93, 222, 114, 67, 29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156,
    180
]

def noise2(x, y):
    # Gitter indizes der Dreieck-ecken
    x_skewed = x + (x + y) * skewfactor
    y_skewed = y + (x + y) * skewfactor
    i = math.floor(x_skewed)
    j = math.floor(y_skewed)

    v_i = [0.0] * 3
    v_j = [0.0] * 3

    # Bestimmung der Ecken des Simplex, in dem sich der Punkt (x,y) befindet
    v_i[0] = i
    v_j[0] = j
    if x_skewed - i + y_skewed - j < 0.5:
        v_i[1] = v_i[0] - 1
        v_j[1] = v_j[0]
        v_i[2] = v_i[0]
        v_j[2] = v_j[0] - 1
    else:
        v_i[1] = v_i[0] - 1
        v_j[1] = v_j[0] + 1
        v_i[2] = v_i[0] + 1
        v_j[2] = v_j[0]

    v_x = [0.0] * 3
    v_y = [0.0] * 3

    distance_x = [0.0] * 3
    distance_y = [0.0] * 3
    for c in range(3):
        v_x[c] = v_i[c] - ((v_i[c] + v_j[c]) * unskewfactor)
        v_y[c] = v_j[c] - ((v_i[c] + v_j[c]) * unskewfactor)
        distance_x[c] = x - v_x[c]
        distance_y[c] = y - v_y[c]

    i1 = distance_x[0] > distance_y[0]
    j1 = distance_x[0] <= distance_y[0]

    # distance_x = [0.0] * 3
    # distance_y = [0.0] * 3
    #
    # distance_x[0] = x - (i - (i + j) * unskewfactor)
    # distance_y[0] = y - (j - (i + j) * unskewfactor)
    #
    # i1 = distance_x[0] > distance_y[0]
    # j1 = distance_x[0] <= distance_y[0]
    #
    # distance_x[2] = distance_x[0] + unskewfactor * 2.0 - 1.0
    # distance_y[2] = distance_y[0] + unskewfactor * 2.0 - 1.0
    # distance_x[1] = distance_x[0] - i1 + unskewfactor
    # distance_y[1] = distance_y[0] - j1 + unskewfactor

    # Distanz von Ecken zu x,y
    # 0,5 weil prüfen ob innerhalb von Kreis mit Radius sqrt(0,5) um Ecke liegt
    # durch
    smoothstep = [0.0] * 3
    for c in range(3):
        # Smoothstep function: smoothstep(r) = 0.5 - r^2
        smoothstep[c] = 0.5 - (distance_x[c] ** 2 + distance_y[c] ** 2)

    noise = [0.0] * 3
    # Normierung der Eckenkoordinaten auf 0-255 für die Permutationstabelle
    I = int(i) & 255
    J = int(j) & 255
    g = [0] * 3
    # "Hashing" der Koordinaten der drei Ecken des Simplex, um die Gradientenvektoren zu bestimmen
    g[0] = PERM[I + PERM[J]] % 12
    g[1] = PERM[I + i1 + PERM[J + j1]] % 12
    g[2] = PERM[I + 1 + PERM[J + 1]] % 12

    # Wenn Ecke innerhalb von Kreis liegt (>0)
    # dann Beitrag für Noise berechnen:
    for c in range(3):
        if smoothstep[c] > 0:
            # distanz ^ 4 * (richtungs vector x * distanz zu ecke auf x + richtungs vector y * distanz zu ecke auf y)
            # Radial falloff der smoothstep function: d^4
            # Gradient contribution: Skalarprodukt aus Stützvector (dx, dy) und Richtungsvektor (grad_x, grad_y)
            noise[c] = smoothstep[c] ** 4 * (GRAD3[g[c]][0] * distance_x[c] + GRAD3[g[c]][1] * distance_y[c])

    # Summe von Beiträgen der drei Ecken skalliert mit 70 um den Wertebereich von
    return (noise[0] + noise[1] + noise[2]) * 70.0


if __name__ == "__main__":
    size = 500
    image = np.zeros((size, size))
    for x in range(size):
        for y in range(size):
            image[x][y] = noise2(x/10, y/10)
    img = Image.fromarray(image, mode='L')
    img.save(f"test.png")
