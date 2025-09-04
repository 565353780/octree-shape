#include "node.h"
#include "MeshBoxOverlap.h"
#include <bitset>
#include <deque>

Node::Node(const std::string &id_, uint8_t child_state_)
    : id(id_), child_state(child_state_) {}

void Node::setId(const std::string &id_) { id = id_; }

void Node::setChildState(uint8_t state) {
  for (int i = 0; i < 8; ++i) {
    const int is_child_exist = (state >> i) & 1;
    updateChildState(i, is_child_exist);
  }
}

void Node::setChildDict(
    const std::unordered_map<int, std::shared_ptr<Node>> &dict) {
  child_dict = dict;
  std::bitset<8> bits;
  for (int i = 0; i < 8; ++i) {
    if (child_dict.find(i) != child_dict.end()) {
      bits.set(i);
    }
  }
  child_state = static_cast<uint8_t>(bits.to_ulong());
}

void Node::updateChildState(int child_idx, bool is_child_exist) {
  if (child_idx < 0 || child_idx > 7)
    return;

  if (is_child_exist) {
    if (child_dict.find(child_idx) == child_dict.end()) {
      child_state |= (1 << child_idx);
      child_dict[child_idx] =
          std::make_shared<Node>(id + std::to_string(child_idx));
    }
  } else {
    if (child_dict.find(child_idx) != child_dict.end()) {
      child_state &= ~(1 << child_idx);
      child_dict.erase(child_idx);
    }
  }
}

int Node::depth() const { return static_cast<int>(id.size()); }

bool Node::isLeaf() const { return child_dict.empty(); }

int Node::leafNum() const {
  if (isLeaf())
    return 1;
  int count = 0;
  for (const auto &pair : child_dict) {
    count += pair.second->leafNum();
  }
  return count;
}

std::vector<int> Node::toChildIdxs() const {
  std::vector<int> indices;
  for (int i = 0; i < 8; ++i) {
    if ((child_state >> i) & 1)
      indices.push_back(i);
  }
  return indices;
}

std::array<double, 6> Node::toAABB(double scale) const {
  double half = scale / 2.0;
  std::array<double, 3> min = {-half, -half, -half};
  std::array<double, 3> max = {half, half, half};

  for (char ch : id) {
    std::array<double, 3> half_size = {(max[0] - min[0]) / 2.0,
                                       (max[1] - min[1]) / 2.0,
                                       (max[2] - min[2]) / 2.0};
    int idx = ch - '0';

    // 根据idx调整min max区间
    if (idx == 0 || idx == 2 || idx == 4 || idx == 6)
      max[0] -= half_size[0];
    else
      min[0] += half_size[0];

    if (idx == 0 || idx == 1 || idx == 4 || idx == 5)
      max[1] -= half_size[1];
    else
      min[1] += half_size[1];

    if (idx == 0 || idx == 1 || idx == 2 || idx == 3)
      max[2] -= half_size[2];
    else
      min[2] += half_size[2];
  }

  return {min[0], min[1], min[2], max[0], max[1], max[2]};
}

void Node::addChild(int child_idx) { updateChildState(child_idx, true); }

void Node::removeChild(int child_idx) { updateChildState(child_idx, false); }

void Node::updateOverlaps(const VerticesArray &vertices,
                          const TrianglesArray &triangles) {
  std::array<double, 6> aabb = toAABB();
  overlap_triangles = toMeshBoxOverlap(vertices, triangles, aabb);
}

void Node::updateChilds(const VerticesArray &vertices,
                        const TrianglesArray &triangles) {
  if (overlap_triangles.empty())
    return;

  // 筛选出当前节点重叠的三角形子集
  TrianglesArray valid_triangles;
  valid_triangles.reserve(overlap_triangles.size());
  for (auto idx : overlap_triangles) {
    valid_triangles.push_back(triangles[idx]);
  }

  for (int child_id = 0; child_id < 8; ++child_id) {
    Node child_node(id + std::to_string(child_id));
    std::array<double, 6> aabb = child_node.toAABB();

    auto overlap = toMeshBoxOverlap(vertices, valid_triangles, aabb);
    if (overlap.empty())
      continue;

    updateChildState(child_id, true);

    // 将相对索引映射回父级索引
    std::vector<int64_t> mapped;
    mapped.reserve(overlap.size());
    for (auto sub_idx : overlap) {
      mapped.push_back(overlap_triangles[sub_idx]);
    }
    child_dict[child_id]->overlap_triangles = std::move(mapped);
  }
}

std::vector<std::shared_ptr<Node>> Node::getLeafNodes() const {
  std::vector<std::shared_ptr<Node>> result;
  if (isLeaf()) {
    result.push_back(std::make_shared<Node>(*this));
    return result;
  }

  for (const auto &pair : child_dict) {
    auto sub = pair.second->getLeafNodes();
    result.insert(result.end(), sub.begin(), sub.end());
  }

  return result;
}

std::vector<uint8_t> Node::getShapeCode() const {
  std::deque<std::shared_ptr<const Node>> queue;
  std::vector<uint8_t> values;

  queue.push_back(std::make_shared<const Node>(*this));

  while (!queue.empty()) {
    auto node = queue.front();
    queue.pop_front();

    if (node->isLeaf())
      continue;

    values.push_back(node->child_state);

    for (int i = 0; i < 8; ++i) {
      if (node->child_dict.find(i) != node->child_dict.end()) {
        queue.push_back(node->child_dict.at(i));
      }
    }
  }

  return values;
}
