#pragma once

#include <embree4/rtcore.h>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>

struct Vec3f {
  float x, y, z;
};
struct AABB {
  Vec3f lower;
  Vec3f upper;
};

class BVHWrapper {
public:
  BVHWrapper() {
    device = rtcNewDevice(nullptr);
    scene = rtcNewScene(device);
  }

  ~BVHWrapper() {
    rtcReleaseScene(scene);
    rtcReleaseDevice(device);
  }

  void build(const std::vector<Vec3f> &vertices,
             const std::vector<std::array<unsigned, 3>> &triangles);

  std::vector<unsigned> query_aabb(const AABB &box);

private:
  RTCDevice device;
  RTCScene scene;
  unsigned geomID;
  std::vector<Vec3f> vertices;
  std::vector<std::array<unsigned, 3>> triangles;
};
