mkdir ../octree-shape/octree_shape/Lib
cd ../octree-shape/octree_shape/Lib

git clone https://github.com/embree/embree.git

cd embree
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

# 检查 conda 是否已激活
if [[ -z "$CONDA_PREFIX" ]]; then
  echo "❌ 没有检测到已激活的 Conda 环境。请先激活一个环境。"
  exit 1
fi

# 检测目标路径
CONDA_LIB_DIR="$CONDA_PREFIX/lib"
TARGET_DYLIB_NAME="libembree4.4.dylib"

# 你本地 embree 安装路径（请替换）
SOURCE_EMBREE_LIB="../octree-shape/octree_shape/Lib/embree/build/install/lib/$TARGET_DYLIB_NAME"

# 检查源文件是否存在
if [[ ! -f "$SOURCE_EMBREE_LIB" ]]; then
  echo "❌ 找不到 Embree dylib 文件：$SOURCE_EMBREE_LIB"
  exit 1
fi

# 复制 dylib 到 conda 的 lib 目录
echo "🔄 正在复制 $TARGET_DYLIB_NAME 到 $CONDA_LIB_DIR ..."
cp "$SOURCE_EMBREE_LIB" "$CONDA_LIB_DIR"

# 检查结果
if [[ $? -eq 0 ]]; then
  echo "✅ 成功复制 $TARGET_DYLIB_NAME 到 $CONDA_LIB_DIR"
else
  echo "❌ 复制失败，请检查权限或路径"
  exit 1
fi
