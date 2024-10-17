docker build --progress=plain --no-cache -t rhoninn11/comfy_docker:v1 .
docker build -t rhoninn11/comfy_docker:v1 .
docker push rhoninn11/comfy_docker:v1
docker exec -it first_gpu_instance sh