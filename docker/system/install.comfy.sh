#!/bin/bash

COMFY_VER="v0.2.3"
COMFY_REPO="https://github.com/comfyanonymous/ComfyUI.git"

COMFY_MNG_VER="2.50.1"
COMFY_MNG_REPO="https://github.com/ltdrdata/ComfyUI-Manager.git"

COMFY_SCRIPT_VER="v0.5.1"
COMFY_SCRIPT_REPO="https://github.com/Chaoses-Ib/ComfyScript.git"

IPADAPTERS_REPO="https://github.com/cubiq/ComfyUI_IPAdapter_plus.git"

install_comfy() {
    
    if [ ! -d "$DIR_COMFY_UI" ]; then
        echo "Cloning ComfyUI..."
        git clone --branch $COMFY_VER --single-branch $COMFY_REPO $DIR_COMFY_UI 
    fi

    DIR_PLUGINS="$DIR_COMFY_UI/custom_nodes"

    NAME="ComfyUI-Manager"
    MANAGER_DIR="$DIR_PLUGINS/$NAME"
    if [ ! -d "$MANAGER_DIR" ]; then
        echo "Cloning $NAME..."
        git clone --branch $COMFY_MNG_VER --single-branch $COMFY_MNG_REPO $MANAGER_DIR
    fi

    NAME="ComfyScript"
    CSCRIPT_DIR="$DIR_PLUGINS/$NAME"
    if [ ! -d "$CSCRIPT_DIR" ]; then
        echo "Cloning $NAME..."
        git clone --branch $COMFY_SCRIPT_VER --single-branch $COMFY_SCRIPT_REPO $CSCRIPT_DIR
    fi
    
    NAME="ComfyUI_IPAdapter_plus"
    ADAPTER_DIR="$DIR_PLUGINS/$NAME"
    if [ ! -d "$ADAPTER_DIR" ]; then
        echo "Cloning $NAME..."
        git clone --single-branch $IPADAPTERS_REPO $ADAPTER_DIR
    fi

    # ComfyUI_essentials...
    # ComfyUI_brushnet
    # but mayby comfyUi manager can install all of this shit...


    cd $COMFY_UI_DIR
    pip install -r requirements.txt
    cd $MANAGER_DIR
    pip install -r requirements.txt
    cd $ADAPTER_DIR
    pip install -r requirements.txt
    cd $CSCRIPT_DIR
    python -m pip install -e ".[default]"
    pip install --upgrade transformers==4.45.0
    pip install --upgrade numpy==1.26.4
    pip install --upgrade peft==0.15.0
    pip install --upgrade accelerate==0.29.0
    pip install --upgrade diffusers==0.29.0

    cd $ADAPTER_DIR
    python cm_cli.py install ComfyUI_essentials
    python cm_cli.py install ComfyUI-Custom-Scripts
    # python cm_cli.py install ComfyUI_Brushnet
    #       trzeba będzie mu cofnąć commita
    # python cm_cli.py install comfyui_controlnet_aux

    echo "+++ ComfyUI setup finished"
    pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu126
    pip install einops
    pip install torchsde
    # pip install torchvision
    # pip install einops
    # pip install torchsde

}