# lowest possible version of 12-3
CUDA_VER_DASH=12-6
CUDA_VER_DOT=12.6

_source () {
    wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb
    dpkg -i cuda-keyring_1.1-1_all.deb
    apt update
}

_profile() {
    PROFILE="/etc/profile.d/cuda.profile.sh"
    echo "export PATH=/usr/local/cuda-${CUDA_VER_DOT}/bin:$PATH" >> ${PROFILE}
}

install() {
    _source
    sleep 10
    apt install -y \
        cuda-toolkit-${CUDA_VER_DASH} \
        cuda-nvcc-${CUDA_VER_DASH}
    _profile
}

NVIDIA_CONTAINER_TOOLKIT_VERSION=1.19.1-1
nvctk_install() {
    sudo apt-get update && sudo apt-get install -y --no-install-recommends \
        ca-certificates curl gnupg2

    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
        && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    
    sudo sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list

    sudo apt-get update

    sudo apt-get install -y \
        nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
        nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
        libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
        libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}
}

nvctk_init() {
    sudo nvidia-ctk runtime configure --runtime=docker
    sudo systemctl restart docker
}
