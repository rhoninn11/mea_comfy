
start_comfy_ui() {
    cd $DIR_COMFY_UI
    pip install -r requirements.txt
    pip install dynaconf
    python main.py --listen --port 8189
}

start_mea_comfy() {
    cd $DIR_COMFY_UI
    pip install -r requirements.txt
    pip install dynaconf
    cd $DIR_MEA_COMFY
    make mea_server
}

start_ollama() {    
    export OLLAMA_HOST="0.0.0.0:11434"
    ollama serve
}