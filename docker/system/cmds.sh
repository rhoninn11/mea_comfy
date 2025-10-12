
start_comfy_ui() {
    echo "Starting ComfyUI..."
    COMFY_UI_DIR="/mea/comfy_ui"
    cd $COMFY_UI_DIR
    python main.py --listen --port 8188
}

start_mea_comfy() {
    echo "+++ Starting mea_comfy from compose_up"
    echo "+++ some edits"
    cd $MEA_COMFY_DIR
    make mea_server
}

start_ollama() {    
    export OLLAMA_HOST="0.0.0.0:11434"
    ollama serve
}