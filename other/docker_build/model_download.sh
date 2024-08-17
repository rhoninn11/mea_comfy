
download_xl() {
    MODEL_URL="https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0_0.9vae.safetensors"
    MODEL_FILE="sd_xl_base_1.0_0.9vae.safetensors"
    
    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/checkpoints"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_FILE}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_FILE} already exists"
        return
    fi

    cd $COMFY_UI_MODEL_DIR
    wget $MODEL_URL
    echo "+++ ${MODEL_FILE} downloaded" 
    return
}

download_xl_inpaint() {
    MODEL_URL="https://huggingface.co/diffusers/stable-diffusion-xl-1.0-inpainting-0.1/resolve/main/unet/diffusion_pytorch_model.fp16.safetensors"
    MODEL_FILE="sd_xl_1.0_inpaint.safetensors"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/unet"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_FILE}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_FILE} already exists"
        return
    fi
    
    cd $COMFY_UI_MODEL_DIR
    wget $MODEL_URL -O $MODEL_FILE
    echo "+++ ${MODEL_NAME} downloaded"
    return
}

download_clip_standard() {
    MODEL_NAME="CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"
    MODEL_URL="https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/clip_vision"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi
    mkdir -p $COMFY_UI_MODEL_DIR
    cd $COMFY_UI_MODEL_DIR
    wget $MODEL_URL
    mv model.safetensors $MODEL_NAME
    echo "+++ ${MODEL_NAME} downloaded"
    return
}

download_clip_xl() {
    MODEL_NAME="CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors"
    MODEL_URL="https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/model.safetensors"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/clip_vision"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi

    mkdir -p $COMFY_UI_MODEL_DIR
    cd $COMFY_UI_MODEL_DIR
    wget $MODEL_URL
    mv model.safetensors $MODEL_NAME
    echo "+++ ${MODEL_NAME} downloaded"
    return
}

downloadc_ipadapter_vit_h() {
    MODEL_NAME="ip-adapter_sdxl_vit-h.safetensors"
    MODEL_URL="https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/ipadapter"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi

    mkdir -p $COMFY_UI_MODEL_DIR
    cd $COMFY_UI_MODEL_DIR
    wget $MODEL_URL
    echo "+++ ${MODEL_NAME} downloaded"
    return
}

downloadc_ipadapter_plus_vit_h() {
    MODEL_NAME="ip-adapter-plus_sdxl_vit-h.safetensors"
    MODEL_URL="https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/ipadapter"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi

    mkdir -p $COMFY_UI_MODEL_DIR
    cd $COMFY_UI_MODEL_DIR
    wget $MODEL_URL
    echo "+++ ${MODEL_NAME} downloaded"
    return
}

downloadc_ipadapter_plus_face_vit_h() {
    MODEL_NAME="ip-adapter-plus-face_sdxl_vit-h.safetensors"
    MODEL_URL="https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus-face_sdxl_vit-h.safetensors"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/ipadapter"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi

    mkdir -p $COMFY_UI_MODEL_DIR
    cd $COMFY_UI_MODEL_DIR
    wget $MODEL_URL
    echo "+++ ${MODEL_NAME} downloaded"
    return
}

downloadc_ipadapter_composition() {
    MODEL_NAME="ip_plus_composition_sdxl.safetensors"
    MODEL_URL="https://huggingface.co/ostris/ip-composition-adapter/resolve/main/ip_plus_composition_sdxl.safetensors"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/ipadapter"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi

    mkdir -p $COMFY_UI_MODEL_DIR
    cd $COMFY_UI_MODEL_DIR
    wget $MODEL_URL
    echo "+++ ${MODEL_NAME} downloaded"
    return
}

# loras hugging face
download_lora_hyper_2_step() {

    MODEL_NAME="Hyper-SDXL-2steps-lora.safetensors"
    MODEL_URL="https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SDXL-2steps-lora.safetensors"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/loras"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi

    cd $COMFY_UI_MODEL_DIR
    wget $MODEL_URL
    echo "+++ ${MODEL_NAME} downloaded"
    return
}

download_lora_hyper_4_step() {

    MODEL_NAME="Hyper-SDXL-4steps-lora.safetensors"
    MODEL_URL="https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SDXL-4steps-lora.safetensors"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/loras"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi

    cd $COMFY_UI_MODEL_DIR
    wget $MODEL_URL
    echo "+++ ${MODEL_NAME} downloaded"
    return
}

download_lora_hyper_12_step() {

    MODEL_NAME="Hyper-SDXL-12steps-CFG-lora.safetensors"
    MODEL_URL="https://huggingface.co/ByteDance/Hyper-SD/resolve/main/Hyper-SDXL-12steps-CFG-lora.safetensors"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/loras"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi

    cd $COMFY_UI_MODEL_DIR
    wget $MODEL_URL
    echo "+++ ${MODEL_NAME} downloaded"
    return
}

download_lora_noise_offset() {

    MODEL_NAME="sd_xl_offset_example-lora_1.0.safetensors"
    MODEL_URL="https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_offset_example-lora_1.0.safetensors"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/loras"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi

    cd $COMFY_UI_MODEL_DIR
    wget $MODEL_URL
    echo "+++ ${MODEL_NAME} downloaded"
    return
}


# loras civit
download_lora_cube() {
    MODEL_NAME="Cube_Shaped_Anatomy.safetensors"
    MODEL_FILE_WITH_CMD="/wget_links/lora_cube.txt"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/loras"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi

    cd $COMFY_UI_MODEL_DIR
    CMD=$(cat $MODEL_FILE_WITH_CMD)
    {
        source /dev/stdin <<< $CMD
    } || {
        echo "!!! ${MODEL_NAME} download failed"
        rm $MODEL_PATH
        return
    }
    echo "+++ ${MODEL_NAME} downloaded"
}

download_lora_vintage_comic_book() {
    MODEL_NAME="wizards_vintage_comics-Undergroundf16.safetensors"
    MODEL_FILE_WITH_CMD="/wget_links/lora_vintage_comic_book.txt"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/loras"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi

    cd $COMFY_UI_MODEL_DIR
    CMD=$(cat $MODEL_FILE_WITH_CMD)
    {
        source /dev/stdin <<< $CMD
    } || {
        echo "!!! ${MODEL_NAME} download failed"
        rm $MODEL_PATH
        return
    }
    echo "+++ ${MODEL_NAME} downloaded"
}

download_lora_ms_paint() {
    MODEL_NAME="SDXL_MSPaint_Portrait.safetensors"
    MODEL_FILE_WITH_CMD="/wget_links/lora_ms_paint.txt"

    COMFY_UI_MODEL_DIR="/workspace/comfy_ui/models/loras"
    MODEL_PATH="${COMFY_UI_MODEL_DIR}/${MODEL_NAME}"

    if [ -f "$MODEL_PATH" ]; then
        echo "+++ ${MODEL_NAME} already exists"
        return
    fi

    cd $COMFY_UI_MODEL_DIR
    CMD=$(cat $MODEL_FILE_WITH_CMD)
    {
        source /dev/stdin <<< $CMD
    } || {
        echo "!!! ${MODEL_NAME} download failed"
        rm $MODEL_PATH
        return
    }
    echo "+++ ${MODEL_NAME} downloaded"
}