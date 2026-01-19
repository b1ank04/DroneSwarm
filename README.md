# Drone Swarm Simulation

A Python-based simulation of swarm intelligence using autonomous agents (drones). The simulation demonstrates emergent behavior based on simple local rules, inspired by Reynolds' Boids algorithm.

## Installation & Usage

### Prerequisites
- Python 3.x installed
- `pip` package manager

### Setup
1. Clone the repository or download the source code.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Simulation
Execute the main script to start the simulation window:
```bash
python main.py
```

### Controls
- **Mouse Movement**: Control the target point (red circle) that the swarm follows.
- **`V` Key**: Toggle the visualization of each drone's neighbor perception radius.

### Running via Docker
To run the simulation in a Docker container while displaying the window on your host machine, follow these steps.

**1. Build the Docker Image**
```bash
docker build -t drone-swarm .
```

**2. Run the Container**

*   **Linux**:
    ```bash
    xhost +local:docker
    docker run -it --rm \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -e DISPLAY=$DISPLAY \
      drone-swarm
    ```

*   **macOS**:
    1.  Install [XQuartz](https://www.xquartz.org/).
    2.  Open XQuartz, go to **Preferences > Security** and check **"Allow connections from network clients"**.
    3.  Restart XQuartz.
    4.  Run the following in your terminal:
        ```bash
        xhost + 127.0.0.1
        docker run -it --rm \
          -e DISPLAY=host.docker.internal:0 \
          drone-swarm
        ```

*   **Windows**:
    1.  Install an X Server like [VcXsrv](https://sourceforge.net/projects/vcxsrv/).
    2.  Launch XLaunch with **"Disable access control"** checked.
    3.  Run in PowerShell/Command Prompt:
        ```bash
        docker run -it --rm -e DISPLAY=host.docker.internal:0 drone-swarm
        ```

### Running via Docker Compose
Alternatively, you can use Docker Compose.

**MACOS USERS:**
Use the provided helper script which automatically configures permissions:
```bash
./run_mac.sh
```
*Make sure you have enabled "Allow connections from network clients" in XQuartz Preferences > Security.*

**Other OS:**
1.  **Start the Simulation**:
    ```bash
    docker-compose up --build
    ```

    *Note: Ensure your X server (XQuartz/VcXsrv/Xorg) is configured as described in the "Run the Container" section above.*

---

## How It Works

The simulation relies on a decentralized system where each drone calculates its next move based solely on its local environment and a few governing rules. There is no central controller determining the specific path of every drone; instead, complex flocking behavior emerges from the sum of individual decisions.

### 1. The Physics Model
Each drone acts as a point mass with:
- **Position**: Coordinates in the 2D space.
- **Velocity**: Current speed and direction.
- **Acceleration**: Changes in velocity derived from applied forces.

On every frame, forces are applied to the drone's acceleration. This updates the velocity (limited to a maximum speed), which in turn updates the position.

### 2. Core Swarm Behaviors (Boids Rules)
The swarm acts cohesively due to three weighted forces calculated relative to neighboring drones (drones within `NEIGHBOR_RADIUS`):

1.  **Separation**: Steer away from neighbors that are too close to avoid collisions.
2.  **Alignment**: Steer towards the average heading (velocity) of neighbors to move in sync.
3.  **Cohesion**: Steer towards the average position (center of mass) of neighbors to stay together.

### 3. Navigation & Target Seeking
Drones are attracted to a target (the mouse cursor).
-   **Seek**: A force steers the drone towards the target.
-   **Arrival**: As the drone enters a `SLOWING_RADIUS` around the target, it linearly decreases speed to prevent overshooting, allowing for a smooth approach.

### 4. Parking Logic
A special behavior triggers when a drone centers on the `PARKING_RADIUS` around the final target:
-   **High Friction**: Velocity is significantly dampened (multiplied by 0.85) to simulate braking.
-   **Enhanced Separation**: The separation force weight is doubled to ensure drones spread out comfortably around the target without overlapping.
-   Other forces (Alignment, Cohesion, Seek) are bypassed to stabilize the formation.
