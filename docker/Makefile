

build:
	docker build -t img_mea_comfy .
# 	docker build --progress=plain -t img_mea_comfy .
# 	docker build --no-cache img_mea_comfy_docker .
# 	cd docker && docker compose up
# 	cd docker && docker exec -it comfy_no_0 bash --login

up_devel:
	docker compose -p mea_comfy_compose -f compose.devel.yaml up

up_service:
	docker compose -p mea_comfy_compose -f compose.service.yaml up

down:
	docker compose -p mea_comfy_compose down

shell:
	docker exec -it c_mea_comfy "/bin/bash" "-l"