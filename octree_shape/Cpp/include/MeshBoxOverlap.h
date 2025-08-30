#pragma once

#include "BVHTree.h"
#include <iostream>

bool anyIntersectionSerial(const float boxCenter[3], const float boxHalfSize[3],
                           const std::vector<Triangle> &triangles);
