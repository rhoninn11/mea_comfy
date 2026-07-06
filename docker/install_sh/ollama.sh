


OLLAMA_VER="v0.6.2"
install() {
    PKG="ollama-linux-amd64.tgz"
    INSTALL_FROM="https://github.com/ollama/ollama/releases/download/${OLLAMA_VER}/${PKG}"
    TMP_LOC="/tmp/$PKG"
    curl --progress-bar -L $INSTALL_FROM -o $TMP_LOC
    tar --directory=/usr -xzf $TMP_LOC
    rm $TMP_LOC
    mkdir -p /var/ollama_models
}

run() {
    export OLLAMA_HOST="0.0.0.0:11434"
    export OLLAMA_MODELS="/var/ollama_models"
    ollama serve
}