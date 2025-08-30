#include "MeshBoxOverlap.h"

bool anyIntersectionSerial(const float boxCenter[3], const float boxHalfSize[3],
                           const std::vector<Triangle> &triangles) {
  BVHTree bvhTree(triangles);

  return bvhTree.anyIntersection(boxCenter, boxHalfSize);
}
