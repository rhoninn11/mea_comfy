from grpc_tools import protoc
import os

# add to os path
def proto_gen(in_dir, out_dir):
    ls = os.listdir(in_dir)
    protofiles = []
    for file in ls:
        if file.endswith(".proto"):
            proto_file = os.path.join(in_dir, file)
            protofiles.append(proto_file)
    
    os.makedirs(out_dir, exist_ok=True)
    for proto_file in protofiles:
        protoc.main((
            "",
            f"-I{in_dir}",
            f"--python_out={out_dir}",
            f"--pyi_out={out_dir}",
            f"--grpc_python_out={out_dir}",
            proto_file,
        ))


def script():
    IN_DIR="./proto"
    OUT_DIR="./src/proto"
    proto_gen(IN_DIR, OUT_DIR)
    print("+++ proto sources regenerated")

script()