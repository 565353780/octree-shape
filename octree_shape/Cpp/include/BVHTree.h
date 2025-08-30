#pragma once

#include <limits>
#include <memory>
#include <vector>

// 三角形定义
struct Triangle {
  float v0[3], v1[3], v2[3];
  int id; // 可选：三角形标识符
};

// 轴对齐包围盒(AABB)
struct AABB {
  float min[3];
  float max[3];

  AABB();

  // 扩展AABB以包含一个点
  void expand(const float point[3]);

  // 扩展AABB以包含另一个AABB
  void expand(const AABB &other);

  // 计算AABB的中心点
  void getCenter(float center[3]) const;

  // 计算AABB的半边长
  void getHalfSize(float halfSize[3]) const;

  // 判断两个AABB是否相交
  bool intersects(const AABB &other) const;
};

struct TriangleComparator {
  int axis;
  const std::vector<Triangle> &triangles;

  TriangleComparator(int a, const std::vector<Triangle> &tris)
      : axis(a), triangles(tris) {}

  bool operator()(int a, int b) const;
};

// BVH节点
struct BVHNode {
  AABB bbox;
  bool isLeaf;
  int startTri, endTri; // 对于叶子节点：三角形范围的起始和结束索引
  std::unique_ptr<BVHNode> left;
  std::unique_ptr<BVHNode> right;

  BVHNode() : isLeaf(false), startTri(-1), endTri(-1) {}
};

// BVH树
class BVHTree {
private:
  std::unique_ptr<BVHNode> root;
  std::vector<Triangle> triangles;

  // 递归构建BVH
  std::unique_ptr<BVHNode> buildRecursive(std::vector<int> &indices, int start,
                                          int end, int depth);

  // 计算一组三角形的包围盒
  AABB computeBoundingBox(const std::vector<int> &indices, int start, int end);

public:
  BVHTree(const std::vector<Triangle> &tris);

  // 查询与AABB可能相交的三角形
  void query(const AABB &queryBox, std::vector<int> &results) const;

  // 判断是否存在与AABB相交的三角形（最快方法）
  bool anyIntersection(const float boxCenter[3],
                       const float boxHalfSize[3]) const;
};
