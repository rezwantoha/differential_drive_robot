import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    package_path = get_package_share_directory(
        'differential_drive_robot'
    )

    config_file = os.path.join(
        package_path,
        'config',
        'controller.yaml'
    )

    urdf_file = os.path.join(
        package_path,
        'urdf',
        'diff_drive_robot.urdf'
    )

    world_file = os.path.join(
        package_path,
        'worlds',
        'lidar_world.sdf'
    )

    with open(urdf_file, 'r') as file:
        robot_description = file.read()

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                '/opt/ros/jazzy/share/ros_gz_sim/launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': world_file
        }.items()
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': robot_description}
        ]
    )

    # Differential drive controller
    controller = Node(
        package='differential_drive_robot',
        executable='wheel_controller',
        name='differential_drive_controller',
        parameters=[config_file]
    )

    # Spawn robot into Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-world', 'lidar_world',
            '-file', urdf_file,
            '-name', 'differential_drive_robot',
            '-x', '0',
            '-y', '0',
            '-z', '0.08'
        ],
        output='screen'
    )

    # Gazebo → ROS 2 LiDAR bridge
    lidar_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/cmd_vel_gazebo@geometry_msgs/msg/Twist@gz.msgs.Twist'
        ],
        output='screen'
    )

    # Correct LiDAR frame_id
    scan_frame_corrector = Node(
        package='differential_drive_robot',
        executable='scan_frame_corrector',
        name='scan_frame_corrector'
    )
    obstacle_avoidance = Node(
        package='differential_drive_robot',
        executable='obstacle_avoidance',
        name='obstacle_avoidance'
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        controller,
        spawn_robot,
        lidar_bridge,
        scan_frame_corrector,
        obstacle_avoidance,
        rviz
    ])