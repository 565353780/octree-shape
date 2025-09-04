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
                int depth_max = 10);

  bool loadShapeCode(const std::vector<std::uint8_t> &shape_code);

private:
  int depth_max;

public:
  std::shared_ptr<Node> root;
};
