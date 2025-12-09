# FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04
FROM debian:bookworm AS base

RUN apt update
RUN apt install -y \
    vim \
    git \
    curl \
    wget

RUN mkdir /mea
RUN echo alias python="python3" >> /etc/profile.d/mea.sh
RUN echo export PROJ_DIR="/mea" >> /etc/profile.d/mea.sh
RUN echo export DIR_COMFY_UI="/mea/comfy_ui" >> /etc/profile.d/mea.sh
RUN echo export DIR_MEA_COMFY="/mea/mea_comfy" >> /etc/profile.d/mea.sh

SHELL ["/bin/bash", "-lc"]
COPY ./system/python.sh /mea/system/python.sh
RUN source /mea/system/python.sh \
    && uv_install

RUN source /mea/system/python.sh \
    && uv_venv
COPY ./bin/pip.sh /usr/local/bin/pip

RUN source /mea/system/python.sh \
    && pip_install_heavy && pip_install_heavy

COPY ./system/p.comfy.sh /mea/system/p.comfy.sh
RUN source /mea/system/p.comfy.sh \
    && install_comfy

RUN apt install -y make && sleep 10
COPY ./system/requirements.txt /mea/system/req.txt
RUN pip install -r /mea/system/req.txt && sleep 10

# # COPY ./system/install.ollama.sh /mea/system/install.ollama.sh
# # RUN source /etc/profile.d/mea.sh && source /mea/system/install.ollama.sh \
# #     && install_ollama

# COPY ./system/install.mea_comfy.sh /mea/system/install.mea_comfy.sh
# RUN source /etc/profile.d/mea.sh && source /mea/system/install.mea_comfy.sh \
#     && install_mea_comfy

COPY system /scripts
RUN cat /scripts/cmds.sh >> /etc/profile.d/cmds.sh

CMD ["/scripts/start.sh"]