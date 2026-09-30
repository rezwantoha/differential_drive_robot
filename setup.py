import os

from setuptools import find_packages, setup

package_name = 'differential_drive_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            ['launch/display_robot.launch.py']),
        (os.path.join('share', package_name, 'urdf'),
            ['urdf/diff_drive_robot.urdf']),
        (os.path.join('share', package_name, 'config'),
            ['config/controller.yaml']),
        (os.path.join('share', package_name, 'worlds'),
            ['worlds/lidar_world.sdf']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rezwan-toha',
    maintainer_email='rezwan-toha@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'wheel_controller = differential_drive_robot.wheel_controller:main',
            'scan_frame_corrector = differential_drive_robot.scan_frame_corrector:main',
            'obstacle_avoidance = differential_drive_robot.obstacle_avoidance:main',
        ],
    },
)