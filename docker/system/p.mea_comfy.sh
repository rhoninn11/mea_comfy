#!/bin/bash

MEA_REPO="https://github.com/rhoninn11/mea_comfy.git"
REPO_NAME="mea_comfy"

install_mea_comfy() {
    PROJ_DIR="/mea"
    MEA_DIR="$PROJ_DIR/$REPO_NAME"
    
    # if dir not exists
    if [ ! -d "$MEA_DIR" ]; then
        cd $PROJ_DIR
        echo "Cloning $REPO_NAME..."
        git clone $MEA_REPO
        cd $MEA_DIR
        git submodule update --init --recursive
        pip install -r requirements.txt
        python proto/proto_gen.py
    fi
}