docker build --progress=plain --no-cache -t rhoninn11/comfy_docker:v2 .
docker build -t rhoninn11/comfy_docker:v2 .
docker push rhoninn11/comfy_docker:v2
docker exec -it comfy_no_0 bash
docker container rm comfy_no_0


