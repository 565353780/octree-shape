mkdir ../octree-shape/octree_shape/Lib
cd ../octree-shape/octree_shape/Lib

git clone https://github.com/embree/embree.git

cd embree
rm -rf build
mkdir build && cd build

export CC=$(which gcc)
export CXX=$(which g++)
echo "Using CC: $CC"
echo "Using CXX: $CXX"

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=./install \
  -DEMBREE_TUTORIALS=OFF \
  -DEMBREE_ISPC_SUPPORT=OFF \
  -DEMBREE_STATIC_LIB=OFF

make -j
make install

if [ -z "$CONDA_PREFIX" ]; then
  echo "❌ 没有检测到已激活的 Conda 环境。请先激活一个环境。"
  exit 1
fi

CONDA_LIB_DIR="$CONDA_PREFIX/lib"

OS=$(uname)
if [ "$OS" = "Darwin" ]; then
  TARGET_DYLIB_NAME="libembree4.4.dylib"
  SOURCE_EMBREE_LIB="../octree-shape/octree_shape/Lib/embree/build/install/lib/$TARGET_DYLIB_NAME"
elif [ "$OS" = "Linux" ]; then
  TARGET_DYLIB_NAME="libembree4.so.4"
  SOURCE_EMBREE_LIB="../octree-shape/octree_shape/Lib/embree/build/install/lib/$TARGET_DYLIB_NAME"
else
  echo "❌ 不支持的操作系统: $OS"
  exit 1
fi

if [ ! -f "$SOURCE_EMBREE_LIB" ]; then
  echo "❌ 找不到 Embree 动态库文件：$SOURCE_EMBREE_LIB"
  exit 1
fi

echo "🔄 正在复制 $TARGET_DYLIB_NAME 到 $CONDA_LIB_DIR ..."
cp "$SOURCE_EMBREE_LIB" "$CONDA_LIB_DIR"

if [ $? -eq 0 ]; then
  echo "✅ 成功复制 $TARGET_DYLIB_NAME 到 $CONDA_LIB_DIR"
else
  echo "❌ 复制失败，请检查权限或路径"
  exit 1
fi
