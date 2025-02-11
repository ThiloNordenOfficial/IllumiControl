#!/bin/bash

# Update package list and install basic packages
apt-get update
apt-get install -y \
    automake \
    build-essential \
    checkinstall \
    cmake \
    git \
    libtool \
    pkg-config \
    sshfs \
    unzip \
    v4l-utils \
    wget \
    x264 \
    yasm \
    python3 \
    python3-numpy 

# Install all the relevant libraries
apt-get install -y \
    libopencv* \
    libjpeg-dev \
    opencv-data \
    libasound-dev \
    libavcodec-dev\
    libavformat-dev \
    libswscale-dev \
    libxine2 \
    libv4l-dev \
    libtbb-dev \
    libgtk2.0-dev \
    libmp3lame-dev \
    libopencore-amrnb-dev \
    libopencore-amrwb-dev \
    libtheora-dev \
    libvorbis-dev \
    libxvidcore-dev \
    libpng-dev \
    libtiff5-dev \
    portaudio19-dev \
    ffmpeg

# Download and extract openSMILE
if [ -d "./lib/opensmile-3.0.2" ]; then
    echo "openSMILE already exists"
else
  if [ -f "v3.0.2.tar.gz" ]; then
    echo "openSMILE tar.gz already exists: now extracting"
    tar -xzf v3.0.2.tar.gz -C ./lib
  else
    wget http://github.com/audeering/opensmile/archive/refs/tags/v3.0.2.tar.gz
    tar -xzf v3.0.2.tar.gz -C ./lib
  fi
fi

# Configure openSMILE install
cp ./build_flags.sh ./lib/opensmile-3.0.2

# Insert portaudio dependency
# Check if tgz file is already present
if [ -d "/usr/lib/portaudio" ]; then
    echo "Portaudio already exists"
else
  if [ -f "pa_stable_v190700_20210406.tgz" ]; then
    echo "Portaudio tgz already exists: now extracting"
    tar -xzf pa_stable_v190700_20210406.tgz -C /usr/lib
  else
    wget http://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz
    tar -xzf pa_stable_v190700_20210406.tgz -C /usr/lib
  fi
fi


# Install openSMILE
cd ./lib/opensmile-3.0.2/ && ./build.sh

# Set library path
#echo "include /usr/local/lib" >> /etc/ld.so.conf
ldconfig