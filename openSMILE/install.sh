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
    libopencv-dev \
    libavcodec-dev \
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
wget http://github.com/audeering/opensmile/archive/refs/tags/v3.0.2.tar.gz
tar -xf v3.0.2.tar.gz -C /opt

# Download and extract OpenCV
wget https://github.com/opencv/opencv/archive/refs/tags/2.4.13.3.zip
unzip opencv-2.4.13.3.zip -d /opt

# Configure openSMILE install
cp /home/nonroot/build_flags.sh /opt/opensmile-3.0.2  # Ensure build_flags.sh is in the correct location
cat /opt/opensmile-3.0.2/build_flags.sh

# Insert portaudio dependency
wget http://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz
tar -xzf pa_stable_v190700_20210406.tgz -C /usr/lib
cd /usr/lib/portaudio

# Install OpenCV
cmake -G "Unix Makefiles" \
    -S/opt/opencv-2.4.13.3 \
    -B/opt/opencv-2.4.13.3/release \
    -DCMAKE_CXX_COMPILER=/usr/bin/g++ \
    -DCMAKE_C_COMPILER=/usr/bin/gcc \
    -DCMAKE_BUILD_TYPE=RELEASE \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DWITH_TBB=ON \
    -DBUILD_NEW_PYTHON_SUPPORT=ON \
    -DWITH_V4L=ON \
    -DINSTALL_C_EXAMPLES=ON \
    -DINSTALL_PYTHON_EXAMPLES=ON \
    -DBUILD_EXAMPLES=ON \
    -DWITH_QT=ON \
    -DWITH_OPENGL=ON \
    -DBUILD_FAT_JAVA_LIB=ON \
    -DINSTALL_TO_MANGLED_PATHS=ON \
    -DINSTALL_CREATE_DISTRIB=ON \
    -DINSTALL_TESTS=ON \
    -DENABLE_FAST_MATH=ON \
    -DWITH_IMAGEIO=ON \
    -DBUILD_SHARED_LIBS=OFF \
    -DWITH_GSTREAMER=ON 
make all
make install

# Install openSMILE
cd /opt/opensmile-3.0.2/
./build.sh

# Set working directory
cd /opt/opensmile-3.0.2/build/progsrc/smilextract/

# Set library path
echo "include /usr/local/lib" >> /etc/ld.so.conf
ldconfig