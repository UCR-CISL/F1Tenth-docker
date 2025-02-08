# **F1TENTH ROS 2 Foxy Docker Setup Guide**

## **Step 1: Build the Docker Image and enable X11 forwarding**
1. Open a terminal and navigate to your workspace:
   ```bash
   cd ~/f1tenth_ws
   ```
2. Ensure the **Dockerfile** is in the correct directory (`f1tenth_ws`).
3. Run the following command to build the Docker image:
   ```bash
   xhost +local:root
   docker build -t f1tenth_foxy .
   ```

   - The `-t f1tenth_foxy` **tags** the image for easy reference.


## ** Step 2: Run the Docker Container**
### **With Ethernet (LiDAR) & Serial (VESC) Support**
To **enable network access (LiDAR over Ethernet) and serial communication (VESC via `/dev/ttyUSB0`)**, use:

```bash
docker run -it --rm --net=host --privileged --device=/dev/tty* f1tenth_foxy
```


## ** Step 3: Verify Installed Packages**
Follow steps on: https://f1tenth.readthedocs.io/en/foxy_test/getting_started/firmware/drive_workspace.html

To open another terminal in the same window, run
```bash
docker exec -it <container_id> /bin/bash
```
Find the container id by running 
```bash
sudo docker ps
```

## **Debugging**
### ** No LiDAR Data?**
- Ensure the **LiDAR IP is reachable**:
  ```bash
  ping 192.168.0.10  # Replace with your LiDAR's IP
  ```
- Modify `urg_node` configuration:
  ```yaml
  urg_node:
    ros__parameters:
      ip_address: "192.168.0.10"
      serial_port: ""
      serial_baud: 0
  ```

### **VESC Not Detected?**
- Ensure your device is listed:
  ```bash
  ls /dev/ttyUSB*
  ```
- If missing, restart the container with correct **`--device=/dev/ttyUSBX`**.

## ** Notes**
1. The **container is stateless** (`--rm` removes it after exit). If you need persistent data, use:
   ```bash
   docker run -it --net=host --privileged --device=/dev/ttyUSB0 -v ~/f1tenth_ws:/root/f1tenth_ws f1tenth_foxy
   ```
2. If modifying the `Dockerfile`, **rebuild**:
   ```bash
   docker build -t f1tenth_foxy .
   ```
