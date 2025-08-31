#pragma once

#include <iostream>

const std::vector<unsigned> toMeshBoxOverlap(const float boxcenter[3],
                                             const float boxhalfsize[3],
                                             const float (*triverts)[9],
                                             const size_t N);

const bool isMeshBoxOverlap(const float boxcenter[3],
                            const float boxhalfsize[3],
                            const float (*triverts)[9], // triverts[N][9]
                            const size_t N);
