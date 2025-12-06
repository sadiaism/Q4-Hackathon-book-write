# Chapter 11: Nav2: Path planning for bipedal humanoid movement

## Learning Objectives
After completing this chapter, students will be able to:
- Install and configure Navigation2 (Nav2) for humanoid robot navigation
- Understand the differences between wheeled robot navigation and bipedal locomotion
- Adapt Nav2 for bipedal humanoid path planning and execution
- Implement custom controllers for bipedal locomotion patterns
- Configure costmaps for humanoid-scale navigation in human environments
- Plan paths that account for bipedal gait constraints and balance requirements
- Integrate humanoid-specific perception and control systems with Nav2
- Validate navigation performance for bipedal robots in complex environments

## 11.1 Introduction to Navigation2 (Nav2)

Navigation2 (Nav2) is the next-generation navigation framework for ROS 2, designed to provide robust, flexible, and efficient path planning and navigation capabilities for mobile robots. While traditionally used for wheeled robots, Nav2 can be adapted for bipedal humanoid navigation with appropriate modifications to account for the unique challenges of legged locomotion.

### Key Features of Nav2
- **Modular Architecture**: Pluggable components for different navigation needs
- **Behavior Trees**: Flexible execution of navigation behaviors
- **Costmap Integration**: 2D and 3D costmap support for obstacle avoidance
- **Path Planning**: Multiple planning algorithms (NavFn, A*, Dijkstra, etc.)
- **Controller Integration**: Pluggable controllers for different robot types
- **Recovery Behaviors**: Robust recovery from navigation failures
- **Simulation Tools**: Extensive simulation and testing capabilities

### Nav2 vs Traditional Navigation Stacks
Compared to older navigation stacks, Nav2 offers:
- **ROS 2 Integration**: Native ROS 2 support with improved architecture
- **Behavior Trees**: More flexible and robust execution framework
- **Modern Algorithms**: Updated path planning and control algorithms
- **Better Testing**: Comprehensive testing and validation tools
- **Extensibility**: Easier customization for different robot types

## 11.2 Installing and Configuring Nav2

### System Requirements
- **Operating System**: Ubuntu 20.04 LTS or 22.04 LTS
- **ROS 2**: Humble Hawksbill (recommended) or later
- **Dependencies**: Gazebo, RViz2, and other standard ROS 2 packages

### Installing Nav2
```bash
# Install Nav2 packages
sudo apt update
sudo apt install ros-humble-navigation2
sudo apt install ros-humble-nav2-bringup
sudo apt install ros-humble-nav2-gui-launchers
sudo apt install ros-humble-nav2-rviz-plugins
sudo apt install ros-humble-nav2-map-server
sudo apt install ros-humble-nav2-utils
sudo apt install ros-humble-nav2-amcl
sudo apt install ros-humble-nav2-controller-server
sudo apt install ros-humble-nav2-planner-server
sudo apt install ros-humble-nav2-recovery
sudo apt install ros-humble-nav2-behaviors
sudo apt install ros-humble-nav2-lifecycle-manager
```

### Basic Nav2 Launch
```bash
# Launch Nav2 with default configuration
ros2 launch nav2_bringup navigation_launch.py

# Launch with simulation
ros2 launch nav2_bringup tb3_simulation_launch.py
```

## 11.3 Bipedal Locomotion vs Wheeled Navigation

### Fundamental Differences
Bipedal humanoid navigation differs significantly from wheeled robot navigation:

#### Kinematic Constraints
- **Wheeled Robots**: Continuous motion, differential or Ackermann steering
- **Bipedal Robots**: Discrete step-based motion, balance-dependent movement

#### Dynamic Considerations
- **Wheeled Robots**: Primarily kinematic planning sufficient
- **Bipedal Robots**: Dynamic balance and stability requirements

#### Footprint and Clearance
- **Wheeled Robots**: Consistent ground contact, predictable footprint
- **Bipedal Robots**: Changing center of mass, swing phase considerations

### Bipedal-Specific Navigation Challenges
- **Balance Maintenance**: Path planning must consider balance constraints
- **Step Planning**: Individual step placement for stable locomotion
- **Terrain Adaptation**: Navigating uneven surfaces and obstacles
- **Energy Efficiency**: Optimizing for battery life with walking gaits
- **Stability Regions**: Maintaining center of mass within support polygon

## 11.4 Adapting Nav2 for Bipedal Navigation

### Custom Costmap Configuration
Bipedal robots require specialized costmap parameters:

```yaml
# bipedal_costmap_params.yaml
amcl:
  ros__parameters:
    use_sim_time: False
    alpha1: 0.2
    alpha2: 0.2
    alpha3: 0.2
    alpha4: 0.2
    alpha5: 0.2
    base_frame_id: "base_footprint"
    beam_skip_distance: 0.5
    beam_skip_error_threshold: 0.9
    beam_skip_threshold: 0.3
    do_beamskip: false
    global_frame_id: "map"
    lambda_short: 0.1
    likelihood_max_dist: 2.0
    set_initial_pose: true
    initial_pose:
      x: 0.0
      y: 0.0
      z: 0.0
      yaw: 0.0
    tf_broadcast: true
    transform_timeout: 0.2
    update_min_a: 0.5
    update_min_d: 0.2
    z_hit: 0.5
    z_max: 0.05
    z_min: 0.05
    z_short: 0.05

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_footprint
      use_sim_time: false
      resolution: 0.05
      robot_radius: 0.4  # Bipedal robot radius consideration
      plugins: ["voxel_layer", "inflation_layer"]
      inflation_layer:
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
      voxel_layer:
        enabled: true
        publish_voxel_map: true
        origin_z: 0.0
        z_resolution: 0.2
        z_voxels: 10
        max_obstacle_height: 2.0
        mark_threshold: 0
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: true
          marking: true
          data_type: LaserScan

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 0.5
      global_frame: map
      robot_base_frame: base_footprint
      use_sim_time: false
      resolution: 0.05
      robot_radius: 0.4
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      obstacle_layer:
        enabled: true
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: true
          marking: true
          data_type: LaserScan
      static_layer:
        enabled: true
        map_topic: /map
      inflation_layer:
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
```

### Bipedal-Specific Parameters
```yaml
# bipedal_specific_params.yaml
bt_navigator:
  ros__parameters:
    use_sim_time: false
    global_frame: map
    robot_base_frame: base_footprint
    odom_topic: /odom
    default_bt_xml_filename: "navigate_w_replanning_and_recovery.xml"
    plugin_lib_names:
    - nav2_compute_path_to_pose_action
    - nav2_follow_path_action
    - nav2_back_up_action
    - nav2_spin_action
    - nav2_wait_action
    - nav2_clear_costmap_service
    - nav2_is_stuck_condition
    - nav2_goal_reached_condition
    - nav2_goal_updated_condition
    - nav2_initial_pose_received_condition
    - nav2_reinitialize_global_localization_service
    - nav2_rate_controller
    - nav2_distance_controller
    - nav2_speed_controller
    - nav2_truncate_path_action
    - nav2_goal_updater_node
    - nav2_recovery_node
    - nav2_pipeline_sequence
    - nav2_round_robin_node
    - nav2_transform_available_condition
    - nav2_time_expired_condition
    - nav2_distance_traveled_condition
    - nav2_single_trigger
    - nav2_is_battery_low_condition

controller_server:
  ros__parameters:
    use_sim_time: false
    controller_frequency: 20.0  # Lower frequency for bipedal stability
    min_x_velocity_threshold: 0.05
    min_y_velocity_threshold: 0.1
    min_theta_velocity_threshold: 0.1
    progress_checker_plugin: "progress_checker"
    goal_checker_plugin: "goal_checker"
    controller_plugins: ["FollowPath"]

    # DWB Controller for bipedal robots
    FollowPath:
      plugin: "nav2_mppi_controller::MPPIController"
      time_steps: 25
      model_dt: 0.05
      batch_size: 1000
      vx_std: 0.2
      vy_std: 0.2
      wz_std: 0.3
      vx_max: 0.5    # Slower for bipedal stability
      vx_min: -0.2
      vy_max: 0.3
      wz_max: 0.3
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25
      state_reset_threshold: 0.5
      control_horizon: 10
      trajectory_visualization_enabled: true
      critics: ["BaseObstacleCritic", "GoalCritic", "PathAlignCritic",
                "PathFollowCritic", "PathProgressCritic", "PreferForwardCritic"]

    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0

    goal_checker:
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25
      stateful: true
```

## 11.5 Custom Controllers for Bipedal Locomotion

### Bipedal Path Following Controller
```python
# bipedal_controller.py
import rclpy
from rclpy.node import Node
from nav2_core.controller import Controller
from nav2_util.lifecycle_node import LifecycleNode
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Path
from builtin_interfaces.msg import Duration
import numpy as np
import math

class BipedalController(Controller):
    """
    Custom controller for bipedal humanoid robots that considers
    balance and gait constraints during path following
    """

    def __init__(self):
        super().__init__()
        self.initialized = False
        self.bipedal_params = {}

    def configure(self, node, plugin_name, tf, costmap_ros):
        """
        Configure the controller with bipedal-specific parameters
        """
        self.node = node
        self.plugin_name = plugin_name
        self.tf = tf
        self.costmap_ros = costmap_ros
        self.costmap = costmap_ros.get_costmap()

        # Bipedal-specific parameters
        self.bipedal_params = {
            'step_length': 0.3,      # Maximum step length
            'step_width': 0.2,       # Step width for stability
            'max_step_height': 0.1,  # Maximum step-over height
            'stance_time': 0.8,      # Time for each step
            'balance_margin': 0.1,   # Safety margin for balance
            'gait_frequency': 1.0    # Steps per second
        }

        self.initialized = True
        self.get_logger().info(f"{self.plugin_name} has been configured!")

    def cleanup(self):
        """Cleanup the controller"""
        self.initialized = False
        self.get_logger().info(f"{self.plugin_name} has been cleaned up")

    def activate(self):
        """Activate the controller"""
        self.get_logger().info(f"{self.plugin_name} has been activated")

    def deactivate(self):
        """Deactivate the controller"""
        self.get_logger().info(f"{self.plugin_name} has been deactivated")

    def setPlan(self, path: Path):
        """
        Set the plan for the controller
        """
        self.path = path
        self.path_index = 0
        self.get_logger().info(f"New plan set with {len(path.poses)} points")

    def computeVelocityCommands(self, pose: PoseStamped, velocity: Twist) -> Twist:
        """
        Compute velocity commands for bipedal locomotion
        """
        if not self.initialized:
            self.get_logger().error("Controller is not initialized")
            return Twist()

        # Calculate desired velocity based on path following
        cmd_vel = self.calculate_bipedal_velocity(pose, velocity)

        # Apply bipedal constraints
        cmd_vel = self.apply_bipedal_constraints(cmd_vel)

        return cmd_vel

    def calculate_bipedal_velocity(self, pose: PoseStamped, velocity: Twist) -> Twist:
        """
        Calculate velocity considering bipedal locomotion constraints
        """
        # Get current position and orientation
        current_x = pose.pose.position.x
        current_y = pose.pose.position.y
        current_yaw = self.quaternion_to_yaw(pose.pose.orientation)

        # Get next goal in path
        if self.path_index < len(self.path.poses):
            goal = self.path.poses[self.path_index]
            goal_x = goal.pose.position.x
            goal_y = goal.pose.position.y
        else:
            # At the end of path, stop
            return Twist()

        # Calculate distance to goal
        dist_to_goal = math.sqrt((goal_x - current_x)**2 + (goal_y - current_y)**2)

        # Check if we've reached current path point
        if dist_to_goal < self.bipedal_params['step_length'] / 2:
            self.path_index += 1
            if self.path_index < len(self.path.poses):
                goal = self.path.poses[self.path_index]
                goal_x = goal.pose.position.x
                goal_y = goal.pose.position.y

        # Calculate desired heading to goal
        desired_yaw = math.atan2(goal_y - current_y, goal_x - current_x)
        yaw_error = self.normalize_angle(desired_yaw - current_yaw)

        # Create velocity command
        cmd_vel = Twist()

        # Linear velocity based on distance to goal and bipedal constraints
        linear_speed = min(dist_to_goal * 1.0, 0.3)  # Max 0.3 m/s for bipedal
        cmd_vel.linear.x = max(0.05, linear_speed)  # Minimum speed to keep walking

        # Angular velocity based on heading error and bipedal constraints
        angular_speed = yaw_error * 1.0
        cmd_vel.angular.z = max(-0.3, min(0.3, angular_speed))  # Limit angular speed

        return cmd_vel

    def apply_bipedal_constraints(self, cmd_vel: Twist) -> Twist:
        """
        Apply bipedal-specific constraints to velocity commands
        """
        # Limit linear velocity for stability
        max_linear = self.bipedal_params['gait_frequency'] * self.bipedal_params['step_length']
        cmd_vel.linear.x = max(0.05, min(cmd_vel.linear.x, max_linear))

        # Limit angular velocity for balance
        cmd_vel.angular.z = max(-0.3, min(cmd_vel.angular.z, 0.3))

        return cmd_vel

    def quaternion_to_yaw(self, orientation):
        """Convert quaternion to yaw angle"""
        siny_cosp = 2 * (orientation.w * orientation.z + orientation.x * orientation.y)
        cosy_cosp = 1 - 2 * (orientation.y * orientation.y + orientation.z * orientation.z)
        return math.atan2(siny_cosp, cosy_cosp)

    def normalize_angle(self, angle):
        """Normalize angle to [-pi, pi] range"""
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle
```

### Bipedal Gait Controller Node
```python
# bipedal_gait_controller.py
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Pose
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32
from tf2_ros import TransformListener, Buffer
import numpy as np
import math

class BipedalGaitController(Node):
    """
    Controller that converts navigation commands to bipedal gait patterns
    """

    def __init__(self):
        super().__init__('bipedal_gait_controller')

        # Subscriptions
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel_nav', self.cmd_vel_callback, 10
        )

        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10
        )

        # Publishers
        self.joint_cmd_pub = self.create_publisher(
            JointState, '/joint_commands', 10
        )

        self.balance_pub = self.create_publisher(
            Float32, '/balance_state', 10
        )

        # TF listener for pose information
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Gait parameters
        self.gait_params = {
            'step_height': 0.05,      # Height of foot lift during step
            'step_duration': 1.0,     # Time for complete step cycle
            'stance_duration': 0.8,   # Time in stance phase
            'swing_duration': 0.2,    # Time in swing phase
            'max_step_length': 0.3,   # Maximum step length
            'hip_height': 0.7         # Desired hip height for walking
        }

        # State variables
        self.current_cmd_vel = Twist()
        self.current_joint_positions = {}
        self.left_foot_in_swing = False
        self.right_foot_in_swing = False
        self.balance_state = 0.0  # -1.0 (left) to 1.0 (right)

        # Timers
        self.gait_timer = self.create_timer(0.02, self.gait_control_loop)  # 50 Hz

    def cmd_vel_callback(self, msg):
        """Handle velocity commands from Nav2"""
        self.current_cmd_vel = msg

        # Log received command
        self.get_logger().debug(
            f'Received cmd_vel: linear.x={msg.linear.x:.3f}, angular.z={msg.angular.z:.3f}'
        )

    def joint_state_callback(self, msg):
        """Update current joint positions"""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.current_joint_positions[name] = msg.position[i]

    def gait_control_loop(self):
        """Main gait control loop"""
        # Calculate desired joint positions based on velocity command
        desired_joints = self.calculate_gait_pattern()

        # Create and publish joint commands
        joint_cmd = JointState()
        joint_cmd.header.stamp = self.get_clock().now().to_msg()
        joint_cmd.name = list(desired_joints.keys())
        joint_cmd.position = list(desired_joints.values())

        self.joint_cmd_pub.publish(joint_cmd)

        # Publish balance state
        balance_msg = Float32()
        balance_msg.data = self.balance_state
        self.balance_pub.publish(balance_msg)

    def calculate_gait_pattern(self):
        """Calculate gait pattern based on desired velocity"""
        # Simplified gait pattern calculation
        # In a real implementation, this would involve complex inverse kinematics

        desired_positions = {}

        # Calculate step parameters based on velocity command
        linear_vel = self.current_cmd_vel.linear.x
        angular_vel = self.current_cmd_vel.angular.z

        # Determine step length and direction
        step_length = min(abs(linear_vel) * 0.5, self.gait_params['max_step_length'])
        step_length = step_length if linear_vel >= 0 else -step_length

        # Calculate turning parameters
        turn_amount = angular_vel * 0.2  # Scale factor for turning

        # Calculate joint positions for basic walking gait
        # This is a simplified representation - real implementation would be more complex
        time_in_cycle = self.get_clock().now().nanoseconds / 1e9 % self.gait_params['step_duration']
        phase = (time_in_cycle / self.gait_params['step_duration']) * 2 * math.pi

        # Hip joints (for balance and forward motion)
        desired_positions['left_hip_roll'] = turn_amount * 0.1  # Slight roll for turning
        desired_positions['right_hip_roll'] = -turn_amount * 0.1

        desired_positions['left_hip_pitch'] = -0.1 + step_length * 0.2  # Forward lean
        desired_positions['right_hip_pitch'] = -0.1 + step_length * 0.2

        # Knee joints (for leg movement)
        knee_angle = math.sin(phase) * 0.3 * abs(step_length)
        desired_positions['left_knee'] = knee_angle
        desired_positions['right_knee'] = -knee_angle  # Opposite phase for alternating steps

        # Ankle joints (for balance)
        ankle_correction = self.balance_state * 0.1
        desired_positions['left_ankle_pitch'] = -0.05 + ankle_correction
        desired_positions['right_ankle_pitch'] = -0.05 - ankle_correction

        # Update balance state based on gait phase
        self.balance_state = math.sin(phase * 2) * 0.5  # Shift balance during steps

        return desired_positions
```

## 11.6 Path Planning for Bipedal Constraints

### Bipedal-Aware Path Planner
```python
# bipedal_path_planner.py
import rclpy
from rclpy.node import Node
from nav2_core.planner import GlobalPlanner
from nav2_costmap_2d.costmap_2d_ros import Costmap2DROS
from geometry_msgs.msg import PoseStamped, Point
from nav_msgs.msg import Path
from builtin_interfaces.msg import Duration
import numpy as np
import math

class BipedalPathPlanner(GlobalPlanner):
    """
    Path planner adapted for bipedal humanoid robots considering
    step constraints and balance requirements
    """

    def __init__(self):
        super().__init__()
        self.initialized = False
        self.bipedal_constraints = {}

    def configure(self, node, name, tf, costmap_ros):
        """
        Configure the planner with bipedal-specific constraints
        """
        self.node = node
        self.name = name
        self.tf = tf
        self.costmap_ros = costmap_ros
        self.costmap = costmap_ros.get_costmap()

        # Bipedal-specific constraints
        self.bipedal_constraints = {
            'max_step_length': 0.4,      # Maximum distance between steps
            'min_step_length': 0.1,      # Minimum step distance
            'max_step_height': 0.15,     # Maximum step-over height
            'max_slope_angle': 15.0,     # Maximum traversable slope (degrees)
            'footprint_radius': 0.15,    # Footprint for collision checking
            'balance_margin': 0.2        # Safety margin for balance
        }

        self.initialized = True
        self.get_logger().info(f"{self.name} has been configured for bipedal navigation")

    def cleanup(self):
        """Cleanup the planner"""
        self.initialized = False
        self.get_logger().info(f"{self.name} has been cleaned up")

    def activate(self):
        """Activate the planner"""
        self.get_logger().info(f"{self.name} has been activated")

    def deactivate(self):
        """Deactivate the planner"""
        self.get_logger().info(f"{self.name} has been deactivated")

    def createPlan(self, start: PoseStamped, goal: PoseStamped) -> Path:
        """
        Create a path considering bipedal locomotion constraints
        """
        if not self.initialized:
            self.get_logger().error("Planner is not initialized")
            return Path()

        # Validate start and goal positions for bipedal feasibility
        if not self.is_bipedal_feasible(start.pose.position, goal.pose.position):
            self.get_logger().warn("Start or goal position not feasible for bipedal robot")
            return Path()

        # Plan path using modified A* algorithm considering bipedal constraints
        path = self.plan_bipedal_path(start, goal)

        # Post-process path to ensure bipedal constraints are met
        path = self.post_process_bipedal_path(path)

        return path

    def is_bipedal_feasible(self, start_pos, goal_pos):
        """
        Check if start and goal positions are feasible for bipedal navigation
        """
        # Check if positions are in valid areas of costmap
        start_cost = self.costmap.getCost(
            int(start_pos.x / self.costmap.getResolution()),
            int(start_pos.y / self.costmap.getResolution())
        )

        goal_cost = self.costmap.getCost(
            int(goal_pos.x / self.costmap.getResolution()),
            int(goal_pos.y / self.costmap.getResolution())
        )

        # Check if costs are within traversable range
        if start_cost >= 253 or goal_cost >= 253:  # LETHAL_OBSTACLE or INSCRIBED_INFLATED_OBSTACLE
            return False

        # Additional checks for bipedal feasibility
        # Check for sufficient space for bipedal movement
        return True

    def plan_bipedal_path(self, start: PoseStamped, goal: PoseStamped) -> Path:
        """
        Plan path using algorithm adapted for bipedal constraints
        """
        # Get map dimensions
        map_width = self.costmap.getSizeInCellsX()
        map_height = self.costmap.getSizeInCellsY()
        resolution = self.costmap.getResolution()

        # Convert start and goal to map coordinates
        start_x = int((start.pose.position.x - self.costmap.getOriginX()) / resolution)
        start_y = int((start.pose.position.y - self.costmap.getOriginY()) / resolution)
        goal_x = int((goal.pose.position.x - self.costmap.getOriginX()) / resolution)
        goal_y = int((goal.pose.position.y - self.costmap.getOriginY()) / resolution)

        # Validate coordinates are within map bounds
        if (start_x < 0 or start_x >= map_width or start_y < 0 or start_y >= map_height or
            goal_x < 0 or goal_x >= map_width or goal_y < 0 or goal_y >= map_height):
            return Path()

        # Implement A* pathfinding with bipedal constraints
        path = self.bipedal_astar(start_x, start_y, goal_x, goal_y)

        # Convert path back to world coordinates
        world_path = Path()
        world_path.header.frame_id = "map"
        world_path.header.stamp = self.node.get_clock().now().to_msg()

        for point in path:
            pose = PoseStamped()
            pose.header.frame_id = "map"
            pose.pose.position.x = point[0] * resolution + self.costmap.getOriginX()
            pose.pose.position.y = point[1] * resolution + self.costmap.getOriginY()
            pose.pose.position.z = 0.0
            pose.pose.orientation.w = 1.0
            world_path.poses.append(pose)

        return world_path

    def bipedal_astar(self, start_x, start_y, goal_x, goal_y):
        """
        A* algorithm modified for bipedal constraints
        """
        import heapq

        def heuristic(x1, y1, x2, y2):
            return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

        # Check if a move is valid considering bipedal constraints
        def is_valid_move(from_x, from_y, to_x, to_y):
            # Check costmap for obstacles
            cost = self.costmap.getCost(to_x, to_y)
            if cost >= 253:  # LETHAL_OBSTACLE
                return False

            # Check if step distance is within bipedal limits
            step_dist = math.sqrt((to_x - from_x)**2 + (to_y - from_y)**2)
            if step_dist > self.bipedal_constraints['max_step_length'] / self.costmap.getResolution():
                return False

            return True

        # A* implementation
        open_set = [(0, start_x, start_y)]
        came_from = {}
        g_score = {(start_x, start_y): 0}
        f_score = {(start_x, start_y): heuristic(start_x, start_y, goal_x, goal_y)}

        while open_set:
            current = heapq.heappop(open_set)
            current_f, current_x, current_y = current

            if current_x == goal_x and current_y == goal_y:
                # Reconstruct path
                path = []
                while (current_x, current_y) in came_from:
                    path.append((current_x, current_y))
                    current_x, current_y = came_from[(current_x, current_y)]
                path.append((start_x, start_y))
                path.reverse()
                return path

            # Check 8-connected neighbors (for more natural paths)
            for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                neighbor_x, neighbor_y = current_x + dx, current_y + dy

                if (neighbor_x < 0 or neighbor_x >= self.costmap.getSizeInCellsX() or
                    neighbor_y < 0 or neighbor_y >= self.costmap.getSizeInCellsY()):
                    continue

                if not is_valid_move(current_x, current_y, neighbor_x, neighbor_y):
                    continue

                # Calculate tentative g_score
                step_cost = math.sqrt(dx*dx + dy*dy)  # Diagonal moves cost more
                tentative_g_score = g_score[(current_x, current_y)] + step_cost

                if (neighbor_x, neighbor_y) not in g_score or tentative_g_score < g_score[(neighbor_x, neighbor_y)]:
                    came_from[(neighbor_x, neighbor_y)] = (current_x, current_y)
                    g_score[(neighbor_x, neighbor_y)] = tentative_g_score
                    f_score[(neighbor_x, neighbor_y)] = tentative_g_score + heuristic(neighbor_x, neighbor_y, goal_x, goal_y)
                    heapq.heappush(open_set, (f_score[(neighbor_x, neighbor_y)], neighbor_x, neighbor_y))

        # No path found
        return []

    def post_process_bipedal_path(self, path: Path) -> Path:
        """
        Post-process path to ensure it meets bipedal constraints
        """
        if len(path.poses) <= 1:
            return path

        # Smooth the path to reduce sharp turns that may be difficult for bipedal robots
        smoothed_path = self.smooth_path_bipedal(path)

        # Ensure path points are spaced appropriately for bipedal steps
        adjusted_path = self.adjust_path_spacing(smoothed_path)

        return adjusted_path

    def smooth_path_bipedal(self, path: Path) -> Path:
        """
        Smooth path with constraints suitable for bipedal locomotion
        """
        if len(path.poses) < 3:
            return path

        # Use a simplified smoothing algorithm that preserves important waypoints
        smoothed = Path()
        smoothed.header = path.header

        # Keep start and end points
        smoothed.poses.append(path.poses[0])

        # Apply smoothing to intermediate points
        for i in range(1, len(path.poses) - 1):
            prev_point = path.poses[i-1].pose.position
            curr_point = path.poses[i].pose.position
            next_point = path.poses[i+1].pose.position

            # Calculate smoothed position
            smoothed_x = (prev_point.x + 2*curr_point.x + next_point.x) / 4.0
            smoothed_y = (prev_point.y + 2*curr_point.y + next_point.y) / 4.0

            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = smoothed_x
            pose.pose.position.y = smoothed_y
            pose.pose.position.z = 0.0
            pose.pose.orientation.w = 1.0
            smoothed.poses.append(pose)

        # Keep end point
        if len(path.poses) > 1:
            smoothed.poses.append(path.poses[-1])

        return smoothed

    def adjust_path_spacing(self, path: Path) -> Path:
        """
        Adjust path point spacing to match bipedal step constraints
        """
        if len(path.poses) <= 1:
            return path

        adjusted_path = Path()
        adjusted_path.header = path.header

        # Add start point
        adjusted_path.poses.append(path.poses[0])

        i = 0
        while i < len(path.poses) - 1:
            current_pos = adjusted_path.poses[-1].pose.position
            j = i + 1

            # Find next point that's at least the minimum step distance away
            while j < len(path.poses):
                next_pos = path.poses[j].pose.position
                dist = math.sqrt((next_pos.x - current_pos.x)**2 + (next_pos.y - current_pos.y)**2)

                if dist >= self.bipedal_constraints['min_step_length']:
                    # Add this point if it's within max step distance
                    if dist <= self.bipedal_constraints['max_step_length']:
                        adjusted_path.poses.append(path.poses[j])
                        i = j
                        break
                    else:
                        # If too far, interpolate points along the path
                        num_intermediate = int(dist / self.bipedal_constraints['min_step_length'])
                        for k in range(1, num_intermediate):
                            ratio = k / num_intermediate
                            interp_x = current_pos.x + ratio * (next_pos.x - current_pos.x)
                            interp_y = current_pos.y + ratio * (next_pos.y - current_pos.y)

                            pose = PoseStamped()
                            pose.header = path.header
                            pose.pose.position.x = interp_x
                            pose.pose.position.y = interp_y
                            pose.pose.position.z = 0.0
                            pose.pose.orientation.w = 1.0
                            adjusted_path.poses.append(pose)

                        adjusted_path.poses.append(path.poses[j])
                        i = j
                        break
                j += 1

            if j >= len(path.poses):
                # Reached end without finding suitable point, add the last point
                if path.poses[-1] != adjusted_path.poses[-1]:
                    adjusted_path.poses.append(path.poses[-1])
                break

        return adjusted_path
```

## 11.7 Integration with Humanoid Perception Systems

### Perception Integration for Navigation
```python
# humanoid_perception_integration.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud2, Image
from geometry_msgs.msg import Twist
from visualization_msgs.msg import MarkerArray
from std_msgs.msg import Bool
import numpy as np
import math

class HumanoidPerceptionIntegrator(Node):
    """
    Integrates humanoid-specific perception systems with Nav2
    """

    def __init__(self):
        super().__init__('humanoid_perception_integrator')

        # Subscriptions for humanoid sensors
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10
        )
        self.depth_sub = self.create_subscription(
            Image, '/camera/depth/image_rect_raw', self.depth_callback, 10
        )
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10
        )
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )

        # Publishers for fused perception data
        self.obstacle_pub = self.create_publisher(
            MarkerArray, '/perception/obstacles', 10
        )
        self.traversable_pub = self.create_publisher(
            MarkerArray, '/perception/traversable', 10
        )
        self.step_height_pub = self.create_publisher(
            MarkerArray, '/perception/step_heights', 10
        )

        # Navigation state
        self.current_odom = None
        self.imu_data = None
        self.depth_image = None
        self.traversable_areas = []

        # Timer for processing loop
        self.process_timer = self.create_timer(0.1, self.process_perception_data)

    def scan_callback(self, msg):
        """Process laser scan data for navigation"""
        # Process LIDAR data to identify obstacles and traversable areas
        obstacles = self.extract_obstacles_from_scan(msg)
        traversable = self.extract_traversable_from_scan(msg)

        # Publish obstacle markers for visualization
        obstacle_markers = self.create_obstacle_markers(obstacles)
        self.obstacle_pub.publish(obstacle_markers)

        # Store for fusion with other sensors
        self.processed_scan = {
            'obstacles': obstacles,
            'traversable': traversable
        }

    def depth_callback(self, msg):
        """Process depth camera data for step height detection"""
        # Convert ROS image to numpy array
        # This is a simplified representation
        depth_data = self.ros_image_to_numpy(msg)

        # Analyze depth data for step heights and traversable surfaces
        step_heights = self.analyze_step_heights(depth_data)
        self.step_height_pub.publish(self.create_step_height_markers(step_heights))

    def imu_callback(self, msg):
        """Process IMU data for balance and orientation"""
        self.imu_data = {
            'orientation': msg.orientation,
            'angular_velocity': msg.angular_velocity,
            'linear_acceleration': msg.linear_acceleration
        }

    def odom_callback(self, msg):
        """Process odometry data"""
        self.current_odom = msg

    def process_perception_data(self):
        """Fusion of perception data for navigation"""
        if not all([self.current_odom, self.imu_data, hasattr(self, 'processed_scan')]):
            return

        # Fuse sensor data to create comprehensive environment model
        environment_model = self.fuse_sensor_data()

        # Update costmaps based on fused perception
        self.update_costmaps(environment_model)

        # Check for navigation safety based on perception
        self.check_navigation_safety(environment_model)

    def extract_obstacles_from_scan(self, scan_msg):
        """Extract obstacle information from laser scan"""
        obstacles = []

        for i, range_val in enumerate(scan_msg.ranges):
            if not math.isnan(range_val) and range_val < scan_msg.range_max:
                angle = scan_msg.angle_min + i * scan_msg.angle_increment
                x = range_val * math.cos(angle)
                y = range_val * math.sin(angle)

                # Filter out ground plane and low obstacles that can be stepped over
                if range_val > 0.1:  # Minimum obstacle height for bipedal
                    obstacles.append((x, y, range_val))

        return obstacles

    def extract_traversable_from_scan(self, scan_msg):
        """Extract traversable area information from laser scan"""
        traversable = []

        for i, range_val in enumerate(scan_msg.ranges):
            if math.isnan(range_val) or range_val > 2.0:  # Beyond sensor range or far objects
                angle = scan_msg.angle_min + i * scan_msg.angle_increment
                x = range_val * math.cos(angle) if not math.isnan(range_val) else 10.0 * math.cos(angle)
                y = range_val * math.sin(angle) if not math.isnan(range_val) else 10.0 * math.sin(angle)

                traversable.append((x, y))

        return traversable

    def analyze_step_heights(self, depth_data):
        """Analyze depth data for step height and traversability"""
        # This would implement complex computer vision algorithms
        # to detect stairs, curbs, and other step-height features
        step_heights = []

        # Simplified implementation
        height_map = self.compute_height_map(depth_data)

        # Identify potential step locations
        for y in range(0, height_map.shape[0], 10):  # Sample every 10 pixels
            for x in range(0, height_map.shape[1], 10):
                height = height_map[y, x]
                if 0.05 < height < 0.3:  # Potential step height
                    step_heights.append((x, y, height))

        return step_heights

    def fuse_sensor_data(self):
        """Fuse data from multiple sensors for navigation"""
        # Combine LIDAR, depth camera, and IMU data
        environment = {
            'obstacles': getattr(self, 'processed_scan', {}).get('obstacles', []),
            'step_heights': [],  # From depth camera
            'balance_state': self.get_balance_state(),
            'traversable_ground': getattr(self, 'processed_scan', {}).get('traversable', [])
        }

        return environment

    def update_costmaps(self, environment_model):
        """Update Nav2 costmaps based on perception data"""
        # This would interface with Nav2's costmap system
        # to update traversability based on fused perception
        pass

    def check_navigation_safety(self, environment_model):
        """Check if navigation is safe based on perception"""
        # Check for obstacles in planned path
        # Check for safe step heights
        # Check for balance stability
        pass

    def create_obstacle_markers(self, obstacles):
        """Create visualization markers for obstacles"""
        from visualization_msgs.msg import Marker, MarkerArray
        from geometry_msgs.msg import Point

        marker_array = MarkerArray()

        for i, (x, y, dist) in enumerate(obstacles):
            marker = Marker()
            marker.header.frame_id = "map"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = "obstacles"
            marker.id = i
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD

            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = 0.5
            marker.pose.orientation.w = 1.0

            marker.scale.x = 0.2  # Diameter
            marker.scale.y = 0.2
            marker.scale.z = 1.0  # Height

            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0
            marker.color.a = 0.8

            marker_array.markers.append(marker)

        return marker_array
```

## 11.8 Simulation and Testing

### Gazebo Simulation for Bipedal Navigation
```xml
<!-- bipedal_navigation_simulation.launch.py -->
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')

    return LaunchDescription([
        # Declare launch arguments
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=[FindPackageShare('my_robot_navigation'), '/config/nav2_params.yaml'],
            description='Full path to the ROS2 parameters file to use'
        ),

        # Launch Gazebo
        IncludeLaunchDescription(
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])
        ),

        # Spawn robot model
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'humanoid_robot',
                '-topic', 'robot_description',
                '-x', '0.0',
                '-y', '0.0',
                '-z', '1.0'
            ],
            output='screen'
        ),

        # Launch robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}]
        ),

        # Launch Nav2 stack with bipedal configuration
        IncludeLaunchDescription(
            PathJoinSubstitution([
                FindPackageShare('nav2_bringup'),
                'launch',
                'navigation_launch.py'
            ]),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'params_file': params_file
            }.items()
        ),

        # Launch RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=[
                '-d',
                PathJoinSubstitution([
                    FindPackageShare('my_robot_navigation'),
                    'rviz',
                    'bipedal_navigation.rviz'
                ])
            ],
            parameters=[{'use_sim_time': use_sim_time}]
        )
    ])
```

## 11.9 Performance Optimization and Validation

### Navigation Performance Metrics
```python
# navigation_performance_evaluator.py
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Path, Odometry
from std_msgs.msg import Float32
import math
import time
import statistics

class NavigationPerformanceEvaluator(Node):
    """
    Evaluate navigation performance for bipedal robots
    """

    def __init__(self):
        super().__init__('navigation_performance_evaluator')

        # Subscriptions
        self.path_sub = self.create_subscription(
            Path, '/plan', self.path_callback, 10
        )
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel_nav', self.cmd_vel_callback, 10
        )

        # Publishers for metrics
        self.path_efficiency_pub = self.create_publisher(
            Float32, '/metrics/path_efficiency', 10
        )
        self.navigation_time_pub = self.create_publisher(
            Float32, '/metrics/navigation_time', 10
        )
        self.energy_efficiency_pub = self.create_publisher(
            Float32, '/metrics/energy_efficiency', 10
        )

        # Metrics storage
        self.start_time = None
        self.path_start_pos = None
        self.current_pos = None
        self.path_length = 0.0
        self.actual_distance = 0.0
        self.previous_pos = None
        self.cmd_vel_history = []

        # Timer for metric calculation
        self.metrics_timer = self.create_timer(1.0, self.calculate_metrics)

    def path_callback(self, msg):
        """Process planned path for efficiency calculation"""
        if len(msg.poses) > 1:
            # Calculate planned path length
            self.path_length = 0.0
            for i in range(1, len(msg.poses)):
                p1 = msg.poses[i-1].pose.position
                p2 = msg.poses[i].pose.position
                dist = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
                self.path_length += dist

            # Store start position
            self.path_start_pos = msg.poses[0].pose.position if msg.poses else None

    def odom_callback(self, msg):
        """Process odometry for actual path tracking"""
        self.current_pos = msg.pose.pose.position

        if self.previous_pos and self.current_pos:
            # Calculate distance traveled
            dist = math.sqrt(
                (self.current_pos.x - self.previous_pos.x)**2 +
                (self.current_pos.y - self.previous_pos.y)**2
            )
            self.actual_distance += dist

        self.previous_pos = self.current_pos

        # Start timing when robot begins moving
        if not self.start_time and self.path_start_pos and self.current_pos:
            start_dist = math.sqrt(
                (self.current_pos.x - self.path_start_pos.x)**2 +
                (self.current_pos.y - self.path_start_pos.y)**2
            )
            if start_dist > 0.1:  # Robot has started moving
                self.start_time = self.get_clock().now().nanoseconds / 1e9

    def cmd_vel_callback(self, msg):
        """Store command velocities for energy calculation"""
        self.cmd_vel_history.append({
            'linear': math.sqrt(msg.linear.x**2 + msg.linear.y**2),
            'angular': abs(msg.angular.z),
            'timestamp': self.get_clock().now().nanoseconds / 1e9
        })

    def calculate_metrics(self):
        """Calculate and publish navigation performance metrics"""
        if self.path_length > 0 and self.actual_distance > 0:
            # Path efficiency (actual path length / optimal path length)
            path_efficiency = Float32()
            path_efficiency.data = self.path_length / self.actual_distance if self.actual_distance > 0 else 0.0
            self.path_efficiency_pub.publish(path_efficiency)

            # Navigation time
            if self.start_time:
                nav_time = Float32()
                nav_time.data = self.get_clock().now().nanoseconds / 1e9 - self.start_time
                self.navigation_time_pub.publish(nav_time)

            # Energy efficiency (simplified calculation)
            energy_efficiency = Float32()
            if len(self.cmd_vel_history) > 10:  # Need sufficient data
                avg_linear_vel = statistics.mean([v['linear'] for v in self.cmd_vel_history[-10:]])
                avg_angular_vel = statistics.mean([v['angular'] for v in self.cmd_vel_history[-10:]])

                # Simplified energy calculation
                energy_usage = avg_linear_vel * 1.0 + avg_angular_vel * 0.5
                energy_efficiency.data = 1.0 / (energy_usage + 0.01)  # Higher is better
            else:
                energy_efficiency.data = 0.0

            self.energy_efficiency_pub.publish(energy_efficiency)

    def reset_metrics(self):
        """Reset all metrics for new navigation task"""
        self.start_time = None
        self.path_start_pos = None
        self.current_pos = None
        self.path_length = 0.0
        self.actual_distance = 0.0
        self.previous_pos = None
        self.cmd_vel_history = []
```

## 11.10 Troubleshooting and Best Practices

### Common Issues and Solutions
- **Path Oscillation**: Implement proper smoothing and hysteresis
- **Balance Instability**: Ensure proper center of mass control
- **Step Planning Failures**: Validate step constraints and terrain
- **Integration Problems**: Verify proper TF trees and message timing

### Best Practices for Bipedal Navigation
- **Gradual Acceleration**: Smooth velocity transitions for stability
- **Balance-First Approach**: Prioritize balance over speed
- **Terrain Classification**: Adapt gait patterns to terrain type
- **Recovery Behaviors**: Implement robust failure recovery
- **Safety Margins**: Maintain conservative safety margins

## 11.11 Exercises and Activities

### Exercise 1: Bipedal Nav2 Configuration
Configure Nav2 for a simulated bipedal robot. Adjust costmap parameters and controller settings for bipedal-specific constraints.

### Exercise 2: Path Planning with Step Constraints
Implement and test path planning algorithms that consider bipedal step length and height constraints. Compare with traditional path planning.

### Exercise 3: Gait Controller Integration
Integrate a simple gait controller with Nav2 to convert navigation commands to bipedal walking patterns.

### Exercise 4: Perception Integration
Integrate depth camera perception with Nav2 for step height detection and terrain classification for bipedal navigation.

## 11.12 Chapter Summary

This chapter explored the adaptation of Navigation2 (Nav2) for bipedal humanoid robots, addressing the unique challenges of legged locomotion compared to wheeled navigation. We covered custom costmap configurations, bipedal-specific controllers, path planning algorithms considering step constraints, and integration with humanoid perception systems. The chapter emphasized the importance of balance, gait patterns, and terrain adaptability in creating robust navigation systems for bipedal robots.

Successfully adapting Nav2 for bipedal robots requires careful consideration of dynamic stability, step planning, and the integration of specialized controllers that account for the unique kinematic and dynamic properties of legged locomotion.

## Key Terms and Definitions

- **Navigation2 (Nav2)**: ROS 2 navigation framework for mobile robots
- **Bipedal Locomotion**: Two-legged walking motion
- **Step Planning**: Planning individual steps for stable walking
- **Center of Mass (CoM)**: Point where robot's mass is concentrated
- **Zero Moment Point (ZMP)**: Point where net moment of ground reaction force is zero
- **Support Polygon**: Convex hull of ground contact points
- **Gait Pattern**: Rhythmic pattern of leg movements during walking
- **Dynamic Balance**: Maintaining balance during motion
- **Static Balance**: Maintaining balance while stationary
- **Costmap**: 2D or 3D representation of environment for navigation
- **Path Planning**: Computing optimal paths from start to goal
- **Trajectory Following**: Following planned paths with control algorithms
- **Behavior Trees**: Task execution framework in Nav2
- **Inverse Kinematics**: Calculating joint angles for desired end-effector positions
- **Stance Phase**: When foot is in contact with ground
- **Swing Phase**: When foot is moving through air
- **Step Height**: Vertical displacement during step
- **Step Length**: Horizontal distance of each step
- **Gait Frequency**: Steps per unit time

## Further Reading

1. Navigation2 Documentation: https://navigation.ros.org/
2. "Humanoid Robotics: A Reference" by Ambarish Goswami and Prahlad Vadakkepat
3. "Introduction to Humanoid Robotics" by Shuuji Kajita
4. ROS Navigation Tutorials: http://wiki.ros.org/navigation/Tutorials
5. "Robotics: Modelling, Planning and Control" by Siciliano et al.

## QA Checklist
- [ ] Chapter content accurately describes Nav2 for bipedal navigation
- [ ] Bipedal-specific navigation challenges are thoroughly explained
- [ ] Custom controller implementation is properly covered
- [ ] Path planning with bipedal constraints is addressed
- [ ] Perception integration is explained
- [ ] Performance optimization techniques are mentioned
- [ ] Troubleshooting and best practices are included
- [ ] Exercises are relevant and test understanding
- [ ] Key terms are defined and explained
- [ ] Content aligns with the module's focus on Nav2 for bipedal robots
- [ ] Links to further reading are valid
- [ ] Chapter summary effectively summarizes key concepts