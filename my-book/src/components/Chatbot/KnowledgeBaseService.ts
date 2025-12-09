import { Message } from './Chatbot';

// Define the structure for our knowledge base entries
interface KnowledgeEntry {
  id: string;
  title: string;
  content: string;
  module: string;
  chapter: string;
  keywords: string[];
}

// Mock knowledge base - in a real implementation, this would be populated from the book content
const knowledgeBase: KnowledgeEntry[] = [
  {
    id: 'm1c1',
    title: 'Introduction to Physical AI & Robotics',
    content: 'Physical AI is a field that combines artificial intelligence with real-world robotics. It involves creating intelligent machines that can interact with the physical world through sensors and actuators. This chapter introduces the fundamental concepts of physical AI and robotics.',
    module: 'Module 1',
    chapter: 'Chapter 1',
    keywords: ['physical ai', 'robotics', 'intelligent machines', 'sensors', 'actuators', 'embodied intelligence']
  },
  {
    id: 'm1c2',
    title: 'Introduction to ROS 2',
    content: 'ROS (Robot Operating System) is a flexible framework for writing robot software. ROS 2 is the latest version with improved security, real-time support, and better architecture. This chapter covers ROS 2 concepts including nodes, topics, services, and actions.',
    module: 'Module 1',
    chapter: 'Chapter 2',
    keywords: ['ros', 'robot operating system', 'nodes', 'topics', 'services', 'actions', 'ros 2']
  },
  {
    id: 'm1c3',
    title: 'Basic Robot Kinematics and Dynamics',
    content: 'Robot kinematics is the study of motion in robotic systems. Forward kinematics calculates the position of the end effector given joint angles, while inverse kinematics calculates joint angles needed to achieve a desired end effector position. This chapter covers both concepts with practical examples.',
    module: 'Module 1',
    chapter: 'Chapter 3',
    keywords: ['kinematics', 'forward kinematics', 'inverse kinematics', 'dynamics', 'end effector', 'joint angles']
  },
  {
    id: 'm1c4',
    title: 'Introduction to Gazebo Simulation',
    content: 'Gazebo is a 3D simulation environment for robotics that provides realistic physics simulation and rendering capabilities. It allows testing robot algorithms in a safe virtual environment before deployment on real hardware. This chapter covers Gazebo basics and integration with ROS.',
    module: 'Module 1',
    chapter: 'Chapter 4',
    keywords: ['gazebo', 'simulation', 'physics', 'robotics', 'virtual environment', 'ros integration']
  },
  {
    id: 'm2c5',
    title: 'Advanced ROS 2 Concepts',
    content: 'This chapter delves into advanced ROS 2 concepts including parameter management, lifecycle nodes, and custom message types. It also covers best practices for building robust ROS 2 applications and debugging techniques.',
    module: 'Module 2',
    chapter: 'Chapter 5',
    keywords: ['ros 2', 'advanced', 'parameters', 'lifecycle nodes', 'custom messages', 'debugging']
  },
  {
    id: 'm2c6',
    title: 'NVIDIA Isaac Sim for High-Fidelity Simulation',
    content: 'NVIDIA Isaac Sim is a high-fidelity simulation platform built on NVIDIA Omniverse. It provides USD-based workflows for creating complex robotic simulation environments with photorealistic rendering and accurate physics simulation.',
    module: 'Module 2',
    chapter: 'Chapter 6',
    keywords: ['isaac sim', 'nvidia', 'omniverse', 'usd', 'simulation', 'photorealistic', 'physics']
  },
  {
    id: 'm2c7',
    title: 'Unity and ROS-TCP-Connector for Robotics',
    content: 'Unity is a game development platform that can be used for robotics simulation. The ROS-TCP-Connector enables communication between ROS and Unity, allowing for advanced visualization and simulation scenarios.',
    module: 'Module 2',
    chapter: 'Chapter 7',
    keywords: ['unity', 'ros-tcp-connector', 'simulation', 'visualization', 'game engine']
  },
  {
    id: 'm2c8',
    title: 'Introduction to Robot Perception (Vision)',
    content: 'Robot perception is the ability of a robot to interpret its environment through sensors. This chapter focuses on vision-based perception including camera models, image processing, and object detection techniques.',
    module: 'Module 2',
    chapter: 'Chapter 8',
    keywords: ['perception', 'vision', 'camera', 'image processing', 'object detection', 'sensors']
  },
  {
    id: 'm2c9',
    title: 'Introduction to Robot Perception (LiDAR & IMU)',
    content: 'This chapter covers perception using LiDAR and IMU sensors. LiDAR provides accurate distance measurements for 3D mapping, while IMU sensors provide orientation and acceleration data for robot localization.',
    module: 'Module 2',
    chapter: 'Chapter 9',
    keywords: ['lidar', 'imu', 'perception', 'mapping', 'localization', 'sensors']
  },
  {
    id: 'm3c10',
    title: 'Nav2 for Autonomous Navigation',
    content: 'Nav2 is the navigation stack for ROS 2 that provides complete path planning, obstacle avoidance, and localization capabilities for mobile robots. This chapter covers Nav2 configuration and implementation.',
    module: 'Module 3',
    chapter: 'Chapter 10',
    keywords: ['nav2', 'navigation', 'path planning', 'obstacle avoidance', 'localization', 'mobile robots']
  },
  {
    id: 'm3c11',
    title: 'Humanoid Robot Kinematics and Control',
    content: 'Humanoid robots have complex kinematic structures with multiple degrees of freedom. This chapter covers inverse kinematics for humanoid robots and control strategies for stable locomotion.',
    module: 'Module 3',
    chapter: 'Chapter 11',
    keywords: ['humanoid', 'kinematics', 'inverse kinematics', 'locomotion', 'control', 'degrees of freedom']
  },
  {
    id: 'm3c12',
    title: 'Robot Manipulation and Grasping',
    content: 'Robot manipulation involves controlling robot arms to interact with objects. This chapter covers MoveIt 2 for motion planning and grasping strategies for various object types.',
    module: 'Module 3',
    chapter: 'Chapter 12',
    keywords: ['manipulation', 'grasping', 'moveit 2', 'motion planning', 'robot arms', 'objects']
  },
  {
    id: 'm3c13',
    title: 'Introduction to Learning for Robotics',
    content: 'Machine learning techniques are increasingly important in robotics. This chapter introduces reinforcement learning, imitation learning, and other approaches for enabling robots to learn from experience.',
    module: 'Module 3',
    chapter: 'Chapter 13',
    keywords: ['learning', 'reinforcement learning', 'imitation learning', 'machine learning', 'robotics']
  },
  {
    id: 'm4c14',
    title: 'Vision-Language-Action (VLA) Models for Robotics',
    content: 'Vision-Language-Action models integrate visual perception, language understanding, and action execution. These models enable robots to understand natural language commands and perform complex tasks in real-world environments.',
    module: 'Module 4',
    chapter: 'Chapter 14',
    keywords: ['vla', 'vision-language-action', 'natural language', 'perception', 'action execution']
  },
  {
    id: 'm4c15',
    title: 'Advanced Perception: Object Detection & VSLAM',
    content: 'This chapter covers advanced perception techniques including deep learning-based object detection and Visual Simultaneous Localization and Mapping (VSLAM) for real-time environment understanding.',
    module: 'Module 4',
    chapter: 'Chapter 15',
    keywords: ['object detection', 'vslam', 'visual slam', 'deep learning', 'environment understanding']
  }
];

class KnowledgeBaseService {
  // Search the knowledge base for relevant entries based on user query
  async search(query: string): Promise<KnowledgeEntry[]> {
    const lowerQuery = query.toLowerCase();
    const queryTerms = lowerQuery.split(/\s+/).filter(term => term.length > 0);

    // Calculate relevance scores for each knowledge entry
    const scoredEntries = knowledgeBase.map(entry => {
      let score = 0;

      // Score based on keyword matches
      for (const keyword of entry.keywords) {
        if (lowerQuery.includes(keyword.toLowerCase())) {
          score += 10;
        }
      }

      // Score based on title matches
      if (entry.title.toLowerCase().includes(lowerQuery)) {
        score += 20;
      } else {
        for (const term of queryTerms) {
          if (entry.title.toLowerCase().includes(term)) {
            score += 5;
          }
        }
      }

      // Score based on content matches
      if (entry.content.toLowerCase().includes(lowerQuery)) {
        score += 15;
      } else {
        for (const term of queryTerms) {
          if (entry.content.toLowerCase().includes(term)) {
            score += 3;
          }
        }
      }

      return { entry, score };
    });

    // Sort by score and return top 3 results
    return scoredEntries
      .filter(item => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 3)
      .map(item => item.entry);
  }

  // Get a comprehensive answer based on search results
  async getAnswer(query: string): Promise<string> {
    const results = await this.search(query);

    if (results.length === 0) {
      return "I couldn't find specific information about that topic in the Physical AI & Humanoid Robotics Textbook. Could you try rephrasing your question or ask about a different topic? The textbook covers ROS 2, Gazebo simulation, humanoid robotics, navigation, perception, manipulation, and Vision-Language-Action models.";
    }

    // Build a comprehensive response from the results
    let response = `Based on the Physical AI & Humanoid Robotics Textbook:\n\n`;

    for (const result of results) {
      response += `**${result.module}, ${result.title}**\n`;
      response += `${result.content}\n\n`;
    }

    if (results.length < knowledgeBase.length) {
      response += "For more detailed information, please refer to the specific chapters in the textbook.";
    }

    return response;
  }
}

export const knowledgeBaseService = new KnowledgeBaseService();