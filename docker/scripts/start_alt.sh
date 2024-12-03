
start_comfy_ui() {
    echo "Starting ComfyUI..."
    COMFY_UI_DIR="/mea/comfy_ui"
    cd $COMFY_UI_DIR
    python main.py --listen --port 8188
}

start_ollama() {
    ollama serve
    # on port 11434
}


start_comfy_ui
# start_ollama