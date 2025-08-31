#include "MeshBoxOverlap.h"
#include "TriangleBoxOverlap.h"
#include <vector>

torch::Tensor toMeshBoxOverlap(const torch::Tensor &vertices,
                               const torch::Tensor &triangles,
                               const torch::Tensor &aabb_tensor) {
  TORCH_CHECK(vertices.dtype() == torch::kFloat32 ||
                  vertices.dtype() == torch::kFloat64,
              "vertices must be float32 or float64");
  TORCH_CHECK(triangles.dtype() == torch::kInt64, "triangles must be int64");
  TORCH_CHECK(aabb_tensor.size(0) == 6, "aabb_tensor must be of shape [6]");

  auto verts = vertices.contiguous();
  auto tris = triangles.contiguous();
  auto aabb = aabb_tensor.contiguous();

  // Convert AABB to center / halfsize
  float boxcenter[3], boxhalfsize[3];
  for (int i = 0; i < 3; ++i) {
    float min_val = aabb[i].item<float>();
    float max_val = aabb[i + 3].item<float>();
    boxcenter[i] = (min_val + max_val) / 2.0f;
    boxhalfsize[i] = (max_val - min_val) / 2.0f;
  }

  // Prepare triangle vertices
  int64_t N = triangles.size(0);
  std::vector<std::array<float, 9>> triverts(N);

  for (int64_t i = 0; i < N; ++i) {
    for (int j = 0; j < 3; ++j) {
      int64_t v_idx = tris[i][j].item<int64_t>();
      for (int k = 0; k < 3; ++k) {
        triverts[i][j * 3 + k] = verts[v_idx][k].item<float>();
      }
    }
  }

  // Call original triBoxOverlap loop
  std::vector<int64_t> overlaps;
  for (int64_t i = 0; i < N; ++i) {
    const float (*tri)[3] =
        reinterpret_cast<const float (*)[3]>(triverts[i].data());

    if (triBoxOverlap(boxcenter, boxhalfsize, tri)) {
      overlaps.push_back(i);
    }
  }

  // Return as torch::Tensor
  return torch::from_blob(overlaps.data(),
                          {static_cast<int64_t>(overlaps.size())},
                          torch::kInt64)
      .clone();
}
