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

PYBIND11_MODULE(octree_cpp, m) {
  m.doc() = "pybind11 octree cpp plugin";

  m.def("triBoxOverlap", &triBoxOverlap_wrapper,
        "Check if a triangle overlaps an AABB", py::arg("boxcenter"),
        py::arg("boxhalfsize"), py::arg("triverts"));
}
