UV_VER="0.9.1"
PY_VER="3.11"
uv_install() {
    SCRIPT="uv-installer.sh"
    wget https://github.com/astral-sh/uv/releases/download/${UV_VER}/${SCRIPT}
    chmod +x ${SCRIPT}
    ./${SCRIPT}
}

uv_venv() {
    uv venv ${VENV_DIR} --python ${PY_VER}
    echo source $VENV_DIR/bin/activate >> /root/.bashrc
    # echo alias 'pip="uv pip"' >> /root/.bashrc
}

VENV_DIR="/venv_global"
pip_install_heavy() {
    echo lol
    pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu126
    pip install einops
    pip install torchsde
}


