#pragma once

#include <torch/extension.h>
#include <vector>

// 你定义的别名，确保头文件里定义过
using VerticesArray = std::vector<std::array<double, 3>>;
using TrianglesArray = std::vector<std::array<int64_t, 3>>;

std::vector<int64_t> toMeshBoxOverlap(const VerticesArray &vertices,
                                      const TrianglesArray &triangles,
                                      const std::array<double, 6> &aabb);
