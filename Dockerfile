# Use the F1Tenth stack base image
FROM f1tenth/focal-l4t-foxy:f1tenth-stack

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive


# Enable universe repo and install dependencies
# Download drivers to enable X11 and rviz support through the container
WORKDIR /root
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository universe \
    && apt-get update \
    && apt-get install -y python3-tk tk \
    && rm -rf /var/lib/apt/lists/* \
    mesa-utils libgl1-mesa-glx libgl1-mesa-dri && \
    rm -rf /var/lib/apt/lists/*
RUN apt install -y build-essential autoconf automake libtool wget
    
# Download and install libffi (fixes joystick driver issues)
WORKDIR /tmp
RUN wget https://github.com/libffi/libffi/releases/download/v3.4.4/libffi-3.4.4.tar.gz && \
    tar -xzf libffi-3.4.4.tar.gz && \
    cd libffi-3.4.4 && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    rm -rf /tmp/libffi-3.4.4 /tmp/libffi-3.4.4.tar.gz

# Set up the ROS 2 workspace
WORKDIR /root/f1tenth_ws/
# RUN source /opt/ros/foxy/setup.bash \
#     source /f1tenth_ws/install/setup.bash

# Create the new autonomous node and copy the prewritten python script
RUN ros2 pkg create --build-type ament_python autonomous_car
COPY autonomous_car.py /root/ros2_ws/src/autonomous_car/autonomous_car/autonomous_car.py

# Set entrypoint
ENTRYPOINT ["/bin/bash"]
