import math
from typing import List

import earcut.earcut
from specklepy.objects.geometry.mesh import Mesh
from specklepy.objects.geometry.polyline import Polyline


def generate_region_mesh(boundary: Polyline, inner_loops: List[Polyline], units: str):
    """Generate Speckle Mesh for a planar shape represented by boundary and inner loops."""

    # Get a 'list of coordinate tuples' for boundary points
    vertices3d_tuples: List[List[float]] = _flat_coords_to_tuples(boundary)

    # Get a list of 'lists of coordinate tuples' for inner loops
    loops3d_tuples_list: List[List[List[float]]] = []
    for loop in inner_loops:
        vertices3d_loop_tuples = _flat_coords_to_tuples(loop)
        loops3d_tuples_list.append(vertices3d_loop_tuples)

    # triangulate region
    all_coords, triangles = _get_all_coords_and_triangles(
        vertices3d_tuples, loops3d_tuples_list
    )

    # construct mesh
    mesh: Mesh = _construct_mesh_from_triangles(all_coords, triangles, units)

    return mesh


def _flat_coords_to_tuples(polyline: Polyline):
    """Reduce resolution of the given polyline (if vertices exceed max amount),
    and return the list of vertices' coordinate tuples."""

    max_points = 1000
    coef = math.ceil(len(polyline.value) / (3 * max_points))

    # Get a list of coordinate tuples for polyline points
    points_count = int(len(polyline.value) / 3)
    coordinates_tuples: List[List[float]] = [
        (
            polyline.value[i * coef * 3],
            polyline.value[i * coef * 3 + 1],
            polyline.value[i * coef * 3 + 2],
        )
        for i, _ in enumerate(polyline.value)
        if i * coef < points_count
    ]
    return coordinates_tuples


def _get_all_coords_and_triangles(
    vertices3d_tuples: List[List[float]], loops3d_tuples: List[List[List[float]]]
):
    """Triangulate the shape given tuple lists of boundary and loops' coordinates.
    Return full flat list of triangulated vertices and list of triangle tuples."""

    data = earcut.earcut.flatten([vertices3d_tuples] + loops3d_tuples)
    triangles_flat_list = earcut.earcut.earcut(data["vertices"], data["holes"], dim=3)

    triangle_tuples = [
        [
            triangles_flat_list[3 * i],
            triangles_flat_list[3 * i + 1],
            triangles_flat_list[3 * i + 2],
        ]
        for i, _ in enumerate(triangles_flat_list)
        if i < len(triangles_flat_list) / 3
    ]

    return data["vertices"], triangle_tuples


def _construct_mesh_from_triangles(all_coords, triangles, units) -> Mesh:
    """Construct Speckle Mesh given a flat list of coordinates and a list of triangles
    (defined by tuples with vertices' indices)."""

    total_vertices = 0
    vertices = []
    faces = []

    for trg in triangles:

        # make sure all faces are clockwise (facing down). Seems earcut already returns clockwise faces
        vertices.extend(
            all_coords[3 * trg[0] : 3 * trg[0] + 3]
            + all_coords[3 * trg[1] : 3 * trg[1] + 3]
            + all_coords[3 * trg[2] : 3 * trg[2] + 3]
        )

        faces.extend(
            [
                3,
                total_vertices,
                total_vertices + 1,
                total_vertices + 2,
            ]
        )
        total_vertices += 3

    return Mesh(vertices=vertices, faces=faces, units=units)
