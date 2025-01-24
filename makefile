


docker_build:
	cd docker && docker build -t rhoninn11/comfy_docker:v3 .

docker_run:
	cd docker && docker compose up

docker_shell:
	cd docker && docker exec -it comfy_no_0 bash

mea_comfy_models:
	python other/download.py

python_proto:
	python proto_gen.py

python_llm:
	python main.py -llm
