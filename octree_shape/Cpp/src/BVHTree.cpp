#include "BVHTree.h"
#include "TriangleBoxOverlap.h"
#include <queue>

AABB::AABB() {
  min[0] = min[1] = min[2] = std::numeric_limits<float>::max();
  max[0] = max[1] = max[2] = -std::numeric_limits<float>::max();
}

void AABB::expand(const float point[3]) {
  for (int i = 0; i < 3; i++) {
    if (point[i] < min[i])
      min[i] = point[i];
    if (point[i] > max[i])
      max[i] = point[i];
  }
}

void AABB::expand(const AABB &other) {
  for (int i = 0; i < 3; i++) {
    if (other.min[i] < min[i])
      min[i] = other.min[i];
    if (other.max[i] > max[i])
      max[i] = other.max[i];
  }
}

void AABB::getCenter(float center[3]) const {
  for (int i = 0; i < 3; i++) {
    center[i] = (min[i] + max[i]) * 0.5f;
  }
}

void AABB::getHalfSize(float halfSize[3]) const {
  for (int i = 0; i < 3; i++) {
    halfSize[i] = (max[i] - min[i]) * 0.5f;
  }
}

bool AABB::intersects(const AABB &other) const {
  for (int i = 0; i < 3; i++) {
    if (max[i] < other.min[i] || min[i] > other.max[i]) {
      return false;
    }
  }
  return true;
}

bool TriangleComparator::operator()(int a, int b) const {
  float centerA[3], centerB[3];

  // 计算三角形A的中心
  centerA[0] =
      (triangles[a].v0[0] + triangles[a].v1[0] + triangles[a].v2[0]) / 3.0f;
  centerA[1] =
      (triangles[a].v0[1] + triangles[a].v1[1] + triangles[a].v2[1]) / 3.0f;
  centerA[2] =
      (triangles[a].v0[2] + triangles[a].v1[2] + triangles[a].v2[2]) / 3.0f;

  // 计算三角形B的中心
  centerB[0] =
      (triangles[b].v0[0] + triangles[b].v1[0] + triangles[b].v2[0]) / 3.0f;
  centerB[1] =
      (triangles[b].v0[1] + triangles[b].v1[1] + triangles[b].v2[1]) / 3.0f;
  centerB[2] =
      (triangles[b].v0[2] + triangles[b].v1[2] + triangles[b].v2[2]) / 3.0f;

  return centerA[axis] < centerB[axis];
}

BVHTree::BVHTree(const std::vector<Triangle> &tris) : triangles(tris) {
  // 创建索引数组
  std::vector<int> indices(triangles.size());
  for (int i = 0; i < triangles.size(); i++) {
    indices[i] = i;
  }

  // 递归构建BVH
  root = buildRecursive(indices, 0, indices.size(), 0);
}

AABB BVHTree::computeBoundingBox(const std::vector<int> &indices, int start,
                                 int end) {
  AABB bbox;
  for (int i = start; i < end; i++) {
    const Triangle &tri = triangles[indices[i]];
    bbox.expand(tri.v0);
    bbox.expand(tri.v1);
    bbox.expand(tri.v2);
  }
  return bbox;
}

std::unique_ptr<BVHNode> BVHTree::buildRecursive(std::vector<int> &indices,
                                                 int start, int end,
                                                 int depth) {
  auto node = std::make_unique<BVHNode>();
  node->bbox = computeBoundingBox(indices, start, end);

  // 如果三角形数量少于阈值，创建叶子节点
  const int LEAF_THRESHOLD = 4;
  if (end - start <= LEAF_THRESHOLD) {
    node->isLeaf = true;
    node->startTri = start;
    node->endTri = end;
    return node;
  }

  // 选择分割轴（使用循环法：x, y, z）
  int axis = depth % 3;

  // 按选定轴排序三角形索引
  TriangleComparator comp(axis, triangles);
  int mid = start + (end - start) / 2;
  std::nth_element(indices.begin() + start, indices.begin() + mid,
                   indices.begin() + end, comp);

  // 递归构建左右子树
  node->left = buildRecursive(indices, start, mid, depth + 1);
  node->right = buildRecursive(indices, mid, end, depth + 1);

  return node;
}

// 查询与AABB可能相交的三角形（填充结果列表）
void BVHTree::query(const AABB &queryBox, std::vector<int> &results) const {
  if (!root)
    return;

  // 使用迭代而非递归，避免栈溢出
  std::queue<const BVHNode *> queue;
  queue.push(root.get());

  while (!queue.empty()) {
    const BVHNode *node = queue.front();
    queue.pop();

    // 如果节点包围盒与查询包围盒不相交，跳过整个子树
    if (!node->bbox.intersects(queryBox)) {
      continue;
    }

    // 如果是叶子节点，将三角形添加到结果中
    if (node->isLeaf) {
      for (int i = node->startTri; i < node->endTri; i++) {
        results.push_back(i);
      }
    } else {
      // 否则，将子节点加入队列
      if (node->left)
        queue.push(node->left.get());
      if (node->right)
        queue.push(node->right.get());
    }
  }
}

// 最快方法：判断是否存在与AABB相交的三角形
bool BVHTree::anyIntersection(const float boxCenter[3],
                              const float boxHalfSize[3]) const {
  if (!root)
    return false;

  // 创建查询AABB
  AABB queryBox;
  for (int i = 0; i < 3; i++) {
    queryBox.min[i] = boxCenter[i] - boxHalfSize[i];
    queryBox.max[i] = boxCenter[i] + boxHalfSize[i];
  }

  // 使用迭代而非递归
  std::queue<const BVHNode *> queue;
  queue.push(root.get());

  while (!queue.empty()) {
    const BVHNode *node = queue.front();
    queue.pop();

    // 如果节点包围盒与查询包围盒不相交，跳过整个子树
    if (!node->bbox.intersects(queryBox)) {
      continue;
    }

    // 如果是叶子节点，检查每个三角形
    if (node->isLeaf) {
      for (int i = node->startTri; i < node->endTri; i++) {
        const Triangle &tri = triangles[i];
        float triverts[3][3] = {{tri.v0[0], tri.v0[1], tri.v0[2]},
                                {tri.v1[0], tri.v1[1], tri.v1[2]},
                                {tri.v2[0], tri.v2[1], tri.v2[2]}};

        // 使用高效的triBoxOverlap函数进行精确检测
        if (triBoxOverlap(boxCenter, boxHalfSize, triverts)) {
          return true; // 找到一个相交，立即返回
        }
      }
    } else {
      // 否则，将子节点加入队列
      // 可以选择先添加更可能相交的子节点以优化搜索顺序
      if (node->left)
        queue.push(node->left.get());
      if (node->right)
        queue.push(node->right.get());
    }
  }

  return false; // 没有找到任何相交
}
