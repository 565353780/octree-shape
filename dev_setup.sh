cd ..
git clone git@github.com:565353780/data-convert.git

cd data-convert
./dev_setup.sh

cd ../octree-shape

pip install -U numpy trimesh

pip3 install -U torch torchvision \
  --index-url https://download.pytorch.org/whl/cu124

./compile.sh
