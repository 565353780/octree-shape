#include "MeshBoxOverlap.h"
#include "TriangleBoxOverlap.h"

const std::vector<unsigned> toMeshBoxOverlap(const float boxcenter[3],
                                             const float boxhalfsize[3],
                                             const float (*triverts)[9],
                                             const size_t N) {
  std::vector<unsigned> overlaps;

  for (size_t i = 0; i < N; ++i) {
    const float (*tri)[3] = (const float (*)[3])triverts[i];

    if (triBoxOverlap(boxcenter, boxhalfsize, tri)) {
      overlaps.emplace_back(i);
    }
  }

  return overlaps;
}

const bool isMeshBoxOverlap(const float boxcenter[3],
                            const float boxhalfsize[3],
                            const float (*triverts)[9], // triverts[N][9]
                            const size_t N) {
  for (size_t i = 0; i < N; ++i) {
    const float (*tri)[3] = (const float (*)[3])triverts[i];

    if (triBoxOverlap(boxcenter, boxhalfsize, tri)) {
      return true;
    }
  }

  return false;
}
