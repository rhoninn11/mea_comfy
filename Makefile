

rebuild_docker:
	cd docker && docker build --no-cache -t rhoninn11/comfy_docker:v3 .

build_docker:
	cd docker && docker build -t rhoninn11/comfy_docker:v3 .

run_docker:
	cd docker && docker compose up

shell_docker:
	cd docker && docker exec -it comfy_no_0 bash

mea_comfy_models:
	python other/download.py

protogen: 
	python proto/proto_gen.py

python_llm:
	python main.py -llm

client_py:
	python main.py -client

conda_env:
# meaby shoud assume a starndard name conda env compatible across multiple proj
	conda activate comfy_ui
