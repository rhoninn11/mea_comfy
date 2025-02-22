#!/bin/bash

COMFY_VER="v0.2.3"
COMFY_REPO="https://github.com/comfyanonymous/ComfyUI.git"

COMFY_MNG_VER="2.50.1"
COMFY_MNG_REPO="https://github.com/ltdrdata/ComfyUI-Manager.git"

COMFY_SCRIPT_VER="v0.5.1"
COMFY_SCRIPT_REPO="https://github.com/Chaoses-Ib/ComfyScript.git"

IPADAPTERS_REPO="https://github.com/cubiq/ComfyUI_IPAdapter_plus.git"

setup_comfy_ui() {
    PROJ_DIR="$PROJ_ROOT"
    echo +++ PROJ_ROOT at $PROJ_DIR

    # TODO: that should be readed from env
    COMFY_DIR="$PROJ_DIR/comfy_ui"
    echo export COMFY="$COMFY_DIR" >> /etc/mea_env
    
    PLUGIN_DIR="$COMFY_DIR/custom_nodes"
    
    if [ ! -d "$COMFY_DIR" ]; then
        echo "Cloning ComfyUI..."
        cd $PROJ_DIR
        git clone --branch $COMFY_VER --single-branch $COMFY_REPO
        mv ComfyUI comfy_ui
    fi

    cd $PLUGIN_DIR

    NAME="ComfyUI-Manager"
    MANAGER_DIR="$PLUGIN_DIR/$NAME"
    if [ ! -d "$MANAGER_DIR" ]; then
        echo "Cloning $NAME..."
        git clone --branch $COMFY_MNG_VER --single-branch $COMFY_MNG_REPO
    fi

    NAME="ComfyScript"
    CSCRIPT_DIR="$PLUGIN_DIR/$NAME"
    if [ ! -d "$CSCRIPT_DIR" ]; then
        echo "Cloning $NAME..."
        git clone --branch $COMFY_SCRIPT_VER --single-branch $COMFY_SCRIPT_REPO
    fi
    

    NAME="ComfyUI_IPAdapter_plus"
    ADAPTER_DIR="$PLUGIN_DIR/$NAME"
    if [ ! -d "$ADAPTER_DIR" ]; then
        echo "Cloning $NAME..."
        git clone --single-branch $IPADAPTERS_REPO
    fi


    cd $COMFY_DIR
    pip install -r requirements.txt
    cd $MANAGER_DIR
    pip install -r requirements.txt
    cd $ADAPTER_DIR
    pip install -r requirements.txt
    cd $CSCRIPT_DIR
    python -m pip install -e ".[default]"
    pip install --upgrade transformers==4.45.0
    pip install --upgrade numpy=1.26.4

    echo "+++ ComfyUI setup finished"

}

setup_comfy_ui