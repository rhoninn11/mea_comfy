


install_python() {
    python -m pip install --upgrade pip
}

VENV_DIR="${PROJ_DIR}/venv"
spawn_venv() {
    ln -s /usr/bin/python3 /usr/bin/python
    python -m venv ${VENV_DIR}
    echo source $VENV_DIR/bin/activate >> /root/.bashrc
}

enter_venv() {
    source $VENV_DIR/bin/activate.sh
}