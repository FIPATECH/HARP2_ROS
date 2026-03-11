import os
import socket

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, EnvironmentVariable
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition
from pathlib import Path

import xacro


def _get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('', 0))
        return sock.getsockname()[1]


def generate_launch_description():
    
	# Create the launch configuration variables    
    namespace = LaunchConfiguration('namespace')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_gazebo_gui = LaunchConfiguration('use_gazebo_gui')
    gui_required = 'False' # Keep simulation alive even if gzclient crashes
    server_required = 'True' #Terminate launch script when gzserver (Gazebo Server) exits
    world = LaunchConfiguration('world')
    gazebo_master_uri = LaunchConfiguration('gazebo_master_uri')
    robot_name = LaunchConfiguration('robot_name')
    pose = {'x': LaunchConfiguration('x_pose'),
            'y': LaunchConfiguration('y_pose'),
            'z': LaunchConfiguration('z_pose'),
            'R': LaunchConfiguration('roll', default='0.00'),
            'P': LaunchConfiguration('pitch', default='0.00'),
            'Y': LaunchConfiguration('yaw', default='0.00')}
    use_gazebo = LaunchConfiguration('use_gazebo')

    # Specify directory and path to file within package
    robot_sim_pkg_dir = get_package_share_directory('robot_sim')
    gazebo_ros_pkg_dir = get_package_share_directory('gazebo_ros')
    wordl_file_subpath = 'world/Table2025_with_elements.world'
    # Gazebo environment variables setup 
    gazebo_models_path = os.path.join(robot_sim_pkg_dir, 'models')
    os.environ['GAZEBO_MODEL_PATH'] = gazebo_models_path # Specification of additional model path to use "model://" in world file


    return LaunchDescription([
        
        # Declare launch arguments
	    DeclareLaunchArgument(
            'namespace',
            default_value='',
            description='Top-level namespace'
        ),
        DeclareLaunchArgument(
            'use_gazebo_gui',
            default_value='True',
            description='Launch the user interface window of Gazebo'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='True',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'world',
            default_value=PathJoinSubstitution([robot_sim_pkg_dir, wordl_file_subpath ]),
            description='world file'
        ),
        DeclareLaunchArgument(
            'gazebo_master_uri',
            default_value=f'http://127.0.0.1:{_get_free_port()}',
            description='Gazebo master URI for this simulation instance'
        ),
            DeclareLaunchArgument(
            'robot_name',
            default_value='HARP2',
            description='name of the robot'
        ),
        DeclareLaunchArgument(
            'x_pose',
            default_value= '0.0',
            description='x_pose'
        ),
        DeclareLaunchArgument(
            'y_pose',
            default_value= '0.0',
            description='Y_pose'
        ),
        DeclareLaunchArgument(
            'z_pose',
            default_value= '0.04',
            description='Z_pose'
        ),
        DeclareLaunchArgument(
            'use_gazebo',
            default_value='True',
            description='Use Gazebo'
        ),

        SetEnvironmentVariable('GAZEBO_MASTER_URI', gazebo_master_uri),


        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gazebo_ros_pkg_dir, 'launch', 'gazebo.launch.py')
            ),
            condition =IfCondition(use_gazebo),         
            launch_arguments={'world': world,
                              'use_sim_time': use_sim_time,
                              'gui': use_gazebo_gui,
                              'gui_required': gui_required,
                              'server_required': server_required,
                             }.items()
        ),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            output={'both': 'log'},
            condition =IfCondition(use_gazebo),         
            arguments=[
                '-entity', robot_name,
                '-topic', 'robot_description', # Use of robot description topic to get robot_description. Can use SDF instead created with $ gz sdf -p <urdf_file_name>
                '-robot_namespace', namespace,
                '-x', pose['x'], '-y', pose['y'], '-z', pose['z'],
                '-R', pose['R'], '-P', pose['P'], '-Y', pose['Y']]
        ),


    ])
