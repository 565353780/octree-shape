#pragma once

#include <torch/extension.h>

torch::Tensor toMeshBoxOverlap(const torch::Tensor &vertices,
                               const torch::Tensor &triangles,
                               const torch::Tensor &aabb_tensor);
