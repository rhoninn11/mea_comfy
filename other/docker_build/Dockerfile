FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04 as base

COPY scripts /scripts
RUN ./scripts/comfy_install.sh 

CMD ["/scripts/start.sh"]