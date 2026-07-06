

export CMAKE_VER="3.30.1"
install () {
    wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VER}/cmake-${CMAKE_VER}.tar.gz
    tar xfvz cmake-${CMAKE_VER}.tar.gz
    cd cmake-${CMAKE_VER}
    mkdir build && cd build
    cmake .. -GNinja
    ninja && ninja install
}