#!/bin/bash

COMFY_VER="v0.2.3"
COMFY_REPO="https://github.com/comfyanonymous/ComfyUI.git"

COMFY_MNG_VER="2.50.1"
COMFY_MNG_REPO="https://github.com/ltdrdata/ComfyUI-Manager.git"

setup_comfy_ui() {
    COMFY_UI_DIR="/workspace/comfy_ui"
    CUSTOM_NODE_DIR="$COMFY_UI_DIR/custom_nodes"
    MANAGER_DIR="$CUSTOM_NODE_DIR/ComfyUI-Manager"
    # if dir not exists
    if [ ! -d "$COMFY_UI_DIR" ]; then
        echo "Cloning ComfyUI..."
        cd /workspace
        git clone --branch $COMFY_VER --single-branch $COMFY_REPO
        mv ComfyUI comfy_ui
    fi

    cd $CUSTOM_NODE_DIR

    # if dir empty
    if [ ! -d "$MANAGER_DIR" ]; then
        echo "Cloning ComfyUI-Manager..."
        git clone --branch $COMFY_MNG_VER --single-branch $COMFY_MNG_REPO
    fi

    cd $COMFY_UI_DIR
    pip install -r requirements.txt
    cd $MANAGER_DIR
    pip install -r requirements.txt
    echo "+++ ComfyUI setup finished"
}

setup_comfy_ui