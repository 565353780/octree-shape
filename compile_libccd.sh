mkdir ../octree-shape/octree_shape/Lib
cd ../octree-shape/octree_shape/Lib

git clone https://github.com/danfis/libccd.git

export CC=$(which gcc)
export CXX=$(which g++)
echo "Using CC: $CC"
echo "Using CXX: $CXX"

cd libccd
rm -rf build
mkdir build && cd build

cmake .. \
  -G "Unix Makefiles" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=./install

make -j
make install
