#!/bin/bash

COMFY_VER="v0.2.3"
COMFY_REPO="https://github.com/comfyanonymous/ComfyUI.git"

COMFY_MNG_VER="2.50.1"
COMFY_MNG_REPO="https://github.com/ltdrdata/ComfyUI-Manager.git"

setup_comfy_ui() {
    PROJ_DIR="/mea"

    COMFY_DIR="$PROJ_DIR/comfy_ui"
    echo export COMFY="$COMFY_DIR" >> /etc/mea_env
    PLUGIN_DIR="$COMFY_DIR/custom_nodes"
    MANAGER_DIR="$CUSTOM_NODE_DIR/ComfyUI-Manager"

    if [ ! -d "$COMFY_DIR" ]; then
        echo "Cloning ComfyUI..."
        cd $PROJ_DIR
        git clone --branch $COMFY_VER --single-branch $COMFY_REPO
        mv ComfyUI comfy_ui
    fi

    cd $PLUGIN_DIR

    # if dir empty
    if [ ! -d "$MANAGER_DIR" ]; then
        echo "Cloning ComfyUI-Manager..."
        git clone --branch $COMFY_MNG_VER --single-branch $COMFY_MNG_REPO
    fi

    cd $COMFY_DIR
    pip install -r requirements.txt
    cd $MANAGER_DIR
    pip install -r requirements.txt
    echo "+++ ComfyUI setup finished"

}

setup_comfy_ui