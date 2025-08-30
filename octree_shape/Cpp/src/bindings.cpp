#include "BVHTree.h"
#include "MeshBoxOverlap.h"
#include "TriangleBoxOverlap.h"
#include <pybind11/numpy.h> // 支持 NumPy 数组
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// 包装函数：将 Python 传递的缓冲区对象转换为 C++ 数组并调用 triBoxOverlap
int triBoxOverlap_wrapper(py::array_t<float> boxcenter_array,
                          py::array_t<float> boxhalfsize_array,
                          py::array_t<float> triverts_array) {
  // 获取 boxcenter 数组的缓冲区信息并验证
  py::buffer_info info_center = boxcenter_array.request();
  if (info_center.ndim != 1 || info_center.shape[0] != 3)
    throw std::runtime_error("boxcenter must be a 1D array of size 3");
  float *boxcenter_ptr = static_cast<float *>(info_center.ptr);

  // 获取 boxhalfsize 数组的缓冲区信息并验证
  py::buffer_info info_halfsize = boxhalfsize_array.request();
  if (info_halfsize.ndim != 1 || info_halfsize.shape[0] != 3)
    throw std::runtime_error("boxhalfsize must be a 1D array of size 3");
  float *boxhalfsize_ptr = static_cast<float *>(info_halfsize.ptr);

  // 获取 triverts 数组的缓冲区信息并验证
  py::buffer_info info_triverts = triverts_array.request();
  if (info_triverts.ndim != 2 || info_triverts.shape[0] != 3 ||
      info_triverts.shape[1] != 3)
    throw std::runtime_error("triverts must be a 2D array of shape 3x3");
  float (*triverts_ptr)[3] = reinterpret_cast<float (*)[3]>(
      info_triverts.ptr); // 注意 reinterpret_cast

  // 调用原始函数
  return triBoxOverlap(boxcenter_ptr, boxhalfsize_ptr, triverts_ptr);
}

bool any_intersection_wrapper(py::array_t<float> box_center,
                              py::array_t<float> box_half_size,
                              py::array_t<float> triangles_array) {

  // 验证和转换 box_center
  if (box_center.size() != 3) {
    throw std::runtime_error("box_center must have exactly 3 elements");
  }
  float boxCenter[3];
  auto box_center_ptr = box_center.unchecked<1>();
  for (int i = 0; i < 3; ++i) {
    boxCenter[i] = box_center_ptr(i);
  }

  // 验证和转换 box_half_size
  if (box_half_size.size() != 3) {
    throw std::runtime_error("box_half_size must have exactly 3 elements");
  }
  float boxHalfSize[3];
  auto box_half_size_ptr = box_half_size.unchecked<1>();
  for (int i = 0; i < 3; ++i) {
    boxHalfSize[i] = box_half_size_ptr(i);
  }

  // 验证和转换 triangles_array
  if (triangles_array.ndim() != 2 || triangles_array.shape(1) != 9) {
    throw std::runtime_error(
        "triangles_array must be a 2D array with shape (N, 9)");
  }

  auto triangles_ptr = triangles_array.unchecked<2>();
  int num_triangles = triangles_ptr.shape(0);

  // 将 NumPy 数组转换为 std::vector<std::vector<float>>
  std::vector<Triangle> triangles(num_triangles);
  for (int i = 0; i < num_triangles; ++i) {
    for (int j = 0; j < 3; ++j) {
      triangles[i].v0[j] = triangles_ptr(i, j);
    }
    for (int j = 3; j < 6; ++j) {
      triangles[i].v1[j - 3] = triangles_ptr(i, j);
    }
    for (int j = 6; j < 9; ++j) {
      triangles[i].v2[j - 6] = triangles_ptr(i, j);
    }
  }

  // 调用实际的函数
  return anyIntersectionSerial(boxCenter, boxHalfSize, triangles);
}

PYBIND11_MODULE(octree_cpp, m) {
  m.doc() = "pybind11 octree cpp plugin";

  m.def("triBoxOverlap", &triBoxOverlap_wrapper,
        "Check if a triangle overlaps an AABB", py::arg("boxcenter"),
        py::arg("boxhalfsize"), py::arg("triverts"));
  m.def("any_intersection", &any_intersection_wrapper,
        "Check if any triangle intersects with the AABB", py::arg("box_center"),
        py::arg("box_half_size"), py::arg("triangles"));
}
