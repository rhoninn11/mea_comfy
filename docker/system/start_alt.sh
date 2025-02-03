
start_comfy_ui() {
    echo "Starting ComfyUI..."
    COMFY_UI_DIR="/mea/comfy_ui"
    cd $COMFY_UI_DIR
    python main.py --listen --port 8188
}

start_comfy_mea() {
    COMFY_MEA="/mea/mea_comfy"
    cd $COMFY_MEA
    python main.py -server
}

start_ollama() {    
    export OLLAMA_HOST="0.0.0.0:11434"
    ollama serve
    # on port 11434
}


# start_comfy_ui
start_comfy_mea
# start_ollama