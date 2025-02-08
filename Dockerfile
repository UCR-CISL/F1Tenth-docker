# Use the official ROS 2 Foxy base image
FROM ros:foxy-ros-base

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install required ROS 2 packages
RUN apt-get update && apt-get install -y \
    ros-foxy-ackermann-msgs \
    ros-foxy-diagnostic-updater \
    ros-foxy-serial-driver \
    ros-foxy-rosbridge-server \
    ros-foxy-test-msgs \
    ros-foxy-control-msgs \
    ros-foxy-joy \
    ros-foxy-joy-teleop \
    ros-foxy-urg-node \
    ros-foxy-action-tutorials-interfaces \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*
    
 # Install rviz2 for visualization
RUN apt-get update && apt-get install -y \
    ros-foxy-rviz2 \
    ros-foxy-rviz-common \
    && rm -rf /var/lib/apt/lists/*
    
# Install GUI dependencies for RViz2
RUN apt-get update && apt-get install -y \
    ros-foxy-rviz2 \
    ros-foxy-rviz-common \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*
    
# Enable universe repo and install dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository universe \
    && apt-get update \
    && apt-get install -y python3-tk tk \
    && rm -rf /var/lib/apt/lists/*

# Set up the ROS 2 workspace
WORKDIR /root/f1tenth_ws

# Source the ROS 2 setup script automatically
RUN echo "source /opt/ros/foxy/setup.bash" >> ~/.bashrc

# Set entrypoint
ENTRYPOINT ["/bin/bash"]
