#include "node.h"
#include "svo.h"
#include <pybind11/functional.h> // 如果需要绑定函数
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>      // 支持 STL 容器绑定
#include <pybind11/stl_bind.h> // 支持STL容器绑定

namespace py = pybind11;

PYBIND11_MODULE(octree_cpp, m) {
  m.doc() = "pybind11 octree cpp plugin";

  // 绑定 Node 类
  py::class_<Node, std::shared_ptr<Node>>(m, "Node")
      .def(py::init<const std::string &, uint8_t>(), py::arg("id") = "",
           py::arg("child_state") = 0)

      // Setters
      .def("setId", &Node::setId)
      .def("setChildState", &Node::setChildState)
      .def("setChildDict", &Node::setChildDict)
      .def("updateChildState", &Node::updateChildState)

      // Tree manipulation
      .def("addChild", &Node::addChild)
      .def("removeChild", &Node::removeChild)
      .def("updateOverlaps", &Node::updateOverlaps, py::arg("vertices"),
           py::arg("triangles"))
      .def("updateChilds", &Node::updateChilds, py::arg("vertices"),
           py::arg("triangles"))

      // Getters
      .def("depth", &Node::depth)
      .def("isLeaf", &Node::isLeaf)
      .def("leafNum", &Node::leafNum)
      .def("toChildIdxs", &Node::toChildIdxs)
      .def("toCenter", &Node::toCenter)
      .def("toAABB", &Node::toAABB, py::arg("scale") = 1.0)
      .def("getLeafNodes", &Node::getLeafNodes)
      .def("getShapeCode", &Node::getShapeCode)

      // Fields
      .def_readwrite("id", &Node::id)
      .def_readwrite("child_state", &Node::child_state)
      // child_dict是unordered_map<int, shared_ptr<Node>>
      // 这里直接暴露可能有问题，建议用property或者自定义接口，如果确实要暴露：
      .def_readwrite("child_dict", &Node::child_dict)
      .def_readwrite("overlap_triangles", &Node::overlap_triangles);

  // 绑定 SVO 类
  py::class_<SVO>(m, "SVO")
      .def(py::init<int>(), py::arg("depth_max") = 10)
      .def("reset", &SVO::reset)
      .def("loadMesh", &SVO::loadMesh, py::arg("vertices"),
           py::arg("triangles"), py::arg("depth_max") = 10)
      .def("loadShapeCode", &SVO::loadShapeCode, py::arg("shape_code"))
      .def_readwrite("root", &SVO::root);
}
