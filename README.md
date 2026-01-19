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
