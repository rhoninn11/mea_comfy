
conf_local_libs() {
    echo /usr/local/lib >> /etc/ld.so.conf.d/local_libs.conf
}

OPENBLAS_VER="v0.3.30"
install_openblas() {
    git clone https://github.com/OpenMathLib/OpenBLAS.git --branch ${OPENBLAS_VER} --recursive --depth=1
    cd OpenBLAS && mkdir -p build && cd build
    cmake .. -GNinja \
        -DCMAKE_BUILD_TYPE=Release \
        -DINTERFACE64=1 \
        -DBUILD_SHARED_LIBS=ON \
        -DBUILD_LAPACK_DEPRECATED=OFF \
        -DCMAKE_INSTALL_PREFIX=/usr/local
    ninja && ninja install
}

SUITESPARSE_VER="v7.9.0"
install_suitesparse() {
    git clone https://github.com/DrTimothyAldenDavis/SuiteSparse.git --branch ${SUITESPARSE_VER} --recursive
    cd SuiteSparse && mkdir -p build && cd build
    cmake .. -GNinja \
        -DBLA_VENDOR=openblas \
        -DSUITESPARSE_CUDA_ARCHITECTURES=80 \
        -DBLAS_LIBRARIES=/usr/local/lib/libopenblas_64.so \
        -DLAPACK_LIBRARIES=/usr/local/lib/libopenblas_64.so \
        -DSUITESPARSE_USE_64BIT_BLAS=ON \
        -DCMAKE_INSTALL_PREFIX=/usr/local 
    ninja install
}
EIGEN_VER="5.0.0"
install_eigen() {
    git clone https://gitlab.com/libeigen/eigen.git --branch ${EIGEN_VER}
    cd eigen && mkdir build && cd build
    cmake .. -GNinja \
        -DEIGEN_CUDA_COMPUTE_ARCH=80 \
        -DCMAKE_INSTALL_PREFIX=/usr/local 
    ninja install
}
ABSEIL_VER="20250814.1"
install_abseil() {
    git clone https://github.com/abseil/abseil-cpp --branch ${ABSEIL_VER}
    cd abseil-cpp
    mkdir -p build && cd build
    cmake .. -GNinja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local
    ninja install
}


CERES_VER="master"
install_ceres() {
    git clone https://github.com/ceres-solver/ceres-solver.git --branch ${CERES_VER}
    cd ceres-solver
    git checkout f9b7b6651b108136a16df44d91fb31735645f5a7
    mkdir -p build && cd build
    cmake .. -GNinja \
        -DCMAKE_CUDA_ARCHITECTURES=80 \
        -DBLA_VENDOR=openblas \
        -DBLAS_LIBRARIES=/usr/local/lib/libopenblas_64.so \
        -DLAPACK_LIBRARIES=/usr/local/lib/libopenblas_64.so \
        -DBUILD_TESTING=OFF \
        -DCMAKE_INSTALL_PREFIX=/usr/local
        # -DEigen3_DIR=/usr/local/share/eigen3/cmake/Eigen3Config.cmake
    ninja install
}

POSELIB_VER="v2.0.5"
install_poselib() {
    git clone https://github.com/PoseLib/PoseLib --branch ${POSELIB_VER}
    cd PoseLib 
    sed -i 's/-Werror//g' CMakeLists.txt
    mkdir build && cd build
    cmake .. -GNinja \
        -DBUILD_SHARED_LIBS=ON \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DMARCH_NATIVE=ON
    ninja install
}

COLMAP_VER=3.13.0
install_colmap() {
    git clone https://github.com/colmap/colmap.git --branch ${COLMAP_VER}
    # git clone https://github.com/colmap/glomap.git --branch ${GLOMAP_VER}
    cd colmap
    # sed -i '1i#include <cassert>' src/colmap/sfm/observation_manager.cc
    mkdir -p build && cd build
    cmake .. -GNinja \
        -DFETCH_POSELIB=OFF \
        -DCMAKE_CUDA_ARCHITECTURES=native \
        -DGUI_ENABLED=OFF \
        -DBLA_VENDOR=openblas \
        -DBLAS_LIBRARIES=/usr/local/lib/libopenblas_64.so \
        -DLAPACK_LIBRARIES=/usr/local/lib/libopenblas_64.so \
        -DCMAKE_INSTALL_PREFIX=/usr/local
    ninja install
}


GLOMAP_VER=1.2.0
install_glomap() {
    git clone https://github.com/colmap/glomap.git --branch ${GLOMAP_VER} --recursive
    cd glomap 
    sed -i 's/find_package(Eigen3 3.4 REQUIRED)/find_package(Eigen3 5.0.0 REQUIRED)/' cmake/FindDependencies.cmake
    mkdir -p build && cd build
    cmake .. -GNinja \
        -DFETCH_POSELIB=OFF \
        -DFETCH_COLMAP=OFF \
        -DCMAKE_CUDA_ARCHITECTURES=80 \
        -DGUI_ENABLED=OFF \
        -DBLA_VENDOR=openblas \
        -DBLAS_LIBRARIES=/usr/local/lib/libopenblas_64.so \
        -DLAPACK_LIBRARIES=/usr/local/lib/libopenblas_64.so \
        -DCMAKE_INSTALL_PREFIX=/usr/local
    ninja install
}

install_all() {
    pushd $PWD && install_openblas && popd && ldconfig
    pushd $PWD && install_eigen && popd && ldconfig

    pushd $PWD && install_suitesparse && popd && ldconfig
    pushd $PWD && install_abseil && popd && ldconfig
    pushd $PWD && install_ceres && popd && ldconfig
    
    pushd $PWD && install_poselib && popd && ldconfig
    
    pushd $PWD && install_colmap && popd && ldconfig
    pushd $PWD && install_glomap && popd && ldconfig
}

