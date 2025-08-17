#pragma once

#include <array>

using Vec3 = std::array<float, 3>;
using Triangle = std::array<Vec3, 3>;

bool triBoxOverlap(const Vec3 &boxCenter, const Vec3 &boxHalfSize,
                   const Triangle &tri);
