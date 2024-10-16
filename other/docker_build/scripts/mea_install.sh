#!/bin/bash

MEA_REPO="https://github.com/rhoninn11/mea_comfy_wrap.git"
REPO_NAME="mea_comfy_wrap"


setup_mea() {
    MEA_DIR="/workspace"
    # if dir not exists
    if [ ! -d "$COMFY_UI_DIR" ]; then
        echo "Cloning ComfyUI..."
        cd $MEA_DIR
        # git clone --branch $COMFY_VER --single-branch $COMFY_REPO
        git clone $MEA_REPO

    fi

    cd $CUSTOM_NODE_DIR


}

setup_mea