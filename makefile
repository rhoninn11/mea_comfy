


dkr_bld:
	cd docker && docker build -t rhoninn11/comfy_docker:v3 .

dkr_run:
	cd docker && docker compose up

dkr_shell:
	cd docker && docker exec -it comfy_no_0 bash

mea_comfy_models:
	cd other && python download.py
