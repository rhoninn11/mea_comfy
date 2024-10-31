docker build --progress=plain --no-cache -t rhoninn11/comfy_docker:v2 .
docker build -t rhoninn11/comfy_docker:v2 .
docker push rhoninn11/comfy_docker:v2
docker exec -it comfy_no_0 bash
docker container rm comfy_no_0


docker flux fp8 20 steps torch 2.1 ~32sec 1.4s/step - docker - RTX 3090
docker flux fp8 20 steps torch 2.2 ~28sec 1.38s/step - docker - RTX 3090
docker flux fp8 20 steps torch 2.4 ~28sec 1.38s/step - docker - RTX 3090
docker flux fp8 20 steps torch 2.4 ~31sec 1.51s/step - native - RTX 3090
docker flux fp8 20 steps torch 2.4 ~26sec 1.26s/step - docker(runpod) - RTX 3090
docker flux fp8 20 steps torch 2.4 ~16sec 0.79s/step - docker(runpod) - A6000
docker flux fp8 20 steps torch 2.4 ~13sec 0.63s/step - docker(runpod) - RTX 4090
docker flux fp8 20 steps torch 2.4 ~8sec 0.42s/step - docker - A100 SMX
