#include "MeshBoxOverlap.h"
#include "TriangleBoxOverlap.h"
#include <array>
#include <cstdint>
#include <vector>

std::vector<int64_t> toMeshBoxOverlap(const VerticesArray &vertices,
                                      const TrianglesArray &triangles,
                                      const std::array<double, 6> &aabb) {
  float boxcenter[3], boxhalfsize[3];
  for (int i = 0; i < 3; ++i) {
    float min_val = static_cast<float>(aabb[i]);
    float max_val = static_cast<float>(aabb[i + 3]);
    boxcenter[i] = (min_val + max_val) * 0.5f;
    boxhalfsize[i] = (max_val - min_val) * 0.5f;
  }

  std::vector<int64_t> overlaps;
  overlaps.reserve(triangles.size());

  for (int64_t i = 0; i < static_cast<int64_t>(triangles.size()); ++i) {
    float tri[3][3];
    for (int j = 0; j < 3; ++j) {
      int64_t v_idx = triangles[i][j];
      tri[j][0] = static_cast<float>(vertices[v_idx][0]);
      tri[j][1] = static_cast<float>(vertices[v_idx][1]);
      tri[j][2] = static_cast<float>(vertices[v_idx][2]);
    }

    if (triBoxOverlap(boxcenter, boxhalfsize, tri)) {
      overlaps.push_back(i);
    }
  }

  return overlaps;
}
