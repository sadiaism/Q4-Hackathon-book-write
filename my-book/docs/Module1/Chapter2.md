# Chapter 2: ROS 2 Nodes, Topics, and Services

## Learning Objectives
After completing this chapter, students will be able to:
- Create and manage ROS 2 nodes for robot control
- Implement publisher-subscriber communication using topics
- Design and use service-based communication patterns
- Use ROS 2 command-line tools for introspection and debugging
- Understand when to use topics vs services for different communication needs

## 2.1 Understanding ROS 2 Nodes

Nodes are the fundamental building blocks of any ROS 2 program. A node is a process that performs computation and is the basic unit of executable code in ROS 2. In the context of the robotic nervous system, nodes can be thought of as specialized cells or organs that perform specific functions, such as processing sensor data, controlling actuators, or making high-level decisions.

Each node typically performs a specific task within the robotic system and communicates with other nodes through topics, services, or actions. Nodes are designed to be modular and reusable, allowing complex robotic systems to be built from smaller, specialized components.

### Creating Nodes in C++
In C++, nodes are created by inheriting from the `rclcpp::Node` class. Here's a basic structure:

```cpp
#include "rclcpp/rclcpp.hpp"

class MyNode : public rclcpp::Node
{
public:
    MyNode() : Node("node_name")
    {
        // Node initialization code
    }

private:
    // Member variables and methods
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MyNode>());
    rclcpp::shutdown();
    return 0;
}
```

### Creating Nodes in Python
In Python, nodes are created by inheriting from the `Node` class:

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('node_name')
        # Node initialization code

def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 2.2 Topics and Publisher-Subscriber Pattern

Topics implement the publish-subscribe communication pattern, which is one of the most common communication methods in ROS 2. This pattern allows for loose coupling between nodes, where publishers send messages to a topic without knowing who subscribes to it, and subscribers receive messages without knowing who published them.

### Publishers
A publisher is a node that sends messages to a topic. Publishers are created within nodes and must specify the message type and topic name. The publisher sends data at regular intervals or in response to events.

### Creating a Publisher (C++)
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class Talker : public rclcpp::Node
{
public:
    Talker() : Node("talker")
    {
        publisher_ = this->create_publisher<std_msgs::msg::String>("topic", 10);
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(500),
            std::bind(&Talker::timer_callback, this));
    }

private:
    void timer_callback()
    {
        auto message = std_msgs::msg::String();
        message.data = "Hello World";
        RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
        publisher_->publish(message);
    }

    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
};
```

### Creating a Publisher (Python)
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World'
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
```

### Subscribers
A subscriber receives messages from a topic. Subscribers are also created within nodes and must specify the topic name and message type. When a message is received, a callback function is executed.

### Creating a Subscriber (C++)
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class Listener : public rclcpp::Node
{
public:
    Listener() : Node("listener")
    {
        subscription_ = this->create_subscription<std_msgs::msg::String>(
            "topic", 10,
            std::bind(&Listener::topic_callback, this, std::placeholders::_1));
    }

private:
    void topic_callback(const std_msgs::msg::String::SharedPtr msg)
    {
        RCLCPP_INFO(this->get_logger(), "I heard: '%s'", msg->data.c_str());
    }

    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};
```

### Creating a Subscriber (Python)
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)
```

## 2.3 Services for Request-Reply Communication

While topics are excellent for continuous data streams, services provide a request-reply communication pattern that is more appropriate for specific tasks that have a clear beginning and end. Services are synchronous, meaning the client waits for the server to complete the requested action before continuing.

### Service Definition
Services are defined using `.srv` files that specify the request and response message types:

```
# Request message
string request_data
---
# Response message
bool success
string message
```

### Creating a Service Server (C++)
```cpp
#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

class ServiceServer : public rclcpp::Node
{
public:
    ServiceServer() : Node("service_server")
    {
        service_ = this->create_service<example_interfaces::srv::AddTwoInts>(
            "add_two_ints",
            [this](const example_interfaces::srv::AddTwoInts::Request::SharedPtr request,
                   example_interfaces::srv::AddTwoInts::Response::SharedPtr response)
            {
                response->sum = request->a + request->b;
                RCLCPP_INFO(this->get_logger(), "Incoming request: %ld + %ld = %ld",
                           request->a, request->b, response->sum);
            });
    }

private:
    rclcpp::Service<example_interfaces::srv::AddTwoInts>::SharedPtr service_;
};
```

### Creating a Service Server (Python)
```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class ServiceServer(Node):
    def __init__(self):
        super().__init__('service_server')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info('Incoming request: %d + %d = %d' % (request.a, request.b, response.sum))
        return response
```

### Creating a Service Client (C++)
```cpp
#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/srv/add_two_ints.hpp"

class ServiceClient : public rclcpp::Node
{
public:
    ServiceClient() : Node("service_client")
    {
        client_ = this->create_client<example_interfaces::srv::AddTwoInts>("add_two_ints");

        while (!client_->wait_for_service(std::chrono::seconds(1))) {
            if (!rclcpp::ok()) {
                return;
            }
            RCLCPP_INFO(this->get_logger(), "Service not available, waiting again...");
        }
    }

    void send_request(int a, int b)
    {
        auto request = std::make_shared<example_interfaces::srv::AddTwoInts::Request>();
        request->a = a;
        request->b = b;

        auto future = client_->async_send_request(request);
        // Process response when available
    }

private:
    rclcpp::Client<example_interfaces::srv::AddTwoInts>::SharedPtr client_;
};
```

### Creating a Service Client (Python)
```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class ServiceClient(Node):
    def __init__(self):
        super().__init__('service_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')

    def send_request(self, a, b):
        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        self.future = self.cli.call_async(request)
```

## 2.4 When to Use Topics vs Services

Understanding when to use topics versus services is crucial for effective ROS 2 design:

### Use Topics When:
- You need continuous data streaming (sensor data, robot state)
- Multiple nodes need to receive the same information simultaneously
- Real-time performance is critical
- The communication is one-way (publish only)
- You want loose coupling between publisher and subscriber

### Use Services When:
- You need a specific result from a computation
- The interaction has a clear start and end
- You need guaranteed delivery and response
- The client needs to wait for the operation to complete
- You're implementing a remote procedure call

## 2.5 Quality of Service (QoS) for Topics

Quality of Service settings allow fine-tuning of topic behavior to match specific requirements:

```cpp
// Reliability: RELIABLE or BEST_EFFORT
rclcpp::QoS qos_profile(10);
qos_profile.reliability(RMW_QOS_POLICY_RELIABILITY_RELIABLE);

// Durability: VOLATILE or TRANSIENT_LOCAL
qos_profile.durability(RMW_QOS_POLICY_DURABILITY_VOLATILE);

publisher_ = this->create_publisher<std_msgs::msg::String>("topic", qos_profile);
```

## Exercises and Activities

### Exercise 1: Node Creation
Create a ROS 2 node that publishes the current time at 1 Hz frequency. Then create a subscriber node that listens to this time topic and logs the received timestamps.

### Exercise 2: Service Implementation
Implement a service that accepts two coordinates (x, y) and returns the Euclidean distance from the origin. Test your service with a client node.

### Exercise 3: Topic vs Service Decision
For each of the following scenarios, decide whether to use a topic or a service and justify your choice:
- Publishing laser scan data from a LiDAR sensor
- Requesting the robot to move to a specific position
- Broadcasting the robot's current battery level
- Requesting a map from the mapping system

## Key Terms and Definitions

- **Node**: A process that performs computation in ROS 2
- **Topic**: Named bus for message exchange using publish-subscribe pattern
- **Publisher**: Node that sends messages to a topic
- **Subscriber**: Node that receives messages from a topic
- **Service**: Synchronous request/reply communication pattern
- **Service Server**: Node that provides a service
- **Service Client**: Node that requests a service
- **Message**: Data structure exchanged via topics
- **Service Definition**: File defining request and response types for services
- **Quality of Service (QoS)**: Configurable parameters that define how messages are handled

## Further Reading

1. ROS 2 Topics Tutorial: https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.html
2. ROS 2 Services Tutorial: https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Services/Understanding-ROS2-Services.html
3. ROS 2 Quality of Service: https://docs.ros.org/en/humble/Concepts/About-Quality-of-Service-Settings.html

## Chapter Summary

This chapter focused on the fundamental communication patterns in ROS 2: nodes, topics, and services. We explored how to create nodes in both C++ and Python, implement publisher-subscriber communication for continuous data streams, and design service-based interactions for request-reply scenarios. Understanding when to use topics versus services is crucial for effective robotic system design, as each pattern serves different purposes in the robotic nervous system.

## QA Checklist
- [ ] Chapter content accurately describes ROS 2 nodes
- [ ] Publisher-subscriber pattern is thoroughly explained
- [ ] Service-based communication is properly described
- [ ] Code examples are provided for both C++ and Python
- [ ] When to use topics vs services is clearly explained
- [ ] Quality of Service settings are mentioned
- [ ] Exercises are relevant and test understanding
- [ ] Key terms are defined and explained
- [ ] Content aligns with the module's focus on ROS 2 communication
- [ ] Links to further reading are valid
- [ ] Chapter summary effectively summarizes key concepts