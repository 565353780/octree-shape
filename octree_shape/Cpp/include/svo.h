#pragma once

#include "node.h"
#include <cstdint>
#include <memory>
#include <string>

class SVO {
public:
  SVO(int depth_max = 10);

  bool reset();

  bool loadMesh(const VerticesArray &vertices, const TrianglesArray &triangles,
                const int &depth_max = 10, const bool &output_info = false);

  bool loadShapeCode(const std::vector<std::uint8_t> &shape_code);

private:
  int depth_max;

public:
  std::shared_ptr<Node> root;
};
