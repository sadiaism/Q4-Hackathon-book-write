# Chapter 13: Voice-to-Action: Using OpenAI Whisper for voice commands

## Learning Objectives
After completing this chapter, students will be able to:
- Install and configure OpenAI Whisper for voice command processing
- Integrate Whisper with ROS 2 for real-time speech recognition
- Process and filter voice commands for robotic applications
- Implement voice command validation and error handling
- Create custom voice command vocabularies for robotics
- Optimize Whisper performance for embedded robotics platforms
- Design voice command grammars for natural human-robot interaction
- Validate voice command accuracy and response times

## 13.1 Introduction to OpenAI Whisper

OpenAI Whisper is a state-of-the-art speech recognition model that converts spoken language into text. For robotics applications, Whisper enables natural voice-to-action interfaces, allowing humans to control robots using spoken commands in a more intuitive way than traditional button-based or app-based interfaces.

### Key Features of Whisper
- **Multilingual Support**: Supports recognition in multiple languages
- **Robustness**: Performs well in noisy environments
- **Real-time Processing**: Can process audio streams in real-time
- **Customizable**: Can be fine-tuned for specific domains and vocabularies
- **Open Source**: Available with different model sizes for various applications

### Whisper Model Variants
- **Tiny**: Fastest, least accurate (75MB)
- **Base**: Good balance of speed and accuracy (145MB)
- **Small**: Better accuracy, moderate speed (484MB)
- **Medium**: High accuracy, slower processing (1.5GB)
- **Large**: Highest accuracy, slowest processing (3.0GB)

## 13.2 Installing and Configuring Whisper

### System Requirements
- **Operating System**: Ubuntu 20.04 LTS or 22.04 LTS
- **Python**: 3.8 or higher
- **Hardware**: CPU with AVX support (GPU recommended for large models)
- **Memory**: 4GB+ RAM (8GB+ for larger models)
- **Storage**: 1-3GB for model files depending on selected variant

### Installing Whisper Dependencies
```bash
# Install Python dependencies
pip install openai-whisper
pip install torch torchvision torchaudio
pip install pyaudio  # For audio capture
pip install speech-recognition  # Alternative recognition library
pip install sounddevice  # For audio I/O
pip install numpy scipy
```

### Installing ROS 2 Dependencies
```bash
# Install ROS 2 audio and speech packages
sudo apt update
sudo apt install ros-humble-audio-common
sudo apt install ros-humble-sound-play
sudo apt install ros-humble-teleop-tools
```

### Basic Whisper Setup
```python
# Basic Whisper setup and test
import whisper
import torch

def test_whisper_installation():
    """Test Whisper installation and basic functionality"""
    # Check if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load a small model for testing
    model = whisper.load_model("base", device=device)
    print("Whisper model loaded successfully")

    # Test with a sample audio file (optional)
    # result = model.transcribe("sample_audio.wav")
    # print(f"Transcription: {result['text']}")

if __name__ == "__main__":
    test_whisper_installation()
```

## 13.3 Audio Capture and Processing for Robotics

### Audio Input Setup
```python
# Audio capture for voice commands
import pyaudio
import wave
import numpy as np
import threading
import time
from collections import deque

class AudioCapture:
    def __init__(self, rate=16000, chunk=1024, channels=1):
        self.rate = rate
        self.chunk = chunk
        self.channels = channels
        self.format = pyaudio.paInt16
        self.audio = pyaudio.PyAudio()

        # Audio buffers
        self.audio_buffer = deque(maxlen=rate * 5)  # 5 seconds buffer
        self.recording = False
        self.stream = None

        # Voice activity detection parameters
        self.energy_threshold = 1000  # Adjust based on environment
        self.silence_duration = 1.0   # Seconds of silence to stop recording

    def start_capture(self):
        """Start audio capture in a separate thread"""
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        self.recording = True

        # Start capture thread
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.start()

    def stop_capture(self):
        """Stop audio capture"""
        self.recording = False
        if self.capture_thread:
            self.capture_thread.join()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

    def _capture_loop(self):
        """Main capture loop running in separate thread"""
        while self.recording:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)

            # Add to buffer
            for sample in audio_data:
                self.audio_buffer.append(sample)

    def get_audio_chunk(self, duration=1.0):
        """Get a chunk of audio data for processing"""
        samples_needed = int(self.rate * duration)
        if len(self.audio_buffer) < samples_needed:
            return None

        # Get the most recent samples
        chunk = np.array(list(self.audio_buffer)[-samples_needed:])
        return chunk

    def detect_voice_activity(self, audio_chunk=None):
        """Detect if voice activity is present in audio chunk"""
        if audio_chunk is None:
            audio_chunk = self.get_audio_chunk(0.5)  # Half-second chunk
            if audio_chunk is None:
                return False

        # Calculate energy of the audio chunk
        energy = np.mean(np.abs(audio_chunk.astype(np.float32)))
        return energy > self.energy_threshold

    def record_until_silence(self, max_duration=10.0):
        """Record audio until silence is detected"""
        recorded_chunks = []
        silence_frames = 0
        max_silence_frames = int(self.rate * self.silence_duration / self.chunk)
        max_frames = int(max_duration * self.rate / self.chunk)
        frame_count = 0

        while frame_count < max_frames:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            recorded_chunks.append(audio_data)

            # Check for silence
            energy = np.mean(np.abs(audio_data.astype(np.float32)))
            if energy < self.energy_threshold:
                silence_frames += 1
            else:
                silence_frames = 0  # Reset silence counter

            if silence_frames >= max_silence_frames:
                break

            frame_count += 1

        # Combine all recorded chunks
        if recorded_chunks:
            full_audio = np.concatenate(recorded_chunks)
            return full_audio
        return None
```

### ROS 2 Audio Interface
```python
# ROS 2 node for audio capture and processing
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from audio_common_msgs.msg import AudioData
import numpy as np
import threading

class VoiceCommandNode(Node):
    def __init__(self):
        super().__init__('voice_command_node')

        # Publishers
        self.command_pub = self.create_publisher(String, '/voice_command', 10)
        self.listening_pub = self.create_publisher(Bool, '/voice_listening_status', 10)

        # Subscribers
        self.audio_sub = self.create_subscription(
            AudioData, '/audio_input', self.audio_callback, 10
        )

        # Audio capture setup
        self.audio_capture = AudioCapture()
        self.whisper_model = None
        self.is_listening = False

        # Parameters
        self.declare_parameter('whisper_model', 'base')
        self.declare_parameter('enable_continuous_listening', False)

        # Setup Whisper model
        self.setup_whisper()

        # Timer for continuous processing if enabled
        if self.get_parameter('enable_continuous_listening').value:
            self.process_timer = self.create_timer(0.1, self.process_audio_continuously)

    def setup_whisper(self):
        """Setup Whisper model for voice processing"""
        import whisper
        import torch

        model_name = self.get_parameter('whisper_model').value
        device = "cuda" if torch.cuda.is_available() else "cpu"

        try:
            self.whisper_model = whisper.load_model(model_name, device=device)
            self.get_logger().info(f'Whisper model {model_name} loaded successfully on {device}')
        except Exception as e:
            self.get_logger().error(f'Failed to load Whisper model: {e}')

    def audio_callback(self, msg):
        """Handle incoming audio data"""
        if not self.is_listening or self.whisper_model is None:
            return

        # Convert audio data to numpy array
        audio_array = np.frombuffer(msg.data, dtype=np.int16).astype(np.float32) / 32768.0

        # Process audio for voice command
        command = self.process_audio_command(audio_array)

        if command:
            self.publish_command(command)

    def process_audio_command(self, audio_array):
        """Process audio array using Whisper to extract command"""
        if self.whisper_model is None:
            return None

        try:
            # Convert audio to the format expected by Whisper
            # Whisper expects audio at 16kHz
            if len(audio_array) < 16000 * 0.1:  # Minimum 0.1 seconds
                return None

            # Transcribe the audio
            result = self.whisper_model.transcribe(audio_array, fp16=False)
            text = result['text'].strip()

            # Filter out empty results or common misrecognitions
            if text and len(text) > 3 and not self.is_noise(text):
                return text

        except Exception as e:
            self.get_logger().error(f'Error processing audio: {e}')

        return None

    def is_noise(self, text):
        """Check if the recognized text is likely noise or misrecognition"""
        noise_patterns = [
            "thank you", "thanks", "okay", "yes", "no", "um", "uh", "hmm",
            "oh", "ah", "uh huh", "mm", "hm", "", " ", "."
        ]
        return text.lower().strip() in noise_patterns

    def publish_command(self, command):
        """Publish recognized voice command"""
        cmd_msg = String()
        cmd_msg.data = command
        self.command_pub.publish(cmd_msg)
        self.get_logger().info(f'Published voice command: {command}')

    def start_listening(self):
        """Start listening for voice commands"""
        self.is_listening = True
        status_msg = Bool()
        status_msg.data = True
        self.listening_pub.publish(status_msg)
        self.get_logger().info('Started listening for voice commands')

    def stop_listening(self):
        """Stop listening for voice commands"""
        self.is_listening = False
        status_msg = Bool()
        status_msg.data = False
        self.listening_pub.publish(status_msg)
        self.get_logger().info('Stopped listening for voice commands')

    def process_audio_continuously(self):
        """Continuously process audio if continuous listening is enabled"""
        if self.audio_capture.detect_voice_activity():
            self.get_logger().info('Voice activity detected, recording...')
            audio_data = self.audio_capture.record_until_silence()

            if audio_data is not None:
                command = self.process_audio_command(audio_data)
                if command:
                    self.publish_command(command)
```

## 13.4 Voice Command Processing and Validation

### Command Recognition and Parsing
```python
# Voice command processor with validation
import re
from typing import Dict, List, Optional

class VoiceCommandProcessor:
    def __init__(self):
        # Define command patterns and their ROS 2 action mappings
        self.command_patterns = {
            # Movement commands
            r'go to (?P<location>\w+)': 'navigate_to',
            r'move to (?P<location>\w+)': 'navigate_to',
            r'go (?P<direction>\w+)': 'move_direction',
            r'move (?P<direction>\w+)': 'move_direction',
            r'forward|straight': 'move_forward',
            r'backward|back': 'move_backward',
            r'left|turn left': 'turn_left',
            r'right|turn right': 'turn_right',

            # Action commands
            r'pick up (?P<object>\w+)': 'pick_object',
            r'grasp (?P<object>\w+)': 'pick_object',
            r'pick (?P<object>\w+)': 'pick_object',
            r'drop|release': 'release_object',
            r'stop': 'stop_robot',
            r'pause': 'pause_robot',
            r'continue|resume': 'resume_robot',
            r'help': 'show_help',

            # Complex commands
            r'bring me (?P<object>\w+) from (?P<location>\w+)': 'fetch_object',
            r'clean the (?P<room>\w+)': 'clean_room',
            r'go to (?P<location>\w+) and (?P<action>\w+)': 'navigate_and_act',
        }

        # Location mappings
        self.location_map = {
            'kitchen': 'kitchen_waypoint',
            'living room': 'living_room_waypoint',
            'bedroom': 'bedroom_waypoint',
            'office': 'office_waypoint',
            'dining room': 'dining_room_waypoint',
            'bathroom': 'bathroom_waypoint',
        }

        # Object mappings
        self.object_map = {
            'cup': 'cup_object',
            'bottle': 'bottle_object',
            'book': 'book_object',
            'phone': 'phone_object',
            'keys': 'keys_object',
        }

        # Direction mappings
        self.direction_map = {
            'forward': 'FORWARD',
            'backward': 'BACKWARD',
            'left': 'LEFT',
            'right': 'RIGHT',
            'north': 'NORTH',
            'south': 'SOUTH',
            'east': 'EAST',
            'west': 'WEST',
        }

    def process_command(self, raw_command: str) -> Optional[Dict]:
        """Process raw voice command and return structured action"""
        if not raw_command:
            return None

        # Normalize the command
        normalized_command = self.normalize_command(raw_command.lower().strip())

        # Try to match against known patterns
        for pattern, action_type in self.command_patterns.items():
            match = re.search(pattern, normalized_command)
            if match:
                # Extract parameters and map them
                params = match.groupdict()

                # Map locations, objects, directions if present
                if 'location' in params:
                    params['location'] = self.location_map.get(params['location'], params['location'])
                if 'object' in params:
                    params['object'] = self.object_map.get(params['object'], params['object'])
                if 'direction' in params:
                    params['direction'] = self.direction_map.get(params['direction'], params['direction'])

                return {
                    'action': action_type,
                    'parameters': params,
                    'original_command': raw_command,
                    'confidence': 0.9  # This would come from the ASR confidence
                }

        # If no pattern matches, return a generic command
        return {
            'action': 'unknown_command',
            'parameters': {'text': raw_command},
            'original_command': raw_command,
            'confidence': 0.5
        }

    def normalize_command(self, command: str) -> str:
        """Normalize command text for better pattern matching"""
        # Remove common filler words
        fillers = ['please', 'could you', 'can you', 'would you', 'the', 'a', 'an']
        normalized = command

        for filler in fillers:
            normalized = normalized.replace(filler, '').strip()

        # Handle common contractions and variations
        contractions = {
            "gonna": "going to",
            "wanna": "want to",
            "gotta": "got to",
            "lemme": "let me",
            "cmon": "come on",
        }

        for contraction, expansion in contractions.items():
            normalized = normalized.replace(contraction, expansion)

        return ' '.join(normalized.split())  # Normalize whitespace

    def validate_command(self, processed_command: Dict) -> bool:
        """Validate if the processed command is appropriate for execution"""
        action = processed_command.get('action')
        params = processed_command.get('parameters', {})

        # Validate based on action type
        if action == 'navigate_to':
            location = params.get('location')
            if not location:
                return False
            # Additional validation could check if location is known

        elif action == 'pick_object':
            obj = params.get('object')
            if not obj:
                return False

        elif action == 'move_direction':
            direction = params.get('direction')
            if direction not in self.direction_map.values():
                return False

        # Check confidence level
        confidence = processed_command.get('confidence', 0.0)
        if confidence < 0.7:  # Threshold for command execution
            return False

        return True

    def get_command_suggestions(self, partial_command: str) -> List[str]:
        """Provide command suggestions based on partial input"""
        suggestions = []

        if 'go' in partial_command or 'move' in partial_command:
            suggestions.extend(['go to kitchen', 'go forward', 'move left', 'move right'])

        if 'pick' in partial_command or 'grasp' in partial_command:
            suggestions.extend(['pick up cup', 'grasp bottle', 'pick book'])

        if 'clean' in partial_command:
            suggestions.extend(['clean the kitchen', 'clean the room'])

        return suggestions[:3]  # Return top 3 suggestions
```

### Voice Command Validation Node
```python
# ROS 2 node for voice command validation
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Bool
from builtin_interfaces.msg import Time

class VoiceCommandValidator(Node):
    def __init__(self):
        super().__init__('voice_command_validator')

        # Subscriptions
        self.command_sub = self.create_subscription(
            String, '/raw_voice_command', self.command_callback, 10
        )

        # Publishers
        self.validated_command_pub = self.create_publisher(
            String, '/validated_voice_command', 10
        )
        self.command_status_pub = self.create_publisher(
            Bool, '/command_valid_status', 10
        )

        # Command processor
        self.command_processor = VoiceCommandProcessor()

        # Store recent commands to avoid repetition
        self.recent_commands = []
        self.max_recent = 5

    def command_callback(self, msg):
        """Process incoming voice command"""
        raw_command = msg.data

        # Process the command
        processed = self.command_processor.process_command(raw_command)

        if processed and self.command_processor.validate_command(processed):
            # Check for command repetition
            if self.is_command_repeated(processed):
                self.get_logger().info(f'Ignoring repeated command: {raw_command}')
                return

            # Publish validated command
            validated_msg = String()
            validated_msg.data = f"{processed['action']}:{processed['parameters']}"
            self.validated_command_pub.publish(validated_msg)

            # Publish success status
            status_msg = Bool()
            status_msg.data = True
            self.command_status_pub.publish(status_msg)

            # Store command to prevent repetition
            self.recent_commands.append(processed['original_command'])
            if len(self.recent_commands) > self.max_recent:
                self.recent_commands.pop(0)

            self.get_logger().info(f'Validated command: {validated_msg.data}')
        else:
            # Publish failure status
            status_msg = Bool()
            status_msg.data = False
            self.command_status_pub.publish(status_msg)

            self.get_logger().warn(f'Invalid command rejected: {raw_command}')

    def is_command_repeated(self, processed_command):
        """Check if command is a recent repetition"""
        original = processed_command['original_command']

        # Simple check for exact repetition
        if original in self.recent_commands:
            return True

        # More sophisticated check could look for semantic similarity
        return False
```

## 13.5 Whisper Optimization for Robotics

### Performance Optimization
```python
# Optimized Whisper processing for robotics
import whisper
import torch
import threading
import queue
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class AudioChunk:
    data: object
    timestamp: float
    callback: Optional[callable] = None

class OptimizedWhisperProcessor:
    def __init__(self, model_size="base", device="cuda"):
        self.model_size = model_size
        self.device = device if torch.cuda.is_available() else "cpu"

        # Load model
        self.model = whisper.load_model(self.model_size, device=self.device)

        # Processing queue
        self.audio_queue = queue.Queue(maxsize=10)
        self.result_queue = queue.Queue()

        # Processing thread
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()

        # Performance metrics
        self.processing_times = []
        self.average_processing_time = 0.0

    def process_audio_async(self, audio_data, callback=None):
        """Add audio to processing queue for asynchronous processing"""
        if self.audio_queue.full():
            self.audio_queue.get()  # Remove oldest item if queue is full

        chunk = AudioChunk(audio_data, time.time(), callback)
        self.audio_queue.put(chunk)

    def _processing_loop(self):
        """Background processing loop"""
        while True:
            try:
                chunk = self.audio_queue.get(timeout=1.0)

                start_time = time.time()

                # Process with Whisper
                result = self.model.transcribe(chunk.data, fp16=False)
                text = result['text'].strip()

                processing_time = time.time() - start_time
                self.processing_times.append(processing_time)

                # Update average processing time (keep last 100 measurements)
                if len(self.processing_times) > 100:
                    self.processing_times.pop(0)
                self.average_processing_time = sum(self.processing_times) / len(self.processing_times)

                # Execute callback if provided
                if chunk.callback:
                    chunk.callback(text, processing_time)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in processing loop: {e}")

    def get_average_processing_time(self):
        """Get average processing time for performance monitoring"""
        return self.average_processing_time

    def is_ready(self):
        """Check if processor is ready for processing"""
        return self.model is not None
```

### Resource Management
```python
# Resource management for Whisper on embedded systems
import psutil
import GPUtil
import os

class WhisperResourceManager:
    def __init__(self, max_cpu_percent=80, max_memory_percent=80):
        self.max_cpu_percent = max_cpu_percent
        self.max_memory_percent = max_memory_percent

        # Monitor system resources
        self.cpu_monitor = self.monitor_cpu_usage
        self.memory_monitor = self.monitor_memory_usage

    def monitor_cpu_usage(self):
        """Monitor CPU usage and adjust processing accordingly"""
        cpu_percent = psutil.cpu_percent(interval=1)
        return cpu_percent < self.max_cpu_percent

    def monitor_memory_usage(self):
        """Monitor memory usage"""
        memory_percent = psutil.virtual_memory().percent
        return memory_percent < self.max_memory_percent

    def get_system_status(self):
        """Get overall system resource status"""
        cpu_ok = self.monitor_cpu_usage()
        memory_ok = self.monitor_memory_usage()

        gpus = GPUtil.getGPUs() if GPUtil.getGPUs() else []
        gpu_ok = all(gpu.memoryUtil < 0.8 for gpu in gpus) if gpus else True

        return {
            'cpu_ok': cpu_ok,
            'memory_ok': memory_ok,
            'gpu_ok': gpu_ok,
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'gpus': [{'id': gpu.id, 'memory_util': gpu.memoryUtil} for gpu in gpus] if gpus else []
        }

    def should_reduce_quality(self):
        """Determine if processing quality should be reduced based on system load"""
        status = self.get_system_status()

        if not status['cpu_ok'] or not status['memory_ok']:
            return True

        return False
```

## 13.6 Integration with Robot Control Systems

### Voice Command to Robot Action Mapping
```python
# Voice command to robot action mapper
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Pose
from std_msgs.msg import String
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from std_srvs.srv import Trigger

class VoiceToRobotActionMapper(Node):
    def __init__(self):
        super().__init__('voice_to_robot_mapper')

        # Subscriptions
        self.voice_command_sub = self.create_subscription(
            String, '/validated_voice_command', self.voice_command_callback, 10
        )

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub = self.create_publisher(String, '/voice_action_status', 10)

        # Navigation action client
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Service clients
        self.gripper_client = self.create_client(Trigger, '/gripper_control')
        self.arm_client = self.create_client(Trigger, '/arm_control')

        # Command mapping
        self.command_mapping = {
            'move_forward': self.execute_move_forward,
            'move_backward': self.execute_move_backward,
            'turn_left': self.execute_turn_left,
            'turn_right': self.execute_turn_right,
            'navigate_to': self.execute_navigate_to,
            'pick_object': self.execute_pick_object,
            'release_object': self.execute_release_object,
            'stop_robot': self.execute_stop_robot,
        }

    def voice_command_callback(self, msg):
        """Process validated voice command and execute robot action"""
        try:
            # Parse command and parameters
            parts = msg.data.split(':', 1)
            if len(parts) < 2:
                self.get_logger().error(f'Invalid command format: {msg.data}')
                return

            action = parts[0]
            params_str = parts[1]

            # Execute mapped action
            if action in self.command_mapping:
                self.command_mapping[action](params_str)
                self.publish_status(f'Executed command: {action}')
            else:
                self.get_logger().warn(f'Unknown action: {action}')
                self.publish_status(f'Unknown command: {action}')

        except Exception as e:
            self.get_logger().error(f'Error executing voice command: {e}')
            self.publish_status(f'Command execution failed: {str(e)}')

    def execute_move_forward(self, params):
        """Execute forward movement"""
        twist = Twist()
        twist.linear.x = 0.3  # Forward speed
        twist.angular.z = 0.0
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info('Moving forward')

    def execute_move_backward(self, params):
        """Execute backward movement"""
        twist = Twist()
        twist.linear.x = -0.3  # Backward speed
        twist.angular.z = 0.0
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info('Moving backward')

    def execute_turn_left(self, params):
        """Execute left turn"""
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.5  # Left turn speed
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info('Turning left')

    def execute_turn_right(self, params):
        """Execute right turn"""
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = -0.5  # Right turn speed
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info('Turning right')

    def execute_navigate_to(self, params_str):
        """Execute navigation to specified location"""
        # Parse parameters (in a real implementation, this would be more structured)
        import ast
        try:
            params = ast.literal_eval(params_str)
            location = params.get('location', 'unknown')

            # In a real implementation, you would look up the pose for the location
            # For now, we'll use a placeholder
            goal_msg = NavigateToPose.Goal()
            goal_msg.pose.header.frame_id = 'map'
            goal_msg.pose.pose.position.x = 1.0  # Placeholder coordinates
            goal_msg.pose.pose.position.y = 1.0
            goal_msg.pose.pose.orientation.w = 1.0

            # Wait for action server
            if not self.nav_client.wait_for_server(timeout_sec=5.0):
                self.get_logger().error('Navigation action server not available')
                return

            # Send navigation goal
            future = self.nav_client.send_goal_async(goal_msg)
            future.add_done_callback(self.navigation_done_callback)

        except Exception as e:
            self.get_logger().error(f'Error parsing navigation parameters: {e}')

    def navigation_done_callback(self, future):
        """Handle navigation completion"""
        goal_handle = future.result()
        if goal_handle.accepted:
            self.get_logger().info('Navigation goal accepted')
        else:
            self.get_logger().error('Navigation goal rejected')

    def execute_pick_object(self, params_str):
        """Execute object picking action"""
        # Call gripper service to pick object
        if self.gripper_client.wait_for_service(timeout_sec=1.0):
            request = Trigger.Request()
            future = self.gripper_client.call_async(request)
            future.add_done_callback(self.gripper_response_callback)
        else:
            self.get_logger().error('Gripper service not available')

    def execute_release_object(self, params_str):
        """Execute object release action"""
        # Call gripper service to release object
        if self.gripper_client.wait_for_service(timeout_sec=1.0):
            request = Trigger.Request()
            future = self.gripper_client.call_async(request)
            future.add_done_callback(self.gripper_response_callback)
        else:
            self.get_logger().error('Gripper service not available')

    def gripper_response_callback(self, future):
        """Handle gripper service response"""
        try:
            response = future.result()
            if response.success:
                self.get_logger().info('Gripper action completed successfully')
            else:
                self.get_logger().error(f'Gripper action failed: {response.message}')
        except Exception as e:
            self.get_logger().error(f'Error in gripper response: {e}')

    def execute_stop_robot(self, params):
        """Stop robot movement"""
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info('Robot stopped')

    def publish_status(self, status_message):
        """Publish status message"""
        status_msg = String()
        status_msg.data = status_message
        self.status_pub.publish(status_msg)
```

## 13.7 Real-time Performance and Latency Optimization

### Latency Monitoring and Optimization
```python
# Performance monitoring for voice-to-action systems
import time
import statistics
from collections import deque

class VoiceSystemPerformanceMonitor:
    def __init__(self):
        self.command_latencies = deque(maxlen=100)
        self.processing_times = deque(maxlen=100)
        self.recognition_accuracies = deque(maxlen=100)

        self.start_times = {}

    def start_command_timer(self, command_id):
        """Start timing for a specific command"""
        self.start_times[command_id] = time.time()

    def end_command_timer(self, command_id):
        """End timing for a specific command and record latency"""
        if command_id in self.start_times:
            latency = time.time() - self.start_times[command_id]
            self.command_latencies.append(latency)
            del self.start_times[command_id]
            return latency
        return None

    def record_processing_time(self, processing_time):
        """Record Whisper processing time"""
        self.processing_times.append(processing_time)

    def record_accuracy(self, accuracy):
        """Record recognition accuracy"""
        self.recognition_accuracies.append(accuracy)

    def get_performance_metrics(self):
        """Get current performance metrics"""
        metrics = {}

        if self.command_latencies:
            metrics['avg_command_latency'] = statistics.mean(self.command_latencies)
            metrics['max_command_latency'] = max(self.command_latencies)
            metrics['min_command_latency'] = min(self.command_latencies)

        if self.processing_times:
            metrics['avg_processing_time'] = statistics.mean(self.processing_times)
            metrics['max_processing_time'] = max(self.processing_times)

        if self.recognition_accuracies:
            metrics['avg_accuracy'] = statistics.mean(self.recognition_accuracies)

        return metrics

    def is_performance_degraded(self):
        """Check if system performance is degraded"""
        metrics = self.get_performance_metrics()

        # Define degradation thresholds
        if 'avg_command_latency' in metrics:
            if metrics['avg_command_latency'] > 3.0:  # More than 3 seconds
                return True

        if 'avg_processing_time' in metrics:
            if metrics['avg_processing_time'] > 2.0:  # More than 2 seconds for processing
                return True

        return False
```

## 13.8 Error Handling and Robustness

### Error Handling for Voice Commands
```python
# Robust error handling for voice command systems
import logging
from enum import Enum

class VoiceCommandError(Enum):
    AUDIO_QUALITY_POOR = "Audio quality is too poor for recognition"
    NO_VOICE_DETECTED = "No voice activity detected"
    COMMAND_AMBIGUOUS = "Command is ambiguous or unclear"
    COMMAND_UNRECOGNIZED = "Command not recognized"
    SYSTEM_OVERLOADED = "System is overloaded, try again"
    ROBOT_BUSY = "Robot is currently busy with another task"
    SAFETY_VIOLATION = "Command would violate safety constraints"

class VoiceCommandErrorHandler:
    def __init__(self, node):
        self.node = node
        self.error_counts = {}
        self.last_error_time = {}

    def handle_error(self, error_type: VoiceCommandError, context=""):
        """Handle different types of voice command errors"""
        error_msg = f"{error_type.value} - {context}" if context else error_type.value

        # Log the error
        self.node.get_logger().error(error_msg)

        # Update error tracking
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1

        self.last_error_time[error_type] = time.time()

        # Take appropriate action based on error type
        if error_type == VoiceCommandError.AUDIO_QUALITY_POOR:
            self.suggest_audio_improvement()
        elif error_type == VoiceCommandError.COMMAND_AMBIGUOUS:
            self.request_clarification()
        elif error_type == VoiceCommandError.SAFETY_VIOLATION:
            self.log_safety_violation(context)

        return error_msg

    def suggest_audio_improvement(self):
        """Suggest ways to improve audio quality"""
        suggestions = [
            "Please speak closer to the microphone",
            "Reduce background noise if possible",
            "Speak more clearly and at a moderate pace"
        ]

        for suggestion in suggestions:
            self.node.get_logger().info(f"Audio improvement: {suggestion}")

    def request_clarification(self):
        """Request user to clarify the command"""
        # This would trigger a response to the user asking for clarification
        pass

    def log_safety_violation(self, context):
        """Log safety violations for analysis"""
        self.node.get_logger().warn(f"Safety violation prevented: {context}")
        # In a real system, this might trigger additional safety protocols
```

## 13.9 Practical Implementation and Testing

### Complete Voice Command System Launch File
```xml
<!-- voice_command_system.launch.py -->
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')
    whisper_model = LaunchConfiguration('whisper_model')

    return LaunchDescription([
        # Declare launch arguments
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time'
        ),
        DeclareLaunchArgument(
            'whisper_model',
            default_value='base',
            description='Whisper model to use (tiny, base, small, medium, large)'
        ),

        # Audio capture node
        Node(
            package='voice_command_system',
            executable='audio_capture_node',
            name='audio_capture',
            parameters=[{
                'use_sim_time': use_sim_time,
                'sample_rate': 16000,
                'chunk_size': 1024
            }],
            remappings=[
                ('/audio_input', '/microphone/audio_raw')
            ]
        ),

        # Voice command recognition node
        Node(
            package='voice_command_system',
            executable='voice_recognition_node',
            name='voice_recognition',
            parameters=[{
                'use_sim_time': use_sim_time,
                'whisper_model': whisper_model,
                'enable_continuous_listening': True
            }],
            remappings=[
                ('/raw_voice_command', '/audio_input'),
                ('/voice_command', '/recognized_command')
            ]
        ),

        # Voice command validation node
        Node(
            package='voice_command_system',
            executable='voice_validation_node',
            name='voice_validation',
            parameters=[{
                'use_sim_time': use_sim_time
            }],
            remappings=[
                ('/raw_voice_command', '/recognized_command'),
                ('/validated_voice_command', '/validated_command')
            ]
        ),

        # Voice to robot action mapper
        Node(
            package='voice_command_system',
            executable='voice_to_action_mapper',
            name='voice_to_action',
            parameters=[{
                'use_sim_time': use_sim_time
            }],
            remappings=[
                ('/validated_voice_command', '/validated_command'),
                ('/cmd_vel', '/robot/cmd_vel')
            ]
        )
    ])
```

## 13.10 Best Practices and Troubleshooting

### Best Practices for Voice Command Systems
- **Audio Quality**: Ensure high-quality audio input for best recognition accuracy
- **Vocabulary Design**: Create a well-defined vocabulary for your specific robot tasks
- **Error Handling**: Implement robust error handling and user feedback mechanisms
- **Performance Monitoring**: Continuously monitor system performance and adjust as needed
- **Privacy Considerations**: Handle voice data appropriately with privacy in mind
- **User Training**: Provide clear instructions and examples for users

### Common Issues and Solutions
- **High Latency**: Use smaller Whisper models or optimize hardware configuration
- **Poor Recognition**: Improve audio quality or adjust recognition thresholds
- **System Overload**: Implement queuing and load balancing mechanisms
- **Ambiguous Commands**: Create more specific command structures

## 13.11 Exercises and Activities

### Exercise 1: Basic Voice Command Setup
Install OpenAI Whisper and create a basic voice command recognition system that can recognize simple movement commands like "move forward" and "turn left".

### Exercise 2: Command Validation Implementation
Implement a command validation system that checks voice commands for safety constraints and semantic validity before execution.

### Exercise 3: Performance Optimization
Optimize the Whisper processing pipeline for real-time performance on your target hardware platform, measuring latency and accuracy.

### Exercise 4: Robot Integration
Integrate the voice command system with a simulated or real robot, implementing the complete pipeline from voice input to robot action.

## 13.12 Chapter Summary

This chapter covered the implementation of voice-to-action systems using OpenAI Whisper for robotics applications. We explored the complete pipeline from audio capture and processing to command recognition, validation, and execution. The chapter emphasized the importance of real-time performance, error handling, and safety considerations when implementing voice interfaces for robotic systems.

Whisper provides a powerful foundation for natural human-robot interaction, enabling more intuitive control methods that can significantly improve the usability of robotic systems in human environments.

## Key Terms and Definitions

- **Whisper**: OpenAI's speech recognition model for converting speech to text
- **ASR (Automatic Speech Recognition)**: Technology that converts spoken language to text
- **Voice Activity Detection (VAD)**: Detection of speech in audio signals
- **Voice Command**: Spoken instruction for robot control
- **Natural Language Processing (NLP)**: Processing of human language for computer understanding
- **Command Mapping**: Translation of recognized commands to robot actions
- **Real-time Processing**: Processing with minimal delay for interactive systems
- **Voice Command Validation**: Verification of voice commands before execution
- **Acoustic Model**: Model that maps audio signals to phonetic units
- **Language Model**: Model that assigns probabilities to sequences of words
- **End-to-End ASR**: Direct mapping from audio to text without intermediate steps
- **Latency**: Delay between input and output in a system
- **Confidence Score**: Measure of how certain the system is about its recognition

## Further Reading

1. OpenAI Whisper GitHub: https://github.com/openai/whisper
2. "Speech and Language Processing" by Daniel Jurafsky and James H. Martin
3. ROS 2 Audio Common Packages: http://wiki.ros.org/audio_common
4. "Robust Automatic Speech Recognition" by Hynek Hermansky
5. NVIDIA Riva Documentation: https://docs.nvidia.com/deeplearning/riva/index.html

## QA Checklist
- [ ] Chapter content accurately describes OpenAI Whisper for voice commands
- [ ] Audio capture and processing concepts are thoroughly explained
- [ ] Voice command validation is properly covered
- [ ] Integration with robot control systems is addressed
- [ ] Performance optimization techniques are mentioned
- [ ] Error handling and robustness are included
- [ ] Exercises are relevant and test understanding
- [ ] Key terms are defined and explained
- [ ] Content aligns with the module's focus on voice-to-action systems
- [ ] Links to further reading are valid
- [ ] Chapter summary effectively summarizes key concepts