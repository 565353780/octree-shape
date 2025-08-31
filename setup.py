import os
import glob
import torch
from platform import system
from setuptools import find_packages, setup
from torch.utils.cpp_extension import CUDAExtension, CppExtension, BuildExtension

embree_include_dirs = [os.getcwd() + "/octree_shape/Lib/embree/build/install/include"]
embree_library_dirs = [os.getcwd() + "/octree_shape/Lib/embree/build/install/lib"]
embree_libraries = ["embree4"]

SYSTEM = system()

octree_root_path = os.getcwd() + "/octree_shape/Cpp/"
octree_src_path = octree_root_path + "src/"
octree_sources = glob.glob(octree_src_path + "*.cpp")
octree_include_dirs = [octree_root_path + "include"]

octree_extra_compile_args = [
    "-O3",
    "-DCMAKE_BUILD_TYPE=Release",
    "-D_GLIBCXX_USE_CXX11_ABI=0",
    "-DTORCH_USE_CUDA_DSA",
]

if SYSTEM == "Darwin":
    octree_extra_compile_args.append("-std=c++17")
elif SYSTEM == "Linux":
    octree_extra_compile_args.append("-std=c++17")

if torch.cuda.is_available():
    cc = torch.cuda.get_device_capability()
    arch_str = f"{cc[0]}.{cc[1]}"
    os.environ["TORCH_CUDA_ARCH_LIST"] = arch_str

    octree_sources += glob.glob(octree_src_path + "*.cu")

    extra_compile_args = {
        "cxx": octree_extra_compile_args
        + [
            "-DUSE_CUDA",
            "-DTORCH_USE_CUDA_DSA",
        ],
        "nvcc": [
            "-O3",
            "-Xfatbin",
            "-compress-all",
            "-DUSE_CUDA",
            "-std=c++17",
            "-DTORCH_USE_CUDA_DSA",
        ],
    }

    octree_module = CUDAExtension(
        name="octree_cpp",
        sources=octree_sources,
        include_dirs=octree_include_dirs + embree_include_dirs,
        library_dirs=embree_library_dirs,
        libraries=embree_libraries,
        extra_compile_args=extra_compile_args,
    )

else:
    octree_module = CppExtension(
        name="octree_cpp",
        sources=octree_sources,
        include_dirs=octree_include_dirs + embree_include_dirs,
        library_dirs=embree_library_dirs,
        libraries=embree_libraries,
        extra_compile_args=octree_extra_compile_args,
    )

setup(
    name="OCTREE-CPP",
    version="1.0.0",
    author="Changhao Li",
    packages=find_packages(),
    ext_modules=[octree_module],
    cmdclass={"build_ext": BuildExtension},
    include_package_data=True,
)
