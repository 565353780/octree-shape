#pragma once

#include <iostream>

void outputOMPSetting();

int isMeshBoxOverlap(const float boxcenter[3], const float boxhalfsize[3],
                     const float (*triverts)[9], // triverts[N][9]
                     size_t N);
