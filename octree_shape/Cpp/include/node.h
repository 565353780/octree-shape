#pragma once

#include "data.h"
#include <array>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

class Node {
public:
  Node(const std::string &id = "", uint8_t child_state = 0);

  // setters
  void setId(const std::string &id_);
  void setChildState(uint8_t state);
  void setChildDict(const std::unordered_map<int, std::shared_ptr<Node>> &dict);
  void updateChildState(int child_idx, bool is_child_exist);

  // getters
  int depth() const;
  bool isLeaf() const;
  int leafNum() const;
  std::vector<int> toChildIdxs() const;
  std::array<double, 3> toCenter() const;
  std::array<double, 6> toAABB(double scale = 1.0) const;
  std::vector<std::shared_ptr<Node>> getLeafNodes() const;
  std::vector<uint8_t> getShapeCode() const;

  // tree manipulation
  void addChild(int child_idx);
  void removeChild(int child_idx);

  // update overlaps using pure arrays
  void updateOverlaps(const VerticesArray &vertices,
                      const TrianglesArray &triangles);

  void updateChilds(const VerticesArray &vertices,
                    const TrianglesArray &triangles);

  // Public members
  std::vector<int64_t> overlap_triangles; // 重叠三角形索引列表

  // identifier and state
  std::string id;
  uint8_t child_state;
  std::unordered_map<int, std::shared_ptr<Node>> child_dict;
};
