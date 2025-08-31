#pragma once

#include <string>
#include <torch/extension.h>
#include <unordered_map>
#include <vector>

class Node {
public:
  Node(const std::string &id = "", uint8_t child_state = 0);

  // Setters
  void setId(const std::string &id);
  void setChildState(uint8_t state);
  void setChildDict(const std::unordered_map<int, std::shared_ptr<Node>> &dict);
  void updateChildState(int child_idx, bool is_child_exist);

  // Getters
  int depth() const;
  bool isLeaf() const;
  int leafNum() const;
  torch::Tensor toChildIdxs() const;
  torch::Tensor toAABB(double scale = 1.0) const;
  std::vector<std::shared_ptr<Node>> getLeafNodes() const;
  torch::Tensor getShapeValue() const;

  // Tree manipulation
  void addChild(int child_idx);
  void removeChild(int child_idx);
  void updateOverlaps(const torch::Tensor &vertices,
                      const torch::Tensor &triangles,
                      const std::string &device = "cpu");

  void updateChilds(const torch::Tensor &vertices,
                    const torch::Tensor &triangles,
                    const std::string &device = "cpu");

  // Public members (tensors only)
  torch::Tensor overlap_triangles;

  // Public identifier and state
  std::string id;
  uint8_t child_state;
  std::unordered_map<int, std::shared_ptr<Node>> child_dict;
};
