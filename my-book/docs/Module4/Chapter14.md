# Chapter 14: Cognitive Planning: Using LLMs to translate natural language into ROS 2 actions

## Learning Objectives
After completing this chapter, students will be able to:
- Integrate Large Language Models (LLMs) with ROS 2 for cognitive planning
- Parse and interpret natural language commands for robotic tasks
- Design prompt engineering strategies for robotics applications
- Create action planning sequences from high-level natural language
- Implement safety constraints and validation for LLM-generated plans
- Evaluate and refine LLM-based cognitive planning systems
- Handle ambiguous or complex natural language commands
- Optimize LLM performance for real-time robotic applications

## 14.1 Introduction to Cognitive Planning with LLMs

Cognitive planning in robotics refers to the process of translating high-level, abstract goals expressed in natural language into executable sequences of robotic actions. Large Language Models (LLMs) have emerged as powerful tools for this translation, enabling robots to understand and execute complex tasks described in human-friendly language.

### The Cognitive Planning Pipeline
The cognitive planning process involves several key stages:
1. **Natural Language Understanding**: Parsing and interpreting human commands
2. **World Modeling**: Understanding the current state of the environment
3. **Action Planning**: Creating a sequence of executable actions
4. **Execution Monitoring**: Supervising plan execution and handling exceptions
5. **Feedback Generation**: Communicating results back to the human operator

### LLMs in Robotics Context
Large Language Models bring several advantages to robotic cognitive planning:
- **Natural Interaction**: Enable communication using everyday language
- **Context Understanding**: Leverage learned world knowledge for task interpretation
- **Flexibility**: Handle a wide range of task specifications and environments
- **Abstraction**: Bridge high-level goals with low-level robot commands

## 14.2 LLM Integration with ROS 2

### LLM Selection and Setup
For robotics applications, several LLM options are available:

#### OpenAI GPT Models
```python
# OpenAI integration for cognitive planning
import openai
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose
import json
import time

class LLMCognitivePlanner(Node):
    def __init__(self):
        super().__init__('llm_cognitive_planner')

        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(api_key=self.get_openai_api_key())

        # Publishers and subscribers
        self.command_sub = self.create_subscription(
            String, '/natural_language_command', self.command_callback, 10
        )
        self.plan_pub = self.create_publisher(
            String, '/generated_plan', 10
        )
        self.status_pub = self.create_publisher(
            String, '/planner_status', 10
        )

        # Parameters
        self.declare_parameter('model_name', 'gpt-4-turbo')
        self.declare_parameter('max_tokens', 1000)
        self.declare_parameter('temperature', 0.3)

        self.model_name = self.get_parameter('model_name').value
        self.max_tokens = self.get_parameter('max_tokens').value
        self.temperature = self.get_parameter('temperature').value

        # World state information
        self.world_state = {
            'objects': [],
            'locations': [],
            'robot_state': {},
            'capabilities': []
        }

    def get_openai_api_key(self):
        """Get OpenAI API key from environment or parameters"""
        # In a real system, this would be securely stored
        import os
        return os.getenv('OPENAI_API_KEY', 'your-api-key-here')

    def command_callback(self, msg):
        """Process natural language command and generate plan"""
        natural_command = msg.data
        self.get_logger().info(f'Received command: {natural_command}')

        # Update world state (in a real system, this would come from perception)
        self.update_world_state()

        # Generate plan using LLM
        plan = self.generate_plan(natural_command)

        if plan:
            # Publish generated plan
            plan_msg = String()
            plan_msg.data = json.dumps(plan)
            self.plan_pub.publish(plan_msg)

            self.get_logger().info(f'Generated plan: {plan}')
        else:
            self.get_logger().error('Failed to generate plan')

    def update_world_state(self):
        """Update world state from perception and other sources"""
        # In a real implementation, this would integrate with perception systems
        # to get current world information
        self.world_state = {
            'objects': [
                {'name': 'cup', 'location': 'kitchen_table', 'status': 'available'},
                {'name': 'book', 'location': 'office_desk', 'status': 'available'},
                {'name': 'keys', 'location': 'entrance_table', 'status': 'available'}
            ],
            'locations': [
                {'name': 'kitchen', 'waypoint': 'kitchen_waypoint'},
                {'name': 'office', 'waypoint': 'office_waypoint'},
                {'name': 'living_room', 'waypoint': 'living_room_waypoint'},
                {'name': 'bedroom', 'waypoint': 'bedroom_waypoint'}
            ],
            'robot_state': {
                'current_location': 'home_base',
                'battery_level': 0.85,
                'manipulator_status': 'available'
            },
            'capabilities': [
                'navigation',
                'object_manipulation',
                'speech_recognition',
                'object_detection'
            ]
        }

    def generate_plan(self, natural_command):
        """Generate action plan from natural language using LLM"""
        try:
            # Create system message with context
            system_message = f"""
            You are a cognitive planning assistant for a humanoid robot. Your task is to convert natural language commands into executable action plans.

            The robot has the following capabilities: {', '.join(self.world_state['capabilities'])}
            Current world state:
            - Objects: {self.world_state['objects']}
            - Locations: {self.world_state['locations']}
            - Robot state: {self.world_state['robot_state']}

            Generate a plan as a JSON array of action objects. Each action should have:
            - type: The type of action (navigate, pick, place, speak, etc.)
            - parameters: Relevant parameters for the action
            - description: Brief description of what the action does

            Available action types:
            - navigate: Move to a specific location
            - pick: Pick up an object
            - place: Place an object at a location
            - speak: Speak a message
            - detect: Detect objects in the environment
            - wait: Wait for a condition

            Example response format:
            [
                {{
                    "type": "navigate",
                    "parameters": {{"location": "kitchen"}},
                    "description": "Navigate to the kitchen"
                }},
                {{
                    "type": "pick",
                    "parameters": {{"object": "cup", "location": "kitchen_table"}},
                    "description": "Pick up the cup from the kitchen table"
                }}
            ]
            """

            # Create user message with the natural command
            user_message = f"Convert this command to an action plan: '{natural_command}'"

            # Call the LLM
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract and parse the response
            plan_text = response.choices[0].message.content.strip()

            # Remove any markdown formatting if present
            if plan_text.startswith('```json'):
                plan_text = plan_text[7:]  # Remove ```json
            if plan_text.endswith('```'):
                plan_text = plan_text[:-3]  # Remove ```

            plan = json.loads(plan_text)
            return plan

        except json.JSONDecodeError:
            self.get_logger().error(f'Failed to parse LLM response as JSON: {plan_text}')
            return None
        except Exception as e:
            self.get_logger().error(f'Error generating plan: {e}')
            return None
```

#### Open-Source LLMs with Hugging Face
```python
# Hugging Face integration for cognitive planning
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json

class HuggingFaceCognitivePlanner(Node):
    def __init__(self):
        super().__init__('hf_cognitive_planner')

        # Initialize local LLM
        self.model_name = "microsoft/DialoGPT-medium"  # Example model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

        # Add padding token if needed
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Publishers and subscribers
        self.command_sub = self.create_subscription(
            String, '/natural_language_command', self.command_callback, 10
        )
        self.plan_pub = self.create_publisher(
            String, '/generated_plan', 10
        )

    def generate_plan_hf(self, natural_command):
        """Generate plan using Hugging Face model"""
        try:
            # Create prompt for the model
            prompt = f"""
            Natural language command: {natural_command}

            Convert this to a JSON plan with action sequences for a robot.
            Example format:
            [
                {{"type": "navigate", "parameters": {{"location": "kitchen"}}}},
                {{"type": "pick", "parameters": {{"object": "cup"}}}}
            ]

            Plan:
            """

            # Tokenize the input
            inputs = self.tokenizer.encode(prompt, return_tensors='pt')

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 200,
                    num_return_sequences=1,
                    temperature=0.7,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Decode the response
            response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract the plan part from the response
            plan_start = response_text.rfind("Plan:") + len("Plan:")
            plan_text = response_text[plan_start:].strip()

            # Parse the plan
            plan = json.loads(plan_text)
            return plan

        except Exception as e:
            self.get_logger().error(f'Error generating plan with Hugging Face model: {e}')
            return None
```

## 14.3 Natural Language Command Processing

### Command Parsing and Understanding
```python
# Advanced command parsing and understanding
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ParsedCommand:
    action: str
    objects: List[str]
    locations: List[str]
    parameters: Dict[str, any]
    original_command: str

class NaturalLanguageParser:
    def __init__(self):
        # Define action patterns
        self.action_patterns = {
            'navigate': [
                r'go to (?P<location>\w+)',
                r'move to (?P<location>\w+)',
                r'go (?P<direction>\w+)',
                r'walk to (?P<location>\w+)'
            ],
            'pick': [
                r'pick up (?P<object>\w+)',
                r'grab (?P<object>\w+)',
                r'get (?P<object>\w+)',
                r'take (?P<object>\w+)'
            ],
            'place': [
                r'put (?P<object>\w+) in (?P<location>\w+)',
                r'place (?P<object>\w+) on (?P<location>\w+)',
                r'drop (?P<object>\w+) at (?P<location>\w+)'
            ],
            'clean': [
                r'clean the (?P<room>\w+)',
                r'tidy up (?P<room>\w+)',
                r'organize (?P<room>\w+)'
            ],
            'find': [
                r'find (?P<object>\w+)',
                r'locate (?P<object>\w+)',
                r'where is (?P<object>\w+)'
            ]
        }

        # Location synonyms
        self.location_synonyms = {
            'kitchen': ['kitchen', 'cooking area', 'food area'],
            'living room': ['living room', 'sitting room', 'lounge'],
            'bedroom': ['bedroom', 'sleeping room', 'bed room'],
            'office': ['office', 'study', 'work room'],
            'bathroom': ['bathroom', 'restroom', 'toilet'],
            'dining room': ['dining room', 'dining area', 'eat room']
        }

        # Object synonyms
        self.object_synonyms = {
            'cup': ['cup', 'mug', 'glass'],
            'book': ['book', 'novel', 'text'],
            'keys': ['keys', 'key', 'house keys'],
            'phone': ['phone', 'mobile', 'cell phone'],
            'bottle': ['bottle', 'water bottle', 'drink'],
            'food': ['food', 'snack', 'meal']
        }

    def parse_command(self, command: str) -> Optional[ParsedCommand]:
        """Parse natural language command into structured format"""
        command_lower = command.lower().strip()

        # Try to match against action patterns
        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command_lower)
                if match:
                    # Extract matched groups
                    groups = match.groupdict()

                    # Find objects and locations in the command
                    objects = self.extract_objects(command_lower)
                    locations = self.extract_locations(command_lower)

                    # Add matched entities to the lists
                    for key, value in groups.items():
                        if key in ['object', 'room']:
                            objects.append(value)
                        elif key in ['location']:
                            locations.append(value)

                    return ParsedCommand(
                        action=action,
                        objects=objects,
                        locations=locations,
                        parameters=groups,
                        original_command=command
                    )

        # If no specific pattern matches, return a generic command
        return ParsedCommand(
            action='unknown',
            objects=self.extract_objects(command_lower),
            locations=self.extract_locations(command_lower),
            parameters={'raw_command': command},
            original_command=command
        )

    def extract_objects(self, command: str) -> List[str]:
        """Extract potential objects from command"""
        objects = []

        # Look for known objects
        for obj, synonyms in self.object_synonyms.items():
            for synonym in synonyms:
                if synonym in command:
                    if obj not in objects:
                        objects.append(obj)

        # Also look for simple noun patterns
        # This is a simplified approach - in practice, you'd use NLP libraries
        simple_objects = re.findall(r'\b(cup|book|keys|phone|bottle|food|water|coffee|tea|plate|fork|spoon|napkin|towel|clothes|toy|game|tool|pen|pencil|paper|box|bag|shoe|hat|coat|glasses|watch|wallet|purse)\b', command)
        for obj in simple_objects:
            if obj not in objects:
                objects.append(obj)

        return objects

    def extract_locations(self, command: str) -> List[str]:
        """Extract potential locations from command"""
        locations = []

        # Look for known locations
        for loc, synonyms in self.location_synonyms.items():
            for synonym in synonyms:
                if synonym in command:
                    if loc not in locations:
                        locations.append(loc)

        # Also look for simple location patterns
        simple_locations = re.findall(r'\b(kitchen|living room|bedroom|office|bathroom|dining room|hallway|garage|garden|yard|patio|balcony|entrance|exit|room|area|space)\b', command)
        for loc in simple_locations:
            if loc not in locations:
                locations.append(loc)

        return locations

    def validate_command(self, parsed_command: ParsedCommand) -> Tuple[bool, str]:
        """Validate if the parsed command is feasible"""
        if parsed_command.action == 'unknown':
            return False, "Unknown action in command"

        # Check if required objects/locations exist in world state
        # This would be connected to the actual world state in a real implementation

        # Check action-specific constraints
        if parsed_command.action == 'pick':
            if not parsed_command.objects:
                return False, "Pick action requires an object"

        if parsed_command.action == 'navigate':
            if not parsed_command.locations:
                return False, "Navigate action requires a destination"

        return True, "Command is valid"
```

### Advanced Command Processing Node
```python
# Advanced cognitive planning node with LLM integration
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
import json
import time

class AdvancedCognitivePlanner(Node):
    def __init__(self):
        super().__init__('advanced_cognitive_planner')

        # Subscriptions
        self.command_sub = self.create_subscription(
            String, '/natural_language_command', self.command_callback, 10
        )
        self.world_state_sub = self.create_subscription(
            String, '/world_state', self.world_state_callback, 10
        )

        # Publishers
        self.plan_pub = self.create_publisher(
            String, '/detailed_plan', 10
        )
        self.status_pub = self.create_publisher(
            String, '/cognitive_planner_status', 10
        )

        # Action clients
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Initialize components
        self.llm_planner = LLMCognitivePlanner()  # Reuse from earlier
        self.nlp_parser = NaturalLanguageParser()
        self.world_state = {}
        self.current_plan = None
        self.plan_execution_status = 'idle'

    def command_callback(self, msg):
        """Process natural language command with advanced cognitive planning"""
        command = msg.data
        self.get_logger().info(f'Processing command: {command}')

        # Publish status
        status_msg = String()
        status_msg.data = f'Processing command: {command}'
        self.status_pub.publish(status_msg)

        # Parse the command
        parsed_command = self.nlp_parser.parse_command(command)

        # Validate the command
        is_valid, validation_msg = self.nlp_parser.validate_command(parsed_command)
        if not is_valid:
            self.get_logger().warn(f'Command validation failed: {validation_msg}')
            self.publish_status(f'Command invalid: {validation_msg}')
            return

        # Generate detailed plan using LLM
        detailed_plan = self.generate_detailed_plan(parsed_command)

        if detailed_plan:
            # Publish the detailed plan
            plan_msg = String()
            plan_msg.data = json.dumps(detailed_plan)
            self.plan_pub.publish(plan_msg)

            self.current_plan = detailed_plan
            self.get_logger().info(f'Generated detailed plan: {detailed_plan}')

            # Optionally execute the plan immediately
            self.execute_plan(detailed_plan)
        else:
            self.get_logger().error('Failed to generate detailed plan')
            self.publish_status('Failed to generate plan')

    def world_state_callback(self, msg):
        """Update world state from perception systems"""
        try:
            self.world_state = json.loads(msg.data)
            self.get_logger().debug(f'Updated world state: {len(self.world_state)} items')
        except json.JSONDecodeError:
            self.get_logger().error('Failed to parse world state message')

    def generate_detailed_plan(self, parsed_command):
        """Generate detailed execution plan using LLM"""
        try:
            # Create a more detailed prompt for the LLM
            world_state_str = json.dumps(self.world_state, indent=2)

            prompt = f"""
            You are a detailed cognitive planning assistant for a humanoid robot.

            Natural command: {parsed_command.original_command}
            Parsed command: {parsed_command.action} with objects {parsed_command.objects} and locations {parsed_command.locations}

            Current world state:
            {world_state_str}

            Generate a detailed execution plan as a JSON array of action objects. Each action should have:
            - type: The type of action
            - parameters: All necessary parameters for execution
            - description: Detailed description of the action
            - preconditions: Conditions that must be true before executing
            - expected_effects: Effects of the action on the world state
            - priority: Priority level (1-5, 5 being highest)

            Available action types:
            - navigate: Move to a specific location
            - pick: Pick up an object
            - place: Place an object at a location
            - detect: Detect objects in the environment
            - grasp: Grasp an object
            - release: Release an object
            - speak: Speak a message
            - wait: Wait for a condition

            Example detailed action:
            {{
                "type": "navigate",
                "parameters": {{"target_location": "kitchen", "waypoint": "kitchen_waypoint"}},
                "description": "Navigate to the kitchen area",
                "preconditions": [{{"robot_battery_level": {{">": 0.2}}}}, {{"robot_available": true}}],
                "expected_effects": [{{"robot_location": "kitchen"}}],
                "priority": 5
            }}

            Detailed plan:
            """

            # Call LLM (this would use the actual LLM in a real implementation)
            # For this example, we'll simulate the response
            detailed_plan = self.simulate_llm_response(parsed_command)
            return detailed_plan

        except Exception as e:
            self.get_logger().error(f'Error generating detailed plan: {e}')
            return None

    def simulate_llm_response(self, parsed_command):
        """Simulate LLM response for demonstration purposes"""
        # In a real implementation, this would call the actual LLM
        # For now, we'll create appropriate plans based on the command

        if parsed_command.action == 'navigate':
            return [
                {
                    "type": "navigate",
                    "parameters": {"target_location": parsed_command.locations[0] if parsed_command.locations else "unknown"},
                    "description": f"Navigate to {parsed_command.locations[0] if parsed_command.locations else 'destination'}",
                    "preconditions": [{"robot_battery_level": {">": 0.2}}, {"robot_available": True}],
                    "expected_effects": [{"robot_location": parsed_command.locations[0] if parsed_command.locations else "unknown"}],
                    "priority": 5
                }
            ]
        elif parsed_command.action == 'pick':
            return [
                {
                    "type": "navigate",
                    "parameters": {"target_location": "object_location"},
                    "description": f"Navigate to the location of {parsed_command.objects[0] if parsed_command.objects else 'object'}",
                    "preconditions": [{"robot_battery_level": {">": 0.2}}, {"robot_available": True}],
                    "expected_effects": [{"robot_location": "object_location"}],
                    "priority": 5
                },
                {
                    "type": "detect",
                    "parameters": {"object_to_find": parsed_command.objects[0] if parsed_command.objects else "unknown"},
                    "description": f"Detect {parsed_command.objects[0] if parsed_command.objects else 'object'} in the environment",
                    "preconditions": [{"robot_camera_working": True}],
                    "expected_effects": [{"object_detected": parsed_command.objects[0] if parsed_command.objects else "unknown"}],
                    "priority": 4
                },
                {
                    "type": "pick",
                    "parameters": {"object": parsed_command.objects[0] if parsed_command.objects else "unknown"},
                    "description": f"Pick up {parsed_command.objects[0] if parsed_command.objects else 'object'}",
                    "preconditions": [{"object_detected": parsed_command.objects[0] if parsed_command.objects else "unknown"}, {"manipulator_available": True}],
                    "expected_effects": [{"object_held": parsed_command.objects[0] if parsed_command.objects else "unknown"}],
                    "priority": 5
                }
            ]
        else:
            # Default plan for unknown actions
            return [
                {
                    "type": "speak",
                    "parameters": {"message": f"I don't know how to {parsed_command.original_command}"},
                    "description": "Inform user about unknown command",
                    "preconditions": [{"speech_system_available": True}],
                    "expected_effects": [{"user_informed": True}],
                    "priority": 3
                }
            ]

    def execute_plan(self, plan):
        """Execute the generated plan step by step"""
        self.get_logger().info(f'Executing plan with {len(plan)} steps')

        for i, action in enumerate(plan):
            self.get_logger().info(f'Executing step {i+1}: {action["description"]}')

            success = self.execute_action(action)

            if not success:
                self.get_logger().error(f'Plan execution failed at step {i+1}')
                self.publish_status(f'Plan failed at step {i+1}: {action["description"]}')
                return False

            self.publish_status(f'Completed step {i+1}: {action["description"]}')

        self.get_logger().info('Plan execution completed successfully')
        self.publish_status('Plan execution completed successfully')
        return True

    def execute_action(self, action):
        """Execute a single action from the plan"""
        action_type = action['type']

        if action_type == 'navigate':
            return self.execute_navigation(action)
        elif action_type == 'pick':
            return self.execute_pick(action)
        elif action_type == 'place':
            return self.execute_place(action)
        elif action_type == 'speak':
            return self.execute_speak(action)
        elif action_type == 'detect':
            return self.execute_detect(action)
        else:
            self.get_logger().warn(f'Unknown action type: {action_type}')
            return False

    def execute_navigation(self, action):
        """Execute navigation action"""
        try:
            target_location = action['parameters'].get('target_location', 'unknown')

            # In a real implementation, this would use the navigation system
            # For simulation, we'll just return success
            self.get_logger().info(f'Navigating to {target_location}')

            # Wait for navigation to complete (simulated)
            time.sleep(2)

            return True
        except Exception as e:
            self.get_logger().error(f'Navigation execution failed: {e}')
            return False

    def execute_pick(self, action):
        """Execute pick action"""
        try:
            object_to_pick = action['parameters'].get('object', 'unknown')

            self.get_logger().info(f'Picking up {object_to_pick}')

            # Simulate pick action
            time.sleep(1)

            return True
        except Exception as e:
            self.get_logger().error(f'Pick execution failed: {e}')
            return False

    def execute_place(self, action):
        """Execute place action"""
        try:
            object_to_place = action['parameters'].get('object', 'unknown')
            location = action['parameters'].get('location', 'unknown')

            self.get_logger().info(f'Placing {object_to_place} at {location}')

            # Simulate place action
            time.sleep(1)

            return True
        except Exception as e:
            self.get_logger().error(f'Place execution failed: {e}')
            return False

    def execute_speak(self, action):
        """Execute speak action"""
        try:
            message = action['parameters'].get('message', '')

            self.get_logger().info(f'Speaking: {message}')

            # In a real implementation, this would use text-to-speech
            # For simulation, we just log the message

            return True
        except Exception as e:
            self.get_logger().error(f'Speak execution failed: {e}')
            return False

    def execute_detect(self, action):
        """Execute detect action"""
        try:
            object_to_find = action['parameters'].get('object_to_find', 'unknown')

            self.get_logger().info(f'Detecting {object_to_find}')

            # In a real implementation, this would use perception systems
            # For simulation, we'll assume detection succeeds
            time.sleep(1)

            return True
        except Exception as e:
            self.get_logger().error(f'Detect execution failed: {e}')
            return False

    def publish_status(self, status_message):
        """Publish status message"""
        status_msg = String()
        status_msg.data = status_message
        self.status_pub.publish(status_msg)
```

## 14.4 Prompt Engineering for Robotics

### Effective Prompt Design
```python
# Prompt engineering for robotics applications
class RoboticsPromptEngineer:
    def __init__(self):
        self.system_prompts = {}
        self.example_prompts = {}
        self.safety_constraints = []

    def create_system_prompt(self, robot_capabilities, world_knowledge, safety_rules):
        """Create a comprehensive system prompt for the LLM"""
        system_prompt = f"""
        You are an AI cognitive planner for a humanoid robot. Your role is to interpret natural language commands and generate safe, executable action plans.

        ROBOT CAPABILITIES:
        {robot_capabilities}

        WORLD KNOWLEDGE:
        {world_knowledge}

        SAFETY CONSTRAINTS:
        {safety_rules}

        ACTION PLANNING GUIDELINES:
        1. Always verify preconditions before executing actions
        2. Include error handling and fallback plans
        3. Respect physical limitations of the robot
        4. Consider battery life and operational constraints
        5. Prioritize safety above all other objectives
        6. Provide clear, executable action sequences
        7. Use available sensors and perception systems
        8. Account for uncertainty in the environment

        OUTPUT FORMAT:
        Respond with a JSON array of action objects. Each action must include:
        - type: The action type
        - parameters: All necessary parameters
        - description: Brief description
        - preconditions: Conditions that must be met
        - expected_effects: Expected outcomes

        Always respond with valid JSON only, no additional text or explanations.
        """
        return system_prompt

    def create_task_specific_prompt(self, task_type, context, constraints):
        """Create task-specific prompts for different types of commands"""
        if task_type == 'navigation':
            return f"""
            Task: Navigation Planning
            Context: {context}
            Constraints: {constraints}

            Plan a safe navigation route considering:
            - Obstacle avoidance
            - Energy efficiency
            - Time optimization
            - Safety margins
            - Known environmental features

            Output navigation plan as JSON with waypoints and safety checks.
            """
        elif task_type == 'manipulation':
            return f"""
            Task: Object Manipulation Planning
            Context: {context}
            Constraints: {constraints}

            Plan manipulation sequence considering:
            - Object properties (size, weight, fragility)
            - Robot end-effector capabilities
            - Safety during manipulation
            - Stable grasp planning
            - Collision avoidance

            Output manipulation plan as JSON with grasp poses and motion sequences.
            """
        elif task_type == 'cleaning':
            return f"""
            Task: Cleaning Task Planning
            Context: {context}
            Constraints: {constraints}

            Plan cleaning sequence considering:
            - Room layout and furniture
            - Types of surfaces to clean
            - Available cleaning tools
            - Safety around obstacles
            - Coverage optimization

            Output cleaning plan as JSON with cleaning paths and tool usage.
            """
        else:
            return f"""
            Task: General Robot Planning
            Context: {context}
            Constraints: {constraints}

            Generate appropriate action plan based on context and constraints.
            Output as JSON array of executable actions.
            """

    def apply_safety_filter(self, generated_plan):
        """Apply safety constraints to filter generated plans"""
        filtered_plan = []

        for action in generated_plan:
            # Check if action violates safety constraints
            if self.is_action_safe(action):
                filtered_plan.append(action)
            else:
                # Log safety violation and potentially generate alternative
                print(f"Action filtered for safety: {action}")

        return filtered_plan

    def is_action_safe(self, action):
        """Check if an action is safe to execute"""
        # This would contain actual safety checking logic
        # For now, we'll implement basic checks

        action_type = action.get('type', '')
        parameters = action.get('parameters', {})

        # Example safety checks
        if action_type == 'navigate':
            # Check if destination is in safe area
            target = parameters.get('target_location', '')
            if target in ['forbidden_area', 'dangerous_zone']:
                return False

        if action_type == 'manipulate':
            # Check if object is safe to manipulate
            obj = parameters.get('object', '')
            if obj in ['fragile_item', 'hazardous_material']:
                return False

        return True
```

## 14.5 Plan Validation and Safety

### Safety Constraint Implementation
```python
# Safety and validation system for LLM-generated plans
import time
from enum import Enum
from typing import List, Dict, Any

class SafetyLevel(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    NONE = 5

class PlanValidator:
    def __init__(self):
        self.safety_rules = self.load_safety_rules()
        self.known_dangerous_actions = [
            'move_to_dangerous_area',
            'manipulate_hazardous_material',
            'operate_in_forbidden_zone'
        ]
        self.robot_constraints = {
            'max_speed': 1.0,  # m/s
            'max_payload': 5.0,  # kg
            'max_operating_time': 8 * 3600,  # seconds
            'min_battery_for_tasks': 0.2,  # 20%
            'safe_distance_to_human': 0.5  # meters
        }

    def load_safety_rules(self):
        """Load safety rules from configuration"""
        return {
            'collision_avoidance': True,
            'human_safety': True,
            'environmental_protection': True,
            'robot_protection': True,
            'operational_limits': True
        }

    def validate_plan(self, plan: List[Dict[str, Any]], current_state: Dict[str, Any]) -> tuple[bool, List[str], List[Dict[str, Any]]]:
        """
        Validate a plan for safety and feasibility
        Returns: (is_valid, error_messages, modified_plan)
        """
        errors = []
        warnings = []
        modified_plan = plan.copy()

        # Check each action in the plan
        for i, action in enumerate(plan):
            action_errors, action_warnings, modified_action = self.validate_action(action, current_state, i)
            errors.extend([f"Action {i}: {error}" for error in action_errors])
            warnings.extend([f"Action {i}: {warning}" for warning in action_warnings])

            if modified_action != action:
                modified_plan[i] = modified_action

        # Check overall plan constraints
        plan_errors = self.check_plan_constraints(plan, current_state)
        errors.extend(plan_errors)

        is_valid = len(errors) == 0
        return is_valid, errors, modified_plan

    def validate_action(self, action: Dict[str, Any], current_state: Dict[str, Any], action_index: int) -> tuple[List[str], List[str], Dict[str, Any]]:
        """Validate a single action"""
        errors = []
        warnings = []
        modified_action = action.copy()

        action_type = action.get('type', '')
        parameters = action.get('parameters', {})

        # Check if action is dangerous
        if action_type in self.known_dangerous_actions:
            errors.append(f"Action '{action_type}' is classified as dangerous and cannot be executed")

        # Validate based on action type
        if action_type == 'navigate':
            nav_errors, nav_warnings = self.validate_navigation(action, current_state)
            errors.extend(nav_errors)
            warnings.extend(nav_warnings)

        elif action_type == 'pick':
            pick_errors, pick_warnings = self.validate_manipulation(action, current_state)
            errors.extend(pick_errors)
            warnings.extend(pick_warnings)

        elif action_type == 'place':
            place_errors, place_warnings = self.validate_manipulation(action, current_state)
            errors.extend(place_errors)
            warnings.extend(place_warnings)

        # Check preconditions
        preconditions = action.get('preconditions', [])
        for precondition in preconditions:
            if not self.check_precondition(precondition, current_state):
                errors.append(f"Precondition not met: {precondition}")

        return errors, warnings, modified_action

    def validate_navigation(self, action: Dict[str, Any], current_state: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """Validate navigation action"""
        errors = []
        warnings = []

        target_location = action['parameters'].get('target_location')
        if not target_location:
            errors.append("Navigation action missing target location")

        # Check if target is in safe area
        if current_state.get('safe_areas'):
            if target_location not in current_state['safe_areas']:
                errors.append(f"Navigation target '{target_location}' is not in safe areas")

        # Check battery for navigation
        battery_level = current_state.get('robot_state', {}).get('battery_level', 1.0)
        if battery_level < self.robot_constraints['min_battery_for_tasks']:
            errors.append("Insufficient battery for navigation task")

        return errors, warnings

    def validate_manipulation(self, action: Dict[str, Any], current_state: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """Validate manipulation action"""
        errors = []
        warnings = []

        obj_name = action['parameters'].get('object')
        if not obj_name:
            errors.append("Manipulation action missing object specification")

        # Check object properties if available
        if current_state.get('objects'):
            obj_info = next((obj for obj in current_state['objects'] if obj.get('name') == obj_name), None)
            if obj_info:
                weight = obj_info.get('weight', 0)
                if weight > self.robot_constraints['max_payload']:
                    errors.append(f"Object '{obj_name}' weighs {weight}kg, exceeding robot's max payload of {self.robot_constraints['max_payload']}kg")

        # Check if manipulator is available
        manipulator_status = current_state.get('robot_state', {}).get('manipulator_status', 'available')
        if manipulator_status != 'available':
            errors.append("Manipulator is not available for manipulation task")

        return errors, warnings

    def check_precondition(self, precondition: Dict[str, Any], current_state: Dict[str, Any]) -> bool:
        """Check if a precondition is satisfied"""
        # This is a simplified implementation
        # In practice, this would be more complex with various condition types
        for key, condition in precondition.items():
            current_value = self.get_nested_value(current_state, key)
            if not self.evaluate_condition(current_value, condition):
                return False
        return True

    def get_nested_value(self, obj: Dict[str, Any], key: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = key.split('.')
        current = obj
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current

    def evaluate_condition(self, value: Any, condition: Any) -> bool:
        """Evaluate a condition against a value"""
        if isinstance(condition, dict):
            # Handle comparison operators
            for op, expected in condition.items():
                if op == '>':
                    return value > expected
                elif op == '<':
                    return value < expected
                elif op == '>=':
                    return value >= expected
                elif op == '<=':
                    return value <= expected
                elif op == '==':
                    return value == expected
                elif op == '!=':
                    return value != expected
        else:
            # Direct equality check
            return value == condition

    def check_plan_constraints(self, plan: List[Dict[str, Any]], current_state: Dict[str, Any]) -> List[str]:
        """Check overall plan constraints"""
        errors = []

        # Check if plan is too long (time-wise)
        estimated_time = len(plan) * 10  # 10 seconds per action (rough estimate)
        if estimated_time > self.robot_constraints['max_operating_time']:
            errors.append(f"Plan estimated time ({estimated_time}s) exceeds max operating time ({self.robot_constraints['max_operating_time']}s)")

        # Check if plan requires unavailable resources
        required_capabilities = set()
        for action in plan:
            # In a real implementation, this would map actions to required capabilities
            pass

        return errors
```

## 14.6 Real-time Execution and Monitoring

### Plan Execution Monitor
```python
# Plan execution monitoring and adaptation
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class ExecutionStatus:
    action_index: int
    status: str  # 'pending', 'executing', 'completed', 'failed', 'interrupted'
    start_time: float
    end_time: Optional[float]
    error_message: Optional[str]
    progress: float  # 0.0 to 1.0

class PlanExecutionMonitor:
    def __init__(self, robot_interface, llm_interface):
        self.robot_interface = robot_interface
        self.llm_interface = llm_interface
        self.current_plan = None
        self.execution_status = []
        self.execution_thread = None
        self.stop_execution = threading.Event()
        self.adaptation_enabled = True

    def execute_plan(self, plan: List[Dict[str, Any]], callback: Optional[Callable] = None):
        """Execute a plan with monitoring"""
        self.current_plan = plan
        self.execution_status = []
        self.stop_execution.clear()

        # Initialize execution status for each action
        for i in range(len(plan)):
            self.execution_status.append(ExecutionStatus(
                action_index=i,
                status='pending',
                start_time=0.0,
                end_time=None,
                error_message=None,
                progress=0.0
            ))

        # Start execution in a separate thread
        self.execution_thread = threading.Thread(
            target=self._execute_plan_thread,
            args=(callback,)
        )
        self.execution_thread.start()

    def _execute_plan_thread(self, callback: Optional[Callable]):
        """Execute plan in a separate thread"""
        for i, action in enumerate(self.current_plan):
            if self.stop_execution.is_set():
                self.execution_status[i].status = 'interrupted'
                break

            # Update status
            self.execution_status[i].status = 'executing'
            self.execution_status[i].start_time = time.time()

            try:
                # Execute the action
                success = self.execute_single_action(action, i)

                if success:
                    self.execution_status[i].status = 'completed'
                    self.execution_status[i].end_time = time.time()
                    self.execution_status[i].progress = 1.0
                else:
                    self.execution_status[i].status = 'failed'
                    self.execution_status[i].end_time = time.time()
                    self.execution_status[i].error_message = 'Action execution failed'

                    # Check if we should adapt the plan
                    if self.adaptation_enabled:
                        adapted_plan = self.adapt_plan(i, action)
                        if adapted_plan:
                            # Continue with adapted plan
                            self.current_plan = adapted_plan
                            continue
                        else:
                            # Stop execution if adaptation fails
                            break

            except Exception as e:
                self.execution_status[i].status = 'failed'
                self.execution_status[i].end_time = time.time()
                self.execution_status[i].error_message = str(e)
                break

        # Call completion callback if provided
        if callback:
            callback(self.execution_status)

    def execute_single_action(self, action: Dict[str, Any], action_index: int) -> bool:
        """Execute a single action with progress monitoring"""
        action_type = action.get('type', '')
        parameters = action.get('parameters', {})

        # Simulate action execution with progress updates
        total_steps = 10  # Simulate 10 progress steps
        for step in range(total_steps):
            if self.stop_execution.is_set():
                return False

            # Update progress
            progress = step / total_steps
            self.execution_status[action_index].progress = progress

            # Simulate action step
            time.sleep(0.1)  # Simulate processing time

            # Check for real-time conditions that might affect execution
            if not self.check_execution_feasibility(action, action_index):
                return False

        return True

    def check_execution_feasibility(self, action: Dict[str, Any], action_index: int) -> bool:
        """Check if action is still feasible to execute"""
        # Check current robot state
        current_state = self.robot_interface.get_current_state()

        # Check if conditions have changed since plan generation
        preconditions = action.get('preconditions', [])
        for precondition in preconditions:
            if not self.llm_interface.check_precondition(precondition, current_state):
                # Plan might need adaptation
                return False

        return True

    def adapt_plan(self, failed_action_index: int, failed_action: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Adapt the plan when an action fails"""
        if not self.adaptation_enabled:
            return None

        # Get the remaining plan
        remaining_plan = self.current_plan[failed_action_index + 1:]

        # Get current world state
        current_state = self.robot_interface.get_current_state()

        # Generate alternative plan using LLM
        try:
            alternative_plan = self.llm_interface.generate_adapted_plan(
                original_plan=self.current_plan,
                failed_action_index=failed_action_index,
                failed_action=failed_action,
                current_state=current_state,
                remaining_goals=remaining_plan
            )

            return alternative_plan

        except Exception as e:
            print(f"Plan adaptation failed: {e}")
            return None

    def get_execution_progress(self) -> Dict[str, Any]:
        """Get overall execution progress"""
        if not self.execution_status:
            return {
                'total_actions': 0,
                'completed_actions': 0,
                'failed_actions': 0,
                'overall_progress': 0.0,
                'current_action': None,
                'estimated_time_remaining': 0
            }

        total_actions = len(self.execution_status)
        completed_actions = sum(1 for status in self.execution_status if status.status == 'completed')
        failed_actions = sum(1 for status in self.execution_status if status.status == 'failed')

        overall_progress = sum(status.progress for status in self.execution_status) / total_actions

        current_action = None
        for i, status in enumerate(self.execution_status):
            if status.status == 'executing':
                current_action = i
                break

        return {
            'total_actions': total_actions,
            'completed_actions': completed_actions,
            'failed_actions': failed_actions,
            'overall_progress': overall_progress,
            'current_action': current_action,
            'estimated_time_remaining': self.estimate_time_remaining()
        }

    def estimate_time_remaining(self) -> float:
        """Estimate time remaining for plan execution"""
        completed_actions = [s for s in self.execution_status if s.status == 'completed']

        if not completed_actions:
            return -1  # Unknown

        avg_time_per_action = sum(
            s.end_time - s.start_time for s in completed_actions
        ) / len(completed_actions)

        remaining_actions = sum(1 for s in self.execution_status if s.status in ['pending', 'executing'])
        return avg_time_per_action * remaining_actions

    def stop_current_execution(self):
        """Stop the current plan execution"""
        self.stop_execution.set()
        if self.execution_thread:
            self.execution_thread.join()
```

## 14.7 Performance Optimization

### Optimized LLM Integration
```python
# Performance-optimized LLM integration
import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import threading
import queue

@dataclass
class LLMRequest:
    prompt: str
    parameters: Dict[str, Any]
    callback: Callable
    priority: int = 1  # Lower number = higher priority

class OptimizedLLMInterface:
    def __init__(self, api_key: str, model_name: str = "gpt-4-turbo"):
        self.api_key = api_key
        self.model_name = model_name
        self.request_queue = queue.PriorityQueue()
        self.result_cache = {}
        self.cache_size_limit = 100
        self.max_retries = 3
        self.retry_delay = 1.0

        # Rate limiting
        self.requests_per_minute = 10  # Adjust based on your API limits
        self.request_times = []

        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_requests, daemon=True)
        self.processing_thread.start()

    def generate_plan_async(self, prompt: str, callback: Callable, priority: int = 1):
        """Add a plan generation request to the queue"""
        request = LLMRequest(
            prompt=prompt,
            parameters={'model': self.model_name, 'temperature': 0.3},
            callback=callback,
            priority=priority
        )
        self.request_queue.put((priority, time.time(), request))

    def _process_requests(self):
        """Process LLM requests in the background"""
        while True:
            try:
                # Wait for a request
                priority, submit_time, request = self.request_queue.get(timeout=1.0)

                # Check rate limit
                self._enforce_rate_limit()

                # Process the request
                result = self._call_llm(request.prompt, request.parameters)

                # Call the callback with the result
                request.callback(result)

                # Add to cache
                self._add_to_cache(request.prompt, result)

                self.request_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing LLM request: {e}")

    def _enforce_rate_limit(self):
        """Enforce API rate limits"""
        current_time = time.time()

        # Remove old requests outside the minute window
        self.request_times = [t for t in self.request_times if current_time - t < 60]

        # Wait if we've hit the limit
        while len(self.request_times) >= self.requests_per_minute:
            time.sleep(1)
            current_time = time.time()
            self.request_times = [t for t in self.request_times if current_time - t < 60]

        # Record this request time
        self.request_times.append(current_time)

    def _call_llm(self, prompt: str, parameters: Dict[str, Any]) -> Optional[str]:
        """Make the actual LLM call with retry logic"""
        import openai

        client = openai.OpenAI(api_key=self.api_key)

        for attempt in range(self.max_retries):
            try:
                response = client.chat.completions.create(
                    model=parameters.get('model', self.model_name),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=parameters.get('max_tokens', 1000),
                    temperature=parameters.get('temperature', 0.3)
                )

                return response.choices[0].message.content

            except openai.RateLimitError:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    raise
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise e

    def _add_to_cache(self, prompt: str, result: str):
        """Add result to cache with size management"""
        if len(self.result_cache) >= self.cache_size_limit:
            # Remove oldest entries
            oldest_key = next(iter(self.result_cache))
            del self.result_cache[oldest_key]

        self.result_cache[prompt] = {
            'result': result,
            'timestamp': time.time()
        }

    def get_cached_result(self, prompt: str) -> Optional[str]:
        """Get result from cache if available"""
        if prompt in self.result_cache:
            cached = self.result_cache[prompt]
            # Check if cache is still valid (e.g., less than 1 hour old)
            if time.time() - cached['timestamp'] < 3600:
                return cached['result']
            else:
                del self.result_cache[prompt]

        return None
```

## 14.8 Integration with ROS 2 Ecosystem

### Complete Integration Example
```python
# Complete cognitive planning system integration
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from sensor_msgs.msg import Image, LaserScan
import json
import threading

class CompleteCognitivePlanningSystem(Node):
    def __init__(self):
        super().__init__('complete_cognitive_planning_system')

        # Publishers
        self.plan_pub = self.create_publisher(String, '/cognitive_plan', 10)
        self.status_pub = self.create_publisher(String, '/cognitive_system_status', 10)
        self.feedback_pub = self.create_publisher(String, '/cognitive_system_feedback', 10)

        # Subscribers
        self.command_sub = self.create_subscription(
            String, '/natural_language_command', self.command_callback, 10
        )
        self.world_state_sub = self.create_subscription(
            String, '/world_state', self.world_state_callback, 10
        )
        self.sensor_subs = [
            self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10),
            self.create_subscription(LaserScan, '/scan', self.laser_callback, 10)
        ]

        # Action clients
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Initialize components
        self.llm_interface = OptimizedLLMInterface(
            api_key=self.get_parameter_or_set_default('openai_api_key', 'your-api-key')
        )
        self.plan_validator = PlanValidator()
        self.execution_monitor = PlanExecutionMonitor(self, self.llm_interface)
        self.nlp_parser = NaturalLanguageParser()

        # System state
        self.world_state = {}
        self.current_plan = None
        self.is_executing = False

        # Parameters
        self.declare_parameter('enable_adaptation', True)
        self.declare_parameter('max_plan_length', 20)
        self.declare_parameter('plan_validation_enabled', True)

        self.get_logger().info('Complete Cognitive Planning System initialized')

    def get_parameter_or_set_default(self, param_name: str, default_value):
        """Get parameter or set to default if not exists"""
        self.declare_parameter(param_name, default_value)
        return self.get_parameter(param_name).value

    def command_callback(self, msg):
        """Main command processing callback"""
        command = msg.data
        self.get_logger().info(f'Received natural language command: {command}')

        # Publish system status
        self.publish_status(f'Processing command: {command}')

        # Parse the command
        parsed_command = self.nlp_parser.parse_command(command)
        if not parsed_command:
            self.get_logger().error('Failed to parse command')
            self.publish_status('Command parsing failed')
            return

        # Generate plan using LLM
        plan = self.generate_plan_with_llm(parsed_command)
        if not plan:
            self.get_logger().error('Failed to generate plan')
            self.publish_status('Plan generation failed')
            return

        # Validate the plan
        if self.get_parameter('plan_validation_enabled').value:
            is_valid, errors, validated_plan = self.plan_validator.validate_plan(plan, self.world_state)
            if not is_valid:
                self.get_logger().error(f'Plan validation failed: {errors}')
                self.publish_status(f'Plan validation failed: {errors}')
                return
            plan = validated_plan

        # Check plan length constraint
        if len(plan) > self.get_parameter('max_plan_length').value:
            self.get_logger().error(f'Plan too long: {len(plan)} actions, max {self.get_parameter("max_plan_length").value}')
            self.publish_status('Generated plan too long')
            return

        # Store and publish the plan
        self.current_plan = plan
        plan_msg = String()
        plan_msg.data = json.dumps(plan)
        self.plan_pub.publish(plan_msg)

        self.get_logger().info(f'Generated and published plan with {len(plan)} actions')

        # Optionally execute the plan
        self.execute_plan_async(plan)

    def generate_plan_with_llm(self, parsed_command):
        """Generate plan using LLM with proper context"""
        try:
            # Create comprehensive prompt with world context
            world_context = json.dumps(self.world_state, indent=2)

            prompt = f"""
            You are an advanced cognitive planning assistant for a humanoid robot.

            USER COMMAND: {parsed_command.original_command}
            PARSED COMMAND: Action={parsed_command.action}, Objects={parsed_command.objects}, Locations={parsed_command.locations}

            CURRENT WORLD STATE:
            {world_context}

            ROBOT CAPABILITIES:
            - Navigation in indoor environments
            - Object detection and manipulation
            - Speech interaction
            - Sensor data processing

            CONSTRAINTS:
            - All actions must be safe for humans and environment
            - Respect robot physical limitations
            - Consider battery and operational constraints

            Generate a detailed action plan as a JSON array. Each action should include:
            - type: Action type (navigate, detect, pick, place, speak, etc.)
            - parameters: All necessary parameters
            - description: Clear description
            - preconditions: Conditions needed before execution
            - expected_effects: Outcomes of the action

            Example format:
            [
                {{
                    "type": "navigate",
                    "parameters": {{"target_location": "kitchen", "waypoint": "kitchen_waypoint"}},
                    "description": "Navigate to kitchen",
                    "preconditions": [{{"robot_battery_level": {{">": 0.2}}}}],
                    "expected_effects": [{{"robot_location": "kitchen"}}]
                }}
            ]

            DETAILED ACTION PLAN:
            """

            # In a real implementation, this would call the LLM
            # For this example, we'll simulate the response
            simulated_plan = self.simulate_llm_plan(parsed_command)
            return simulated_plan

        except Exception as e:
            self.get_logger().error(f'Error generating plan with LLM: {e}')
            return None

    def simulate_llm_plan(self, parsed_command):
        """Simulate LLM response for demonstration"""
        # This would be replaced with actual LLM call in real implementation
        if parsed_command.action == 'clean':
            room = parsed_command.locations[0] if parsed_command.locations else 'room'
            return [
                {
                    "type": "speak",
                    "parameters": {"message": f"Starting cleaning of the {room}"},
                    "description": f"Announce cleaning start for {room}",
                    "preconditions": [{"speech_system_available": True}],
                    "expected_effects": [{"user_notified": True}]
                },
                {
                    "type": "navigate",
                    "parameters": {"target_location": room, "waypoint": f"{room.replace(' ', '_')}_waypoint"},
                    "description": f"Navigate to {room}",
                    "preconditions": [{"robot_battery_level": {">": 0.3}}, {"navigation_system_available": True}],
                    "expected_effects": [{"robot_location": room}]
                },
                {
                    "type": "detect",
                    "parameters": {"target_area": room, "object_types": ["clutter", "dirt", "obstacles"]},
                    "description": f"Detect cleaning targets in {room}",
                    "preconditions": [{"camera_available": True}, {"robot_location": room}],
                    "expected_effects": [{"cleaning_targets_identified": True}]
                }
            ]
        else:
            # Default plan for other commands
            return [
                {
                    "type": "speak",
                    "parameters": {"message": f"Processing your request: {parsed_command.original_command}"},
                    "description": "Acknowledge the command",
                    "preconditions": [{"speech_system_available": True}],
                    "expected_effects": [{"user_acknowledged": True}]
                }
            ]

    def execute_plan_async(self, plan):
        """Execute plan asynchronously"""
        if self.is_executing:
            self.get_logger().warn('Plan execution already in progress, skipping')
            return

        self.is_executing = True
        execution_thread = threading.Thread(
            target=self._execute_plan_thread,
            args=(plan,)
        )
        execution_thread.start()

    def _execute_plan_thread(self, plan):
        """Execute plan in separate thread with monitoring"""
        try:
            self.execution_monitor.execute_plan(plan, self.plan_execution_callback)
        except Exception as e:
            self.get_logger().error(f'Plan execution thread error: {e}')
        finally:
            self.is_executing = False

    def plan_execution_callback(self, execution_status):
        """Callback for plan execution completion"""
        completed = sum(1 for status in execution_status if status.status == 'completed')
        total = len(execution_status)

        status_msg = f'Plan execution completed: {completed}/{total} actions successful'
        self.publish_status(status_msg)

        self.get_logger().info(status_msg)

    def world_state_callback(self, msg):
        """Update world state from perception systems"""
        try:
            new_state = json.loads(msg.data)
            self.world_state.update(new_state)
            self.get_logger().debug(f'Updated world state with {len(new_state)} new items')
        except json.JSONDecodeError:
            self.get_logger().error('Failed to parse world state update')

    def image_callback(self, msg):
        """Process camera images for object detection"""
        # This would integrate with computer vision systems
        # For now, just log that we received an image
        pass

    def laser_callback(self, msg):
        """Process laser scan for navigation"""
        # This would integrate with navigation systems
        # For now, just log that we received a scan
        pass

    def publish_status(self, status_message):
        """Publish status message"""
        status_msg = String()
        status_msg.data = status_message
        self.status_pub.publish(status_msg)

def main(args=None):
    rclpy.init(args=args)

    cognitive_planner = CompleteCognitivePlanningSystem()

    try:
        rclpy.spin(cognitive_planner)
    except KeyboardInterrupt:
        cognitive_planner.get_logger().info('Shutting down cognitive planning system')
    finally:
        cognitive_planner.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 14.9 Error Handling and Fallback Strategies

### Robust Error Handling
```python
# Error handling and fallback strategies for cognitive planning
import random
from enum import Enum

class ErrorType(Enum):
    LLM_COMMUNICATION_ERROR = "llm_communication_error"
    PLAN_VALIDATION_ERROR = "plan_validation_error"
    EXECUTION_ERROR = "execution_error"
    SENSORY_ERROR = "sensory_error"
    ROBOT_ERROR = "robot_error"

class CognitivePlanningErrorHandler:
    def __init__(self, cognitive_planner):
        self.planner = cognitive_planner
        self.error_history = []
        self.fallback_strategies = self.initialize_fallback_strategies()

    def initialize_fallback_strategies(self):
        """Initialize various fallback strategies"""
        return {
            ErrorType.LLM_COMMUNICATION_ERROR: [
                self.use_cached_plan,
                self.request_human_intervention,
                self.use_simplified_planning
            ],
            ErrorType.PLAN_VALIDATION_ERROR: [
                self.simplify_plan,
                self.request_clarification,
                self.use_default_plan
            ],
            ErrorType.EXECUTION_ERROR: [
                self.retry_action,
                self.skip_action,
                self.alternative_action
            ],
            ErrorType.SENSORY_ERROR: [
                self.use_estimated_data,
                self.request_sensor_reset,
                self.use_backup_sensors
            ],
            ErrorType.ROBOT_ERROR: [
                self.return_to_home,
                self.request_maintenance,
                self.use_manual_control
            ]
        }

    def handle_error(self, error_type: ErrorType, context: Dict[str, Any] = None):
        """Handle an error using appropriate fallback strategies"""
        error_entry = {
            'type': error_type,
            'timestamp': time.time(),
            'context': context or {},
            'handled': False
        }
        self.error_history.append(error_entry)

        # Get appropriate fallback strategies
        strategies = self.fallback_strategies.get(error_type, [])

        for strategy in strategies:
            try:
                result = strategy(context)
                if result:
                    error_entry['handled'] = True
                    self.planner.get_logger().info(f'Error {error_type.value} handled by {strategy.__name__}')
                    return True
            except Exception as e:
                self.planner.get_logger().error(f'Fallback strategy {strategy.__name__} failed: {e}')
                continue

        # If no strategy worked, escalate
        self.planner.get_logger().error(f'No fallback strategy succeeded for error: {error_type.value}')
        self.escalate_error(error_type, context)
        return False

    def use_cached_plan(self, context):
        """Use a previously cached plan as fallback"""
        command = context.get('command', '')
        cached_plan = self.planner.llm_interface.get_cached_result(command)

        if cached_plan:
            self.planner.get_logger().info('Using cached plan as fallback')
            # Execute cached plan
            return True
        return False

    def request_human_intervention(self, context):
        """Request human assistance"""
        self.planner.publish_status('Requesting human assistance')
        # This would trigger a human-in-the-loop system
        return True

    def use_simplified_planning(self, context):
        """Use rule-based simplified planning"""
        command = context.get('command', '')
        # Implement simplified rule-based planning
        simple_plan = self.create_simple_plan(command)
        if simple_plan:
            self.planner.get_logger().info('Using simplified plan as fallback')
            self.planner.execute_plan_async(simple_plan)
            return True
        return False

    def create_simple_plan(self, command):
        """Create a simple rule-based plan"""
        command_lower = command.lower()

        if 'go to' in command_lower or 'move to' in command_lower:
            # Simple navigation plan
            return [
                {
                    "type": "navigate",
                    "parameters": {"target_location": "default_location"},
                    "description": "Navigate to default location",
                    "preconditions": [],
                    "expected_effects": []
                }
            ]
        elif 'pick' in command_lower or 'get' in command_lower:
            # Simple pick plan
            return [
                {
                    "type": "detect",
                    "parameters": {"object_type": "default_object"},
                    "description": "Detect default object",
                    "preconditions": [],
                    "expected_effects": []
                },
                {
                    "type": "pick",
                    "parameters": {"object": "default_object"},
                    "description": "Pick default object",
                    "preconditions": [],
                    "expected_effects": []
                }
            ]

        return None

    def simplify_plan(self, context):
        """Simplify an over-complex plan"""
        original_plan = context.get('plan', [])
        if len(original_plan) > 5:  # If plan has more than 5 actions
            # Simplify by removing intermediate steps
            simplified_plan = [original_plan[0], original_plan[-1]]  # Just first and last
            self.planner.get_logger().info('Plan simplified due to validation error')
            self.planner.execute_plan_async(simplified_plan)
            return True
        return False

    def retry_action(self, context):
        """Retry the failed action"""
        action = context.get('failed_action', {})
        retry_count = context.get('retry_count', 0)

        if retry_count < 3:  # Max 3 retries
            self.planner.get_logger().info(f'Retrying action: {action.get("type", "unknown")}')
            # In real implementation, this would retry the specific action
            context['retry_count'] = retry_count + 1
            return True
        return False

    def escalate_error(self, error_type, context):
        """Escalate error to higher level system"""
        # This would typically trigger emergency protocols
        self.planner.publish_status(f'CRITICAL: {error_type.value} escalated - requesting immediate attention')
```

## 14.10 Best Practices and Evaluation

### Performance Evaluation Metrics
```python
# Evaluation metrics for cognitive planning systems
import statistics
from datetime import datetime

class CognitivePlanningEvaluator:
    def __init__(self):
        self.metrics = {
            'plan_generation_time': [],
            'execution_success_rate': [],
            'plan_feasibility_rate': [],
            'user_satisfaction': [],
            'safety_violations': [],
            'adaptation_frequency': []
        }

    def record_plan_generation_time(self, time_seconds):
        """Record time taken to generate a plan"""
        self.metrics['plan_generation_time'].append(time_seconds)

    def record_execution_result(self, success: bool, plan_length: int):
        """Record plan execution result"""
        self.metrics['execution_success_rate'].append({
            'success': success,
            'plan_length': plan_length
        })

    def record_plan_feasibility(self, feasible: bool, plan):
        """Record whether a plan was feasible"""
        self.metrics['plan_feasibility_rate'].append(feasible)

    def record_user_satisfaction(self, rating: int):
        """Record user satisfaction rating (1-5 scale)"""
        if 1 <= rating <= 5:
            self.metrics['user_satisfaction'].append(rating)

    def record_safety_violation(self, violation_type: str):
        """Record a safety violation"""
        self.metrics['safety_violations'].append({
            'type': violation_type,
            'timestamp': datetime.now()
        })

    def record_adaptation(self, reason: str):
        """Record when plan adaptation was needed"""
        self.metrics['adaptation_frequency'].append({
            'reason': reason,
            'timestamp': datetime.now()
        })

    def get_evaluation_report(self):
        """Generate a comprehensive evaluation report"""
        report = {
            'summary': {},
            'detailed_metrics': {},
            'recommendations': []
        }

        # Calculate summary statistics
        if self.metrics['plan_generation_time']:
            report['summary']['avg_generation_time'] = statistics.mean(self.metrics['plan_generation_time'])
            report['summary']['max_generation_time'] = max(self.metrics['plan_generation_time'])
            report['summary']['min_generation_time'] = min(self.metrics['plan_generation_time'])

        if self.metrics['execution_success_rate']:
            successful_executions = [r for r in self.metrics['execution_success_rate'] if r['success']]
            success_rate = len(successful_executions) / len(self.metrics['execution_success_rate'])
            report['summary']['execution_success_rate'] = success_rate

        if self.metrics['plan_feasibility_rate']:
            feasible_plans = sum(self.metrics['plan_feasibility_rate'])
            total_plans = len(self.metrics['plan_feasibility_rate'])
            report['summary']['plan_feasibility_rate'] = feasible_plans / total_plans if total_plans > 0 else 0

        if self.metrics['user_satisfaction']:
            report['summary']['avg_user_satisfaction'] = statistics.mean(self.metrics['user_satisfaction'])

        report['summary']['total_safety_violations'] = len(self.metrics['safety_violations'])
        report['summary']['adaptation_count'] = len(self.metrics['adaptation_frequency'])

        # Add detailed metrics
        report['detailed_metrics'] = self.metrics

        # Generate recommendations
        if report['summary'].get('avg_generation_time', 0) > 5.0:
            report['recommendations'].append("Plan generation time is too high. Consider optimizing LLM prompts or using smaller models.")

        if report['summary'].get('execution_success_rate', 1.0) < 0.8:
            report['recommendations'].append("Execution success rate is low. Review plan validation and safety constraints.")

        if report['summary'].get('plan_feasibility_rate', 1.0) < 0.9:
            report['recommendations'].append("Plan feasibility rate is concerning. Improve world modeling and constraint checking.")

        if report['summary'].get('avg_user_satisfaction', 5.0) < 4.0:
            report['recommendations'].append("User satisfaction is low. Review natural language understanding and plan quality.")

        if report['summary']['total_safety_violations'] > 0:
            report['recommendations'].append("Safety violations detected. Review safety constraint implementation.")

        return report
```

## 14.11 Exercises and Activities

### Exercise 1: Basic LLM Integration
Integrate a simple LLM (like OpenAI GPT or a local model) with ROS 2 to convert natural language commands into basic robot actions. Test with simple commands like "move forward" and "turn left".

### Exercise 2: Plan Validation System
Implement a plan validation system that checks LLM-generated plans for safety constraints and feasibility before execution. Include checks for robot capabilities, environmental constraints, and safety rules.

### Exercise 3: Natural Language Parser
Create an advanced natural language parser that can handle complex commands with multiple objects, locations, and conditions. Test with commands like "Go to the kitchen and pick up the red cup from the table".

### Exercise 4: Plan Adaptation
Implement a plan adaptation system that can modify an executing plan when unexpected conditions are encountered. Test with simulated sensor failures or changed environmental conditions.

## 14.12 Chapter Summary

This chapter explored the implementation of cognitive planning systems using Large Language Models (LLMs) to translate natural language commands into executable robot actions. We covered the complete pipeline from natural language understanding to plan generation, validation, and execution.

The cognitive planning system bridges the gap between high-level human commands and low-level robot control, enabling more intuitive human-robot interaction. Key components include LLM integration, natural language parsing, plan validation, safety constraint enforcement, and real-time execution monitoring.

Successful cognitive planning requires careful attention to safety, validation, and error handling to ensure reliable operation in real-world environments.

## Key Terms and Definitions

- **Cognitive Planning**: The process of translating high-level goals into executable action sequences
- **Large Language Model (LLM)**: AI models trained on vast text corpora for language understanding and generation
- **Natural Language Processing (NLP)**: Techniques for understanding and processing human language
- **Plan Validation**: Verification that a generated plan is safe and feasible
- **Action Planning**: Creating sequences of robot actions to achieve goals
- **Prompt Engineering**: Designing effective prompts for LLMs
- **Plan Adaptation**: Modifying plans during execution based on changing conditions
- **Safety Constraints**: Rules that prevent unsafe robot behaviors
- **Precondition**: Conditions that must be true before executing an action
- **Expected Effects**: Outcomes that result from executing an action
- **World State**: Representation of the current environment and robot status
- **Execution Monitoring**: Supervision of plan execution with feedback
- **Fallback Strategy**: Alternative approaches when primary methods fail
- **Human-in-the-Loop**: System design that includes human oversight and intervention
- **Constraint Satisfaction**: Ensuring plans meet all required conditions
- **Temporal Planning**: Planning that considers time and sequencing constraints

## Further Reading

1. "Language Models for Robotics" by Ha et al.
2. ROS 2 Navigation: https://navigation.ros.org/
3. "Robot Learning from Language" research papers
4. OpenAI API Documentation: https://platform.openai.com/docs/
5. "Planning Algorithms" by LaValle for classical planning techniques

## QA Checklist
- [ ] Chapter content accurately describes LLM integration for cognitive planning
- [ ] Natural language processing concepts are thoroughly explained
- [ ] Plan validation and safety mechanisms are properly covered
- [ ] Real-time execution and monitoring are addressed
- [ ] Performance optimization techniques are mentioned
- [ ] Error handling and fallback strategies are included
- [ ] Exercises are relevant and test understanding
- [ ] Key terms are defined and explained
- [ ] Content aligns with the module's focus on cognitive planning
- [ ] Links to further reading are valid
- [ ] Chapter summary effectively summarizes key concepts