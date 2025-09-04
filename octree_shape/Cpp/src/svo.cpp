#include "svo.h"
#include <chrono>
#include <deque>
#include <iostream>

SVO::SVO(int depth_max_) : depth_max(depth_max_) {
  root = std::make_shared<Node>();
}

bool SVO::reset() {
  root = std::make_shared<Node>();
  return true;
}

bool SVO::loadMesh(const VerticesArray &vertices,
                   const TrianglesArray &triangles, int max_depth) {
  auto start = std::chrono::steady_clock::now();
  root->updateOverlaps(vertices, triangles);

  std::deque<std::shared_ptr<Node>> queue{root};
  int current_depth = 0;

  while (!queue.empty()) {
    auto node = queue.front();
    queue.pop_front();

    int node_depth = node->depth();
    if (node_depth != current_depth) {
      auto now = std::chrono::steady_clock::now();
      double elapsed =
          std::chrono::duration_cast<std::chrono::duration<double>>(now - start)
              .count();
      std::cout << "Depth " << current_depth << " done in " << elapsed << "s\n";
      start = now;
      current_depth = node_depth;
    }

    node->updateChilds(vertices, triangles);

    if (node_depth < max_depth - 1) {
      for (const auto &[_, child] : node->child_dict) {
        queue.push_back(child);
      }
    }
  }

  auto now = std::chrono::steady_clock::now();
  double elapsed =
      std::chrono::duration_cast<std::chrono::duration<double>>(now - start)
          .count();
  std::cout << "Depth " << current_depth << " done in " << elapsed << "s\n";

  return true;
}

bool SVO::loadShapeCode(const std::vector<std::uint8_t> &shape_code) {
  std::deque<std::shared_ptr<Node>> queue{root};

  size_t idx = 0;

  while (!queue.empty()) {
    if (idx >= shape_code.size()) {
      break;
    }

    auto node = queue.front();
    queue.pop_front();

    node->setChildState(shape_code[idx]);
    ++idx;

    // 遍历子节点
    for (int i = 0; i < 8; ++i) {
      auto it = node->child_dict.find(i);
      if (it != node->child_dict.end()) {
        queue.push_back(it->second);
      }
    }
  }

  return true;
}
