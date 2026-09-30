# Differential Drive Robot — ROS 2 & Gazebo

A differential-drive mobile robot simulation developed using **ROS 2 Jazzy** and **Gazebo Harmonic**.

This project focuses on understanding the complete workflow of a mobile robot: robot modeling, differential-drive kinematics, odometry, TF, LiDAR sensing, ROS 2 communication, teleoperation, command safety, and autonomous obstacle avoidance.

## Project Overview

The robot is simulated in Gazebo and controlled through ROS 2.

The system receives velocity commands from keyboard teleoperation, processes LiDAR data for obstacle detection, applies a safety layer, calculates wheel motion and odometry, and finally sends the velocity command to the Gazebo differential-drive system.

## Features

- Differential-drive mobile robot
- Custom URDF robot model
- Differential-drive kinematics
- Wheel velocity calculation
- Joint-state publishing
- Odometry calculation
- `odom → base_link` TF broadcasting
- Gazebo physics simulation
- Simulated GPU LiDAR
- ROS 2 LaserScan data
- LiDAR frame correction
- Keyboard teleoperation
- Command safety layer
- Command watchdog
- Front obstacle detection
- Left/right obstacle comparison
- Autonomous obstacle avoidance
- Finite State Machine (FSM)
- Custom Gazebo simulation world
- Wall obstacle
- Decorative environment objects
- RViz2 visualization

## 1. Robot Model

The robot is modeled using **URDF**.

Main links:

```text
base_link
left_wheel_link
right_wheel_link
lidar_link
```

Robot parameters:

| Parameter | Value |
|---|---:|
| Wheel radius | 0.075 m |
| Wheel separation | 0.40 m |
| LiDAR height | 0.27 m |

## 2. Differential Drive Kinematics

For a differential-drive robot:

```text
ω_left = (v - ωL/2) / r
ω_right = (v + ωL/2) / r
```

where:

```text
v = robot linear velocity
ω = robot angular velocity
L = wheel separation
r = wheel radius
```

The controller converts the desired robot velocity into left and right wheel velocities.

## 3. Odometry

The controller calculates differential-drive odometry:

```text
v = (v_right + v_left) / 2
ω = (v_right - v_left) / L
```

Pose update:

```text
x = x + v cos(θ) dt
y = y + v sin(θ) dt
θ = θ + ω dt
```

Published topic:

```text
/odom
```

TF:

```text
odom → base_link
```

## 4. LiDAR

A simulated GPU LiDAR is mounted on the robot.

| Parameter | Value |
|---|---:|
| Samples | 180 |
| Horizontal FOV | -π to +π |
| Minimum range | 0.1 m |
| Maximum range | 5.0 m |
| Update rate | 5 Hz |

Raw topic:

```text
/scan
```

## 5. LiDAR Frame Correction

Gazebo generates:

```text
differential_drive_robot/base_link/gpu_lidar
```

The intended ROS frame is:

```text
lidar_link
```

The `scan_frame_corrector` node changes the LaserScan `frame_id` to `lidar_link` and republishes:

```text
/scan_corrected
```

## 6. Obstacle Avoidance

The `obstacle_avoidance` node processes LiDAR data and divides the field of view into:

```text
                  FRONT
              -30° → +30°

          LEFT             RIGHT
       +30° → +90°      -90° → -30°
```

Safe distance:

```text
0.5 m
```

If an obstacle is detected within the safe distance, forward motion is stopped and the robot turns toward the side with more available space.

## 7. Finite State Machine

```text
FORWARD
   │
   │ front_distance < 0.5 m
   ▼
TURNING
   │
   │ front_distance >= 0.5 m
   ▼
FORWARD
```

During `TURNING`:

```text
linear velocity = 0
angular velocity = ±0.5 rad/s
```

## 8. Command Safety Architecture

```text
teleop_twist_keyboard
          │
          ▼
      /cmd_vel
          │
          ▼
 obstacle_avoidance
          │
          ▼
   /cmd_vel_safe
          │
          ▼
   wheel_controller
          │
          ▼
 /cmd_vel_gazebo
          │
          ▼
      Gazebo
```

## 9. Command Watchdog

The `wheel_controller` uses a **0.5 second command timeout**.

If no new velocity command is received within the timeout:

```text
linear velocity = 0
angular velocity = 0
```

This prevents the robot from continuing to move indefinitely if the command source stops publishing.

## 10. Gazebo Environment

The world contains:

- Large ground plane
- Static wall
- Directional light
- Two decorative trees
- Gazebo physics and sensor systems

The decorative trees are environmental visualization objects and are separate from the robot control system.

## 11. ROS 2 Communication

| Topic | Type | Purpose |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Teleoperation command |
| `/cmd_vel_safe` | `geometry_msgs/msg/Twist` | Safety-filtered command |
| `/cmd_vel_gazebo` | `geometry_msgs/msg/Twist` | Gazebo velocity command |
| `/scan` | `sensor_msgs/msg/LaserScan` | Raw LiDAR |
| `/scan_corrected` | `sensor_msgs/msg/LaserScan` | Corrected LiDAR |
| `/joint_states` | `sensor_msgs/msg/JointState` | Wheel joint states |
| `/odom` | `nav_msgs/msg/Odometry` | Robot odometry |

## 12. Package Structure

```text
differential_drive_robot/
├── differential_drive_robot/
│   ├── wheel_controller.py
│   ├── scan_frame_corrector.py
│   └── obstacle_avoidance.py
├── launch/
│   └── display_robot.launch.py
├── urdf/
│   └── diff_drive_robot.urdf
├── config/
│   └── controller.yaml
├── worlds/
│   └── lidar_world.sdf
├── resource/
├── package.xml
├── setup.py
└── setup.cfg
```

## 13. How to Run

### Prerequisites

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- Python 3
- `colcon`

### Build and Launch

```bash
cd ~/ros2_ws && colcon build --packages-select differential_drive_robot && source install/setup.bash && ros2 launch differential_drive_robot display_robot.launch.py
```

### Keyboard Teleoperation

Install:

```bash
sudo apt install ros-jazzy-teleop-twist-keyboard
```

Run:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Controls:

```text
i → Forward
, → Backward
j → Rotate left
l → Rotate right
k → Stop
```

## Useful ROS 2 Commands

```bash
ros2 topic list
ros2 topic echo /scan_corrected --once
ros2 topic echo /odom --once
ros2 topic echo /cmd_vel_safe
ros2 run tf2_ros tf2_echo base_link lidar_link
ros2 pkg prefix differential_drive_robot
```

## Learning Objectives

This project demonstrates:

- ROS 2 package organization
- ROS 2 nodes
- Publisher/subscriber communication
- ROS 2 topics
- URDF modeling
- SDF simulation environments
- Differential-drive kinematics
- Odometry
- TF transformations
- LiDAR sensing
- Sensor-frame handling
- Safety watchdogs
- Finite State Machines
- Autonomous obstacle avoidance
- Gazebo simulation
- RViz2 visualization

## Current Project Status

- [x] ROS 2 package created
- [x] Differential-drive robot modeled
- [x] Wheel joints configured
- [x] Gazebo simulation working
- [x] Robot movement working
- [x] Wheel kinematics implemented
- [x] Joint states implemented
- [x] Odometry implemented
- [x] `odom → base_link` TF implemented
- [x] LiDAR simulation implemented
- [x] LiDAR frame correction implemented
- [x] RViz visualization
- [x] Keyboard teleoperation
- [x] Command watchdog
- [x] Safety command layer
- [x] Front obstacle detection
- [x] Left/right obstacle comparison
- [x] FSM-based obstacle avoidance
- [x] Custom Gazebo environment
- [x] Decorative environment objects

## Future Development

- PID-based wheel control
- Encoder simulation
- IMU integration
- Sensor fusion
- Improved obstacle avoidance
- SLAM
- Mapping
- Nav2
- Path planning
- Autonomous waypoint navigation
- Multi-sensor perception
- Real robot hardware implementation

## Technologies

```text
ROS 2 Jazzy
Gazebo Harmonic
Python
rclpy
URDF
SDF
RViz2
ros_gz_sim
ros_gz_bridge
```

## Author

**Rezwanus Samam Toha**

Mechanical Engineering Graduate Engineer

Interests: Robotics, ROS 2, CAD, CFD, Embedded Systems, and Machine Learning.
