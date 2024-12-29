#!/bin/bash

MEA_REPO="https://github.com/rhoninn11/mea_comfy_wrap.git"
REPO_NAME="mea_comfy_wrap"


setup_mea() {
    PROJ_DIR="/mea"
    MEA_DIR="$PROJ_DIR/$REPO_NAME"
    
    # if dir not exists
    if [ ! -d "$MEA_DIR" ]; then
        echo "Cloning $REPO_NAME..."
        cd $PROJ_DIR
        git clone $MEA_REPO
        cd $MEA_DIR
        # meaby some scripcts eventualy
    fi

}

setup_mea