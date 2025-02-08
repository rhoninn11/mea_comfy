

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

gen_proto: 
	python proto/proto_gen.py

python_llm:
	python main.py -llm
