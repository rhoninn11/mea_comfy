FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04

COPY model_download.sh /script_src/model_download.sh
COPY start.sh /start.sh
COPY baseline_snapshot_act_ii.json /baseline_snapshot.json
COPY wget_links /wget_links

CMD ["/start.sh"]