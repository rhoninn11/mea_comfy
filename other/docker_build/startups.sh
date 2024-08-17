cd /workspace
git clone https://github.com/comfyanonymous/ComfyUI.git
mv ComfyUI comfy_ui
cd comfy_ui/custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
cd /workspace/comfy_ui
pip install -r requirements.txt
