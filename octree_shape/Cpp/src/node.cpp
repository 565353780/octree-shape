#include "node.h"
#include "MeshBoxOverlap.h"
#include <bitset>
#include <deque>
#include <sstream>

Node::Node(const std::string &id, uint8_t child_state)
    : id(id), child_state(child_state),
      overlap_triangles(torch::empty({0}, torch::kLong)) {}

void Node::setId(const std::string &id_) { id = id_; }

void Node::setChildState(uint8_t state) { child_state = state; }

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

torch::Tensor Node::toChildIdxs() const {
  std::vector<int64_t> indices;
  for (int i = 0; i < 8; ++i) {
    if ((child_state >> i) & 1)
      indices.push_back(i);
  }
  return torch::tensor(indices, torch::kLong);
}

torch::Tensor Node::toAABB(double scale) const {
  double half = scale / 2.0;
  torch::Tensor min = torch::full({3}, -half, torch::kFloat64);
  torch::Tensor max = torch::full({3}, half, torch::kFloat64);

  for (char ch : id) {
    torch::Tensor half_size = (max - min) / 2.0;
    int idx = ch - '0';

    if (idx == 0 || idx == 2 || idx == 4 || idx == 6)
      max[0] -= half_size[0].item<double>();
    else
      min[0] += half_size[0].item<double>();

    if (idx == 0 || idx == 1 || idx == 4 || idx == 5)
      max[1] -= half_size[1].item<double>();
    else
      min[1] += half_size[1].item<double>();

    if (idx == 0 || idx == 1 || idx == 2 || idx == 3)
      max[2] -= half_size[2].item<double>();
    else
      min[2] += half_size[2].item<double>();
  }

  return torch::cat({min, max});
}

void Node::addChild(int child_idx) { updateChildState(child_idx, true); }

void Node::removeChild(int child_idx) { updateChildState(child_idx, false); }

void Node::updateOverlaps(const torch::Tensor &vertices,
                          const torch::Tensor &triangles,
                          const std::string &device) {
  torch::Tensor aabb = toAABB().to(torch::Device(device), torch::kFloat64);
  overlap_triangles = toMeshBoxOverlap(vertices, triangles, aabb);
}

void Node::updateChilds(const torch::Tensor &vertices,
                        const torch::Tensor &triangles,
                        const std::string &device) {
  auto valid_triangles = triangles.index_select(0, overlap_triangles);

  for (int child_id = 0; child_id < 8; ++child_id) {
    Node child_node(id + std::to_string(child_id));
    torch::Tensor aabb =
        child_node.toAABB().to(torch::Device(device), torch::kFloat64);

    torch::Tensor overlap = toMeshBoxOverlap(vertices, valid_triangles, aabb);

    if (overlap.numel() == 0)
      continue;

    updateChildState(child_id, true);

    torch::Tensor mapped = overlap_triangles.index_select(0, overlap);
    child_dict[child_id]->overlap_triangles = mapped;
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

torch::Tensor Node::getShapeValue() const {
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

  return torch::tensor(values, torch::kUInt8);
}
