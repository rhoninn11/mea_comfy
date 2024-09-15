
# Mea comfy wrap

Simple script for wraping comfy ui workflows for future usage as a micro services with gRPC interface

![image from assets](assets/inpaint_steps.png)

#### setting environment:
```
pip install -r req.txt
python proto_gen.py
```
/not all dependencies added yet into req.txt

#### Start one of scripts using:
```
python main.py 
```

### +++ Help +++
```
usage: main.py [-h] [-demo] [-server] [-client]

comfy ui workflow run

options:
  -h, --help  show this help message and exit
  -demo       run demo script for comfy ui inpaint
  -server     start grpc for comfy ui inpaint
  -client     start grpc client for comfy ui inpaint
```

### +++ That might be helpful for me +++
```
conda install pytorch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 pytorch-cuda=11.8 -c pytorch -c nvidia -y

```

