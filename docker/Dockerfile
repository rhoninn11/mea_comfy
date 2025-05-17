FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04 AS base

COPY system /scripts

RUN touch /etc/mea_env
RUN mkdir /mea
# should be writen to /etc/profile.d/...
RUN echo export PROJ_ROOT="/mea" >> /etc/mea_env
RUN echo export COMFY="/mea/comfy_ui" >> /etc/mea_env

RUN source /etc/mea_env && ./scripts/comfy_install.sh 
RUN source /etc/mea_env && ./scripts/ollama_install.sh
# propably also need added to mea_eni 
RUN source /etc/mea_env && ./scripts/mea_install.sh
# do jakiego standardu się przygotować?
# ja bym chciał mieć to jakoś warstwowo, ale za razem wartościowo, zrobione

RUN cat /etc/mea_env

CMD ["/scripts/start.sh"]