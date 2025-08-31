#pragma once

#include "node.h"
#include <deque>
#include <string>
#include <torch/extension.h>

class SVO {
public:
  SVO(int depth_max = 10, const std::string &device = "cpu");

  bool reset();

  bool loadMesh(const torch::Tensor &vertices, const torch::Tensor &triangles,
                const int &depth_max = 10);

private:
  std::string device;

public:
  std::shared_ptr<Node> root;
};
