#include "TriangleAABBOverlap.h"
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

bool tri_box_overlap_numpy(py::array_t<float> box_center,
                           py::array_t<float> box_halfsize,
                           py::array_t<float> tri_verts) {
  if (box_center.size() != 3 || box_halfsize.size() != 3)
    throw std::runtime_error(
        "box_center and box_halfsize must be 3-element arrays.");
  if (tri_verts.size() != 9)
    throw std::runtime_error("tri_verts must be a 3x3 array.");

  auto bc = box_center.unchecked<1>();
  auto hs = box_halfsize.unchecked<1>();
  auto tv = tri_verts.unchecked<2>();

  Vec3 center = {bc(0), bc(1), bc(2)};
  Vec3 halfsize = {hs(0), hs(1), hs(2)};
  Triangle tri = {{{{tv(0, 0), tv(0, 1), tv(0, 2)}},
                   {{tv(1, 0), tv(1, 1), tv(1, 2)}},
                   {{tv(2, 0), tv(2, 1), tv(2, 2)}}}};

  return triBoxOverlap(center, halfsize, tri);
}

PYBIND11_MODULE(octree_cpp, m) {
  m.doc() = "pybind11 octree cpp plugin";

  m.def("tri_box_overlap", &tri_box_overlap_numpy,
        "Check triangle-AABB intersection");
}
