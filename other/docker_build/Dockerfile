FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04 as base

COPY scripts /scripts

RUN touch /etc/mea_env
RUN mkdir /mea

RUN ./scripts/comfy_install.sh 
RUN cat /etc/mea_env

CMD ["/scripts/start.sh"]