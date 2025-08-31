#include "MeshBoxOverlap.h"
#include "TriangleBoxOverlap.h"
#include "node.h"
#include "svo.h"
#include <pybind11/chrono.h>
#include <pybind11/complex.h>
#include <pybind11/functional.h>
#include <pybind11/iostream.h>
#include <pybind11/numpy.h>
#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <torch/extension.h>

namespace py = pybind11;

PYBIND11_MODULE(octree_cpp, m) {
  m.doc() = "pybind11 octree cpp plugin";

  m.def("toMeshBoxOverlap", &toMeshBoxOverlap,
        "Check mesh-box overlap and return intersecting triangle indices");

  py::class_<Node, std::shared_ptr<Node>>(m, "Node")
      .def(py::init<const std::string &, uint8_t>(), py::arg("id") = "",
           py::arg("child_state") = 0)

      // Methods
      .def("setId", &Node::setId)
      .def("setChildState", &Node::setChildState)
      .def("setChildDict", &Node::setChildDict)
      .def("updateChildState", &Node::updateChildState)
      .def("addChild", &Node::addChild)
      .def("removeChild", &Node::removeChild)
      .def("updateOverlaps", &Node::updateOverlaps, py::arg("vertices"),
           py::arg("triangles"), py::arg("device") = "cpu")
      .def("updateChilds", &Node::updateChilds, py::arg("vertices"),
           py::arg("triangles"), py::arg("device") = "cpu")

      // Getters / Properties
      .def("depth", &Node::depth)
      .def("isLeaf", &Node::isLeaf)
      .def("leafNum", &Node::leafNum)
      .def("toChildIdxs", &Node::toChildIdxs)
      .def("toAABB", &Node::toAABB)
      .def("getLeafNodes", &Node::getLeafNodes)
      .def("getShapeValue", &Node::getShapeValue)

      // Fields
      .def_readwrite("id", &Node::id)
      .def_readwrite("child_state", &Node::child_state)
      .def_readwrite("child_dict", &Node::child_dict)
      .def_readwrite("overlap_triangles", &Node::overlap_triangles);

  py::class_<SVO>(m, "SVO")
      .def(py::init<int, const std::string &>(), py::arg("depth_max") = 10,
           py::arg("device") = "cpu")
      .def("reset", &SVO::reset)
      .def("loadMesh", &SVO::loadMesh)
      .def_readwrite("root", &SVO::root);
}
