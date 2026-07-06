

UV_VER="0.9.1"
install() {
    SCRIPT="uv-installer.sh"
    wget https://github.com/astral-sh/uv/releases/download/${UV_VER}/${SCRIPT}
    chmod +x ${SCRIPT}
    ./${SCRIPT}
}

DEF_PY_VER="3.11"
VENV_DIR="/uv_glob_env"
uv_venv() {
    uv venv ${VENV_DIR} --python ${DEF_PY_VER}
    echo source $VENV_DIR/bin/activate >> /root/.bashrc
    # echo alias 'pip="uv pip"' >> /root/.bashrc
}

# use like: global_venv global 3.12
global_venv() {
    INIT_IN="${HOME}/.bashrc"
    DIR=$1
    VER_PARAM=$DEF_PY_VER
    if [ -z "$VER_PARAM"]; then
        VER_PARAM=$DEF_PY_VER
    fi
    mkdir -p ${DIR}
    uv venv ${DIR} --python ${VER_PARAM}
    echo source ${DIR}/bin/activate >> ${INIT_IN}
    echo 'alias pip="uv pip"' >> ${INIT_IN}
    echo 'alias python="python3"' >> ${INIT_IN}
}