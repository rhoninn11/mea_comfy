FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04 AS base

COPY scripts /scripts

RUN touch /etc/mea_env
RUN mkdir /mea
RUN echo export PROJ_ROOT="/mea" >> /etc/mea_env

RUN source /etc/mea_env && ./scripts/comfy_install.sh 
RUN echo export COMFY="/mea/comfy_ui" >> /etc/mea_env
RUN source /etc/mea_env && ./scripts/mea_install.sh
RUN cat /etc/mea_env

CMD ["/scripts/start.sh"]