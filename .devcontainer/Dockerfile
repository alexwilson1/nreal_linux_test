FROM docker.io/fizmath/gpu-opencv:latest
RUN apt-key del 7fa2af80 && sed -i '/developer\.download\.nvidia\.com\/compute\/cuda\/repos/d' /etc/apt/sources.list.d/* && sed -i '/developer\.download\.nvidia\.com\/compute\/machine-learning\/repos/d' /etc/apt/sources.list.d/*
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-keyring_1.0-1_all.deb && dpkg -i cuda-keyring_1.0-1_all.deb
# ARG USERNAME=local_user
# ARG USER_UID=1000
# ARG USER_GID=$USER_UID

# # Create the user
# RUN groupadd --gid $USER_GID $USERNAME \
#     && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME 

RUN apt purge --auto-remove cmake -y && pip install cmake

# Install dependencies
RUN apt-get update && apt-get install -y \
    libusb-1.0-0-dev \
    git \
    libssl-dev\
    libjson-c-dev \
    usbutils \
    udev \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository and update submodules
RUN git clone https://gitlab.com/TheJackiMonster/nrealAirLinuxDriver.git /home/$USERNAME/nrealAirLinuxDriver \
    && cd /home/$USERNAME/nrealAirLinuxDriver \
    && git checkout bacc08e5943722570a51e62c9e97b3470484988d\
    && git submodule update --init

# Build the project
RUN cd /home/$USERNAME/nrealAirLinuxDriver \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make


# USER $USERNAME