
import safetensors as sft
import os


def ensure_path_exist(path):
    if os.path.exists(path):
        os.makedirs(path, exist_ok=True)

tmp = "tmp"
ensure_path_exist(tmp)


comfy_path = os.getenv('COMFY')
if comfy_path is None:
    print("!!! path to ComfyUI must be set in env variable 'COMFY'")
    exit()


models = "models/checkpoints"
comfy_cpkt = os.path.join(comfy_path,models)

ls: list[str] = os.listdir(comfy_cpkt)
ls = list(filter(lambda s: s.find("flux") >= 0, ls))

for i, item in enumerate(ls):
    model_file = os.path.join(comfy_cpkt, item)
    model = sft.safe_open(model_file, framework="pt")

    report_lines = []
    tensor_list = list(model.keys())
    for name in tensor_list:
        pt_tensor = model.get_tensor(name)
        line = f"{name:<100} shape: {str(pt_tensor.shape)}\n"
        report_lines.append(line)

    name = item.split(".")[:-1]
    
    save_info = open(os.path.join(tmp,f"{name}.txt"), "w")
    save_info.writelines(report_lines)
    save_info.close()


