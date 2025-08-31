#include "BVHTree.h"
#include <embree4/rtcore.h>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>

namespace py = pybind11;

void BVHWrapper::build(const std::vector<Vec3f> &vertices,
                       const std::vector<std::array<unsigned, 3>> &triangles) {
  RTCGeometry geom = rtcNewGeometry(device, RTC_GEOMETRY_TYPE_TRIANGLE);

  Vec3f *vertexBuffer = (Vec3f *)rtcSetNewGeometryBuffer(
      geom, RTC_BUFFER_TYPE_VERTEX, 0, RTC_FORMAT_FLOAT3, sizeof(Vec3f),
      vertices.size());
  std::copy(vertices.begin(), vertices.end(), vertexBuffer);

  unsigned *indexBuffer = (unsigned *)rtcSetNewGeometryBuffer(
      geom, RTC_BUFFER_TYPE_INDEX, 0, RTC_FORMAT_UINT3, 3 * sizeof(unsigned),
      triangles.size());
  std::memcpy(indexBuffer, triangles.data(),
              sizeof(unsigned) * 3 * triangles.size());

  rtcCommitGeometry(geom);
  geomID = rtcAttachGeometry(scene, geom);
  rtcReleaseGeometry(geom);
  rtcCommitScene(scene);

  this->vertices = vertices;
  this->triangles = triangles;
}

std::vector<unsigned> BVHWrapper::query_aabb(const AABB &box) {
  std::vector<unsigned> hits;

  RTCBounds bounds;
  bounds.lower_x = box.lower.x;
  bounds.lower_y = box.lower.y;
  bounds.lower_z = box.lower.z;
  bounds.upper_x = box.upper.x;
  bounds.upper_y = box.upper.y;
  bounds.upper_z = box.upper.z;

  struct UserData {
    const AABB *aabb;
    const std::vector<std::array<unsigned, 3>> *tris;
    std::vector<unsigned> *hits;
  } userData{&box, &triangles, &hits};

  auto boundsFunc = [](const struct RTCBoundsFunctionArguments *args) {
    auto *bounds_o = (RTCBounds *)args->bounds_o;
    // Not needed; we use prebuilt BVH
  };

  auto intersectFunc = [](const RTCIntersectFunctionNArguments *args) {
    const UserData *data = (UserData *)args->geometryUserPtr;
    unsigned primID = args->primID;

    // Here we just add all primID whose bounds overlap AABB
    data->hits->push_back(primID);
  };

  // Not directly exposed, so we simulate the AABB test with RTCQuery
  // Instead: iterate over triangles, test triangle AABB with box

  for (unsigned i = 0; i < triangles.size(); ++i) {
    const auto &tri = triangles[i];
    Vec3f v0 = vertices[tri[0]];
    Vec3f v1 = vertices[tri[1]];
    Vec3f v2 = vertices[tri[2]];

    Vec3f triMin = {
        std::min({v0.x, v1.x, v2.x}),
        std::min({v0.y, v1.y, v2.y}),
        std::min({v0.z, v1.z, v2.z}),
    };
    Vec3f triMax = {
        std::max({v0.x, v1.x, v2.x}),
        std::max({v0.y, v1.y, v2.y}),
        std::max({v0.z, v1.z, v2.z}),
    };

    if (triMax.x < box.lower.x || triMin.x > box.upper.x)
      continue;
    if (triMax.y < box.lower.y || triMin.y > box.upper.y)
      continue;
    if (triMax.z < box.lower.z || triMin.z > box.upper.z)
      continue;

    hits.push_back(i);
  }

  return hits;
}
