# Differential Drive Robot — Technical Project Description

## 1. Project Overview

This project implements a differential-drive mobile robot using **ROS 2 Jazzy** and **Gazebo Harmonic**.

The objective is to understand robot modeling, differential-drive kinematics, odometry, TF, LiDAR sensing, ROS 2 communication, teleoperation, command safety, and autonomous obstacle avoidance.

## 2. Robot Model

Main links:

```text
base_link
left_wheel_link
right_wheel_link
lidar_link
```

Parameters:

```text
Wheel radius     = 0.075 m
Wheel separation = 0.40 m
LiDAR height     = 0.27 m
```

## 3. Differential Drive Kinematics

```text
ω_left = (v - ωL/2) / r
ω_right = (v + ωL/2) / r
```

where `v` is linear velocity, `ω` is angular velocity, `L` is wheel separation, and `r` is wheel radius.

## 4. Odometry

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

## 5. LiDAR

Configuration:

```text
Samples        = 180
Horizontal FOV = -π to +π
Minimum range  = 0.1 m
Maximum range  = 5.0 m
Update rate    = 5 Hz
```

Raw topic:

```text
/scan
```

## 6. LiDAR Frame Correction

Gazebo generates:

```text
differential_drive_robot/base_link/gpu_lidar
```

The project uses `scan_frame_corrector` to publish the same data with:

```text
frame_id = lidar_link
```

on:

```text
/scan_corrected
```

## 7. Obstacle Avoidance

LiDAR regions:

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

When an obstacle is detected, forward motion is stopped and the robot turns toward the side with more available space.

## 8. Finite State Machine

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

Turning command:

```text
linear velocity = 0
angular velocity = ±0.5 rad/s
```

## 9. Command Safety Architecture

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

## 10. Command Watchdog

Timeout:

```text
0.5 seconds
```

If no new command is received:

```text
linear velocity = 0
angular velocity = 0
```

This prevents indefinite motion after the command source stops.

## 11. Gazebo Environment

The simulation contains:

- Ground plane
- Static wall
- Directional light
- Two decorative trees
- Gazebo physics and sensor systems

The trees are environmental visualization objects separate from the robot control system.

## 12. ROS 2 Communication

```text
/cmd_vel            → geometry_msgs/msg/Twist
/cmd_vel_safe       → geometry_msgs/msg/Twist
/cmd_vel_gazebo     → geometry_msgs/msg/Twist
/scan               → sensor_msgs/msg/LaserScan
/scan_corrected      → sensor_msgs/msg/LaserScan
/joint_states       → sensor_msgs/msg/JointState
/odom               → nav_msgs/msg/Odometry
```

## 13. Package Structure

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

## 14. Running the Project

Build and launch:

```bash
cd ~/ros2_ws && colcon build --packages-select differential_drive_robot && source install/setup.bash && ros2 launch differential_drive_robot display_robot.launch.py
```

Teleoperation:

```bash
sudo apt install ros-jazzy-teleop-twist-keyboard
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

## 15. Useful ROS 2 Commands

```bash
ros2 topic list
ros2 topic echo /scan_corrected --once
ros2 topic echo /odom --once
ros2 topic echo /cmd_vel_safe
ros2 run tf2_ros tf2_echo base_link lidar_link
ros2 pkg prefix differential_drive_robot
```

## 16. Learning Objectives

The project demonstrates:

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

## 17. Project Workflow

```text
SENSOR
  ↓
LiDAR
  ↓
ROS 2 Topic
  ↓
Obstacle Detection
  ↓
Decision / Safety
  ↓
Velocity Command
  ↓
Robot Controller
  ↓
Wheel Kinematics
  ↓
Gazebo
  ↓
Robot Motion
  ↓
Odometry
  ↓
TF
```

## 18. Current Project Status

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

## 19. Future Development

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
