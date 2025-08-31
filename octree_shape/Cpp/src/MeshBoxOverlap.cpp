#include "MeshBoxOverlap.h"
#include "TriangleBoxOverlap.h"
#include <atomic>
#include <iostream>
#include <omp.h>

void outputOMPSetting() {
#pragma omp parallel
  {
#pragma omp critical
    {
      std::cout << "Thread " << omp_get_thread_num() << " / "
                << omp_get_num_threads() << " is active." << std::endl;
    }
  }
}

int isMeshBoxOverlap(const float boxcenter[3], const float boxhalfsize[3],
                     const float (*triverts)[9], // triverts[N][9]
                     size_t N) {
  std::atomic<bool> hit(false);

#pragma omp parallel for shared(hit)
  for (size_t i = 0; i < N; ++i) {
    // 提前终止检查
    if (hit.load(std::memory_order_relaxed))
      continue;

    const float (*tri)[3] = (const float (*)[3])triverts[i];

    if (triBoxOverlap(boxcenter, boxhalfsize, tri)) {
      hit.store(true, std::memory_order_relaxed);
      // 不能用 break；OpenMP 不能 break for 并行循环
    }
  }

  return hit.load() ? 1 : 0;
}
