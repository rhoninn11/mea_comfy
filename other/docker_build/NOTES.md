docker build --progress=plain --no-cache -t rhoninn11/comfy_docker:v1 .
docker build -t rhoninn11/comfy_docker:v1 .
docker push rhoninn11/comfy_docker:v1
docker exec -it first_gpu_instance sh


docker flux fp8 20 steps torch 2.1 ~32sec 1.4s/step - docker - RTX 3090
docker flux fp8 20 steps torch 2.2 ~28sec 1.38s/step - docker - RTX 3090
docker flux fp8 20 steps torch 2.4 ~28sec 1.38s/step - docker - RTX 3090
docker flux fp8 20 steps torch 2.4 ~31sec 1.51s/step - native - RTX 3090