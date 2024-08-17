#!/bin/bash
set -e  # Exit the script if any statement returns a non-true return value

# ---------------------------------------------------------------------------- #
#                          Function Definitions                                #
# ---------------------------------------------------------------------------- #

# Start nginx service
start_nginx() {
    echo "Starting Nginx service..."
    service nginx start
}

# Execute script if exists
execute_script() {
    local script_path=$1
    local script_msg=$2
    if [[ -f ${script_path} ]]; then
        echo "${script_msg}"
        bash ${script_path}
    fi
}

# Setup ssh
setup_ssh() {
    if [[ $PUBLIC_KEY ]]; then
        echo "Setting up SSH..."
        mkdir -p ~/.ssh
        echo "$PUBLIC_KEY" >> ~/.ssh/authorized_keys
        chmod 700 -R ~/.ssh

        if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
            ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -q -N ''
        fi

        if [ ! -f /etc/ssh/ssh_host_dsa_key ]; then
            ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key -q -N ''
        fi

        if [ ! -f /etc/ssh/ssh_host_ecdsa_key ]; then
            ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -q -N ''
        fi

        if [ ! -f /etc/ssh/ssh_host_ed25519_key ]; then
            ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -q -N ''
        fi

        service ssh start

        echo "SSH host keys:"
        cat /etc/ssh/*.pub
    fi
}

# Export env vars
export_env_vars() {
    echo "Exporting environment variables..."
    printenv | grep -E '^RUNPOD_|^PATH=|^_=' | awk -F = '{ print "export " $1 "=\"" $2 "\"" }' >> /etc/rp_environment
    echo 'source /etc/rp_environment' >> ~/.bashrc
}

# Start jupyter lab
start_jupyter() {
    if [[ $JUPYTER_PASSWORD ]]; then
        echo "Starting Jupyter Lab..."
        mkdir -p /workspace && \
        cd / && \
        nohup jupyter lab --allow-root --no-browser --port=8888 --ip=* --FileContentsManager.delete_to_trash=False --ServerApp.terminado_settings='{"shell_command":["/bin/bash"]}' --ServerApp.token=$JUPYTER_PASSWORD --ServerApp.allow_origin=* --ServerApp.preferred_dir=/workspace &> /jupyter.log &
        echo "Jupyter Lab started"
    fi
}

setup_comfy_ui() {
    COMFY_UI_DIR="/workspace/comfy_ui"
    CUSTOM_NODE_DIR="$COMFY_UI_DIR/custom_nodes"
    MANAGER_DIR="$CUSTOM_NODE_DIR/ComfyUI-Manager"
    # if dir not exists
    if [ ! -d "$COMFY_UI_DIR" ]; then
        echo "Cloning ComfyUI..."
        cd /workspace
        git clone https://github.com/comfyanonymous/ComfyUI.git
        mv ComfyUI comfy_ui
    fi

    cd $CUSTOM_NODE_DIR

    # if dir empty
    if [ ! -d "$MANAGER_DIR" ]; then
        echo "Cloning ComfyUI-Manager..."
        git clone https://github.com/ltdrdata/ComfyUI-Manager.git
    fi

    cd $COMFY_UI_DIR
    pip install -r requirements.txt
    cd $MANAGER_DIR
    pip install -r requirements.txt
    echo "+++ ComfyUI setup finished"
}

start_comfy_ui() {
    COMFY_UI_DIR="/workspace/comfy_ui"
    cd $COMFY_UI_DIR
    nohup python main.py --listen --port 8188 &> /comfy_ui_nohup.log &
}

install_basic_tools() {
    apt-get update
    apt-get install vim -y
}

download_act_I_models() {
    source "/script_src/model_download.sh"
    download_xl
    download_xl_inpaint
}

download_act_II_models() {
    source "/script_src/model_download.sh"
    download_clip_standard
    downloadc_ipadapter_vit_h
    downloadc_ipadapter_plus_vit_h
    downloadc_ipadapter_plus_face_vit_h
    downloadc_ipadapter_composition
}

download_act_II_loras() {
    source "/script_src/model_download.sh"
    # utilitarian
    download_lora_hyper_2_step
    download_lora_hyper_4_step
    download_lora_hyper_12_step
    download_lora_noise_offset

    # conceptual
    download_lora_cube
    download_lora_vintage_comic_book
    download_lora_ms_paint
}

restore_snapshot() {
    SNAPSHOT_NAME="baseline_snapshot.json"
    SNAPSHOT_DIR="/workspace/comfy_ui/custom_nodes/ComfyUI-Manager/snapshots"
    SNAPSHOT_SRC="/${SNAPSHOT_NAME}"
    SNAPSHOT_DST="${SNAPSHOT_DIR}/${SNAPSHOT_NAME}"

    CM_CLI="/workspace/comfy_ui/custom_nodes/ComfyUI-Manager/cm-cli.py"

    if [ -f "${SNAPSHOT_DST}" ]; then
        echo "+++ ${SNAPSHOT_NAME} already restored"
        return
    fi

    cp $SNAPSHOT_SRC $SNAPSHOT_DST
    python $CM_CLI restore-snapshot $SNAPSHOT_NAME
    echo "+++ ${SNAPSHOT_NAME} restored"
    return
}

# ---------------------------------------------------------------------------- #
#                               Main Program                                   #
# ---------------------------------------------------------------------------- #

start_nginx

execute_script "/pre_start.sh" "Running pre-start script..."

echo "Pod Started"
echo "custom echo message for comfy_ui"

install_basic_tools

setup_ssh
setup_comfy_ui
download_act_I_models
download_act_II_models
download_act_II_loras
restore_snapshot

start_comfy_ui
start_jupyter
export_env_vars

export COMFY="/workspace/ComfyUI"

execute_script "/post_start.sh" "Running post-start script..."

echo "Start script(s) finished, pod is ready to use."
sleep 10s
jupyter server list

sleep infinity