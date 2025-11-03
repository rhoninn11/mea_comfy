


install_python() {
    python -m pip install --upgrade pip
}

install_heavy_packages() {
    pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu126
    pip install einops
    pip install torchsde
}

VENV_DIR="${PROJ_DIR}/venv"
spawn_venv() {
    ln -s /usr/bin/python3 /usr/bin/python
    python -m venv ${VENV_DIR}
    echo source $VENV_DIR/bin/activate >> /root/.bashrc
}

