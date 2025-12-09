
img_name = "img_mea_comfy"
proj_name = "mea_comfy_compose"


build:
	docker build -t $(img_name) .
# 	docker build --progress=plain -t img_mea_comfy .
# 	docker build --no-cache img_mea_comfy_docker .
# 	cd docker && docker compose up
# 	cd docker && docker exec -it comfy_no_0 bash --login

devel_up:
	docker compose -p mea_comfy_compose -f compose.devel.yaml up

up:
	docker compose -p mea_comfy_compose -f compose.yaml up

down:
	docker compose -p mea_comfy_compose down

bash:
	docker exec -it c_mea_comfy "/bin/bash" "-l"