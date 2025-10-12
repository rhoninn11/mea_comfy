

up:
	@echo "+++ go to ./docker/Makefile"
down:
	@echo "+++ go to ./docker/Makefile"
build:
	@echo "+++ go to ./docker/Makefile"
shell:
	@echo "+++ go to ./docker/Makefile"




install:
	pip install -r requirements.txt

models:
	python misc/download.py

protogen: 
	python proto/proto_gen.py

python_llm:
	python main.py -llm

mea_client:
	python main.py -client

mea_server:
	python main.py -server

mea_server_docker:
	cd docker && docker exec -it comfy_no_0 bash --login -c "start_mea_comfy"
conda_env:
# meaby shoud assume a starndard name conda env compatible across multiple proj
	conda activate comfy_ui

sleep:
	sleep 1800

