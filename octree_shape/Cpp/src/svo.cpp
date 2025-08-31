#include "svo.h"
#include <chrono>
#include <iostream>

SVO::SVO(int depth_max, const std::string &device) : device(device) {
  root = std::make_shared<Node>();
}

bool SVO::reset() {
  root = std::make_shared<Node>();
  return true;
}

bool SVO::loadMesh(const torch::Tensor &vertices,
                   const torch::Tensor &triangles, const int &depth_max) {
  auto verts = vertices.to(torch::Device(device));
  auto tris = triangles.to(torch::Device(device));

  auto timestamp = std::chrono::steady_clock::now();
  int current_depth = 0;

  root->updateOverlaps(verts, tris, device);

  std::deque<std::shared_ptr<Node>> queue{root};

  while (!queue.empty()) {
    auto node = queue.front();
    queue.pop_front();

    if (node->depth() != current_depth) {
      auto now = std::chrono::steady_clock::now();
      double duration =
          std::chrono::duration_cast<std::chrono::duration<double>>(now -
                                                                    timestamp)
              .count();
      timestamp = now;

      std::cout << "finish solve node depth: " << current_depth
                << ", time spend: " << duration << " s\n";

      current_depth = node->depth();
    }

    node->updateChilds(verts, tris, device);

    for (auto &[_, child] : node->child_dict) {
      if (node->depth() < depth_max - 1) {
        queue.push_back(child);
      }
    }
  }

  auto end = std::chrono::steady_clock::now();
  double total =
      std::chrono::duration_cast<std::chrono::duration<double>>(end - timestamp)
          .count();
  std::cout << "finish solve node depth: " << current_depth
            << ", time spend: " << total << " s\n";

  return true;
}
