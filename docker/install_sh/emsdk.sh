EMSDK_VER="4.0.0"
install() {
    git clone https://github.com/emscripten-core/emsdk.git \
    --depth 1 --branch ${EMSDK_VER} /opt/emsdk

    cd /opt/emsdk
    ./emsdk install ${EMSDK_VER}
    ./emsdk activate ${EMSDK_VER}
    chmod -R 777 /opt/emsdk/upstream/emscripten/cache
    echo "source /opt/emsdk/emsdk_env.sh" >/etc/profile.d/emsdk.sh
}
