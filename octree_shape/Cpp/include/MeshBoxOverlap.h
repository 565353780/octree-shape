#pragma once

#include "data.h"
#include <vector>

std::vector<int64_t> toMeshBoxOverlap(const VerticesArray &vertices,
                                      const TrianglesArray &triangles,
                                      const std::array<double, 6> &aabb);
