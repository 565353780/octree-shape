#include "TriangleAABBOverlap.h"
#include <algorithm>
#include <cmath>

inline Vec3 cross(const Vec3 &a, const Vec3 &b) {
  return {a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
          a[0] * b[1] - a[1] * b[0]};
}

inline float dot(const Vec3 &a, const Vec3 &b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

inline Vec3 subtract(const Vec3 &a, const Vec3 &b) {
  return {a[0] - b[0], a[1] - b[1], a[2] - b[2]};
}

inline bool planeBoxOverlap(const Vec3 &normal, const Vec3 &vert,
                            const Vec3 &maxbox) {
  Vec3 vmin, vmax;
  for (int q = 0; q < 3; ++q) {
    if (normal[q] > 0.0f) {
      vmin[q] = -maxbox[q] - vert[q];
      vmax[q] = maxbox[q] - vert[q];
    } else {
      vmin[q] = maxbox[q] - vert[q];
      vmax[q] = -maxbox[q] - vert[q];
    }
  }
  if (dot(normal, vmin) > 0.0f)
    return false;
  if (dot(normal, vmax) >= 0.0f)
    return true;
  return false;
}

inline void findMinMax(float x0, float x1, float x2, float &min, float &max) {
  min = std::min({x0, x1, x2});
  max = std::max({x0, x1, x2});
}

bool triBoxOverlap(const Vec3 &boxCenter, const Vec3 &boxHalfSize,
                   const Triangle &tri) {
  Vec3 v0 = subtract(tri[0], boxCenter);
  Vec3 v1 = subtract(tri[1], boxCenter);
  Vec3 v2 = subtract(tri[2], boxCenter);

  Vec3 e0 = subtract(v1, v0);
  Vec3 e1 = subtract(v2, v1);
  Vec3 e2 = subtract(v0, v2);

  auto axisTest = [&](float a, float b, const Vec3 &vA, const Vec3 &vB,
                      float fa, float fb, int i, int j) {
    float p0 = a * vA[i] - b * vA[j];
    float p1 = a * vB[i] - b * vB[j];
    float min = std::min(p0, p1);
    float max = std::max(p0, p1);
    float rad = fa * boxHalfSize[i] + fb * boxHalfSize[j];
    return !(min > rad || max < -rad);
  };

  float fex = std::fabs(e0[0]), fey = std::fabs(e0[1]), fez = std::fabs(e0[2]);
  if (!axisTest(e0[2], e0[1], v0, v2, fez, fey, 1, 2))
    return false;
  if (!axisTest(e0[2], e0[0], v0, v2, fez, fex, 0, 2))
    return false;
  if (!axisTest(e0[1], e0[0], v1, v2, fey, fex, 0, 1))
    return false;

  fex = std::fabs(e1[0]);
  fey = std::fabs(e1[1]);
  fez = std::fabs(e1[2]);
  if (!axisTest(e1[2], e1[1], v0, v2, fez, fey, 1, 2))
    return false;
  if (!axisTest(e1[2], e1[0], v0, v2, fez, fex, 0, 2))
    return false;
  if (!axisTest(e1[1], e1[0], v0, v1, fey, fex, 0, 1))
    return false;

  fex = std::fabs(e2[0]);
  fey = std::fabs(e2[1]);
  fez = std::fabs(e2[2]);
  if (!axisTest(e2[2], e2[1], v0, v1, fez, fey, 1, 2))
    return false;
  if (!axisTest(e2[2], e2[0], v0, v1, fez, fex, 0, 2))
    return false;
  if (!axisTest(e2[1], e2[0], v1, v2, fey, fex, 0, 1))
    return false;

  float min, max;
  findMinMax(v0[0], v1[0], v2[0], min, max);
  if (min > boxHalfSize[0] || max < -boxHalfSize[0])
    return false;

  findMinMax(v0[1], v1[1], v2[1], min, max);
  if (min > boxHalfSize[1] || max < -boxHalfSize[1])
    return false;

  findMinMax(v0[2], v1[2], v2[2], min, max);
  if (min > boxHalfSize[2] || max < -boxHalfSize[2])
    return false;

  Vec3 normal = cross(e0, e1);
  if (!planeBoxOverlap(normal, v0, boxHalfSize))
    return false;

  return true;
}
