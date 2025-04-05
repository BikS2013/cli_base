# Introducing Graphite — An Event Driven AI Agent Framework

**By Craig Li, Ph.D**  
*Published in Binome · 9 min read · 3 days ago*

---

Graphite is an open-source framework for building domain-specific AI assistants using composable agentic workflows. It offers a highly extensible platform that can be tailored to unique business requirements, enabling organizations to develop custom workflows suited to their specific domains.

We've mentioned this product in our previous posts, and we're proud to share that we have now open sourced Graphite on GitHub! Check it out and give us a Star ⭐ there if you like it!

[GitHub - binome-dev/graphite](https://github.com/binome-dev/graphite)  
*Contribute to binome-dev/graphite development by creating an account on GitHub.*

You might be wondering, "With AI solutions like ChatGPT, Claude, and various agentic platforms and frameworks already available, why create another one?" The short answer: we identified a gap in solving real-world problems with AI tools. Many generic agents — like typical ReAct or CoT agents — struggle with mission-critical tasks where mistakes can be costly.

Graphite provides a straightforward and controllable framework for building workflows, allowing large language models (LLMs) not just to reason and plan, but to operate within a defined, auditable, and easily restorable workflow. It also includes essential features such as observability, idempotency, and auditability out of the box.

In this post, we'll introduce Graphite briefly, from its architecture to its key features, and provide a simple example: using Graphite to build a Know-Your-Client AI assistant.

## The Architecture: Simple, Powerful, and Composable

Graphite is structured into three conceptual layers — Assistants, Nodes, and Tools:

- **Assistants** orchestrate the workflow and manage the conversation state.
- **Nodes** encapsulate discrete logic, each dedicated to a specific function (e.g., an LLM call or function execution).
- **Tools** are pure functions responsible for executing tasks, such as calling an API or running a Python function.

Additionally, Graphite employs event sourcing pattern to record every state change. Whenever an Assistant, Node, or Tool is invoked, responds, or fails, a corresponding event is generated and stored in the event store.

The command pattern cleanly separates request initiators from executors through well-defined Command objects and handlers. These Commands carry all the necessary context, enabling nodes to invoke tools in a self-contained and straightforward manner.

The nodes coordinate through a lightweight, Pub/Sub workflow orchestration mechanism.

Workflow orchestrates interactions among nodes using a Pub/Sub pattern with in-memory message queuing.

This architecture unlocks plug-and-play modularity — you can build workflows like Lego bricks, add or remove nodes, and isolate failures with surgical precision.

## The Features — What Makes Graphite Shine

The core design principles we've introduced above shows that set Graphite apart from other agent frameworks are:

### A Simple 3-Layer Execution Model
Three distinct layers — assistant, node, and tool — manage execution, while a dedicated workflow layer oversees orchestration.

### Pub/Sub Event-Driven Orchestration
Communication relies on publishing and subscribing to events, ensuring a decoupled, modular flow of data throughout the system.

### Events as the Single Source of Truth
All operational states and transitions are recorded as events, providing a uniform way to track and replay system behavior if needed.

Combining these elements, Graphite provides a production-grade AI application framework capable of operating reliably at scale, handling failures gracefully, and maintaining user and stakeholder trust. Four essential capabilities form the backbone of this approach:

1. **Observability**  
   Complex AI solutions involve multiple steps, data sources, and models. Graphite's event-driven architecture, logging, and tracing make it possible to pinpoint bottlenecks or errors in real time, ensuring that each component's behavior is transparent and measurable.

2. **Idempotency**  
   Asynchronous workflows often require retries when partial failures occur or network conditions fluctuate. Graphite's design emphasizes idempotent operations, preventing pub/sub data duplication or corruption when calls must be repeated.

3. **Auditability**  
   By treating events as the single source of truth, Graphite automatically logs every state change and decision path. This level

3. **Auditability**  
   By treating events as the single source of truth, Graphite automatically logs every state change and decision path. This level of detailed record-keeping is indispensable for users working in regulated sectors or who need full traceability for debugging and compliance.

4. **Restorability**  
   Long-running AI tasks risk substantial rework if they fail mid-execution. In Graphite, checkpoints and event-based playback enable workflows to resume from the precise point of interruption, minimizing downtime and maximizing resource efficiency.

Together, these capabilities — observability, idempotency, auditability, and restorability — distinguish Graphite as a framework for building robust and trustworthy AI applications. Below is a detailed breakdown of how Graphite implements each feature.

## Show Your Code — KYC Assistant

When designing an AI-based workflow, keep in mind that large language models introduce uncertainty. It's helpful to follow Occam's razor principle, which means the simpler the workflow, the better.

### Design the workflow

Suppose you want to create a "Know Your Client (KYC)" assistant for a gym registration process, with human-in-the-loop (HITL) functionality. The user must provide their full name and email address to finish the registration workflow. And if anything is missing, the workflow pauses and asks client for more information. Clearly the real world problem would need more information, but here we just simplify it for this demo.

### Build the assistant

Firstly, install Graphite from pip

```bash
pip install grafi
```

From above workflow graph, we will need add following components:

**7 topics:**

1. agent input topic (framework provided)
```python
from grafi.common.topics.topic import agent_input_topic
```

2. user info extract topic
```python
user_info_extract_topic = Topic(name="user_info_extract_topic")
```

3. human call topic
```python
hitl_call_topic = Topic(
    name="hitl_call_topic",
    condition=lambda msgs: msgs[-1].tool_calls[0].function.name
    != "register_client",
)
```

4. human in the loop topic (framework provided)
```python
from grafi.common.topics.human_request_topic import human_request_topic
```

5. register user topic topic
```python
register_user_topic = Topic(
    name="register_user_topic",
    condition=lambda msgs: msgs[-1].tool_calls[0].function.name
    == "register_client",
)
```

6. register user respond topic
```python
register_user_respond_topic = Topic(name="register_user_respond")
```

7. agent output topic (framework provided)
```python
from grafi.common.topics.output_topic import agent_output_topic
```

**5 nodes:**

1. LLM Node [User info extract node] to extract name and email from user input
```python
user_info_extract_node = (
    LLMNode.Builder()
    .name("ThoughtNode")
    .subscribe(
        SubscriptionBuilder()
        .subscribed_to(agent_input_topic)
        .or_()
        .subscribed_to(human_request_topic)
        .build()
    )
    .command(
        LLMResponseCommand.Builder()
        .llm(
            OpenAITool.Builder()
            .name("ThoughtLLM")
            .api_key(self.api_key)
            .model(self.model)
            .system_message(self.user_info_extract_system_message)
            .build()
        )
        .build()
    )
    .publish_to(user_info_extract_topic)
    .build()
)
```

2. LLM Node [action] to create action given extracted information
```python
action_node = (
    LLMNode.Builder()
    .name("ActionNode")
    .subscribe(user_info_extract_topic)
    .command(
        LLMResponseCommand.Builder()
        .llm(
            OpenAITool.Builder()
            .name("ActionLLM")
            .api_key(self.api_key)
            .model(self.model)
            .system_message

```python
            .system_message(self.action_llm_system_message)
            .build()
        )
        .build()
    )
    .publish_to(hitl_call_topic)
    .publish_to(register_user_topic)
    .build()
)
```

3. Function Tool Node [human-in-the-loop] to ask user for missing information if any
```python
human_request_function_call_node = (
    LLMFunctionCallNode.Builder()
    .name("HumanRequestNode")
    .subscribe(hitl_call_topic)
    .command(
        FunctionCallingCommand.Builder()
        .function_tool(self.hitl_request)
        .build()
    )
    .publish_to(human_request_topic)
    .build()
)
```

4. Function Tool Node [register user] to register the client
```python
register_user_node = (
    LLMFunctionCallNode.Builder()
    .name("FunctionCallRegisterNode")
    .subscribe(register_user_topic)
    .command(
        FunctionCallingCommand.Builder()
        .function_tool(self.register_request)
        .build()
    )
    .publish_to(register_user_respond_topic)
    .build()
)
```

5. LLM Node [response to user] to draft the final respond to user
```python
user_reply_node = (
    LLMNode.Builder()
    .name("LLMResponseToUserNode")
    .subscribe(register_user_respond_topic)
    .command(
        LLMResponseCommand.Builder()
        .llm(
            OpenAITool.Builder()
            .name("ResponseToUserLLM")
            .api_key(self.api_key)
            .model(self.model)
            .system_message(self.summary_llm_system_message)
            .build()
        )
        .build()
    )
    .publish_to(agent_output_topic)
    .build()
)
```

And here is the source code — KYC assistant

Then let's write a simple code to test it:

```python
import json
import uuid

from kyc_assistant import KycAssistant
from grafi.common.decorators.llm_function import llm_function
from grafi.common.models.execution_context import ExecutionContext
from grafi.common.models.message import Message
from grafi.tools.functions.function_tool import FunctionTool


class ClientInfo(FunctionTool):

    @llm_function
    def request_client_information(self, question_description: str):
        """
        Requests client input for personal information based on a given question description.
        """
        return json.dumps({"question_description": question_description})


class RegisterClient(FunctionTool):

    @llm_function
    def register_client(self, name: str, email: str):
        """
        Registers a user based on their name and email.
        """
        return f"User {name}, email {email} has been registered."


user_info_extract_system_message = """
"You are a strict validator designed to check whether a given input contains a user's full name and email address. Your task is to analyze the input and determine if both a full name (first and last name) and a valid email address are present.

### Validation Criteria:
- **Full Name**: The input should contain at least two words that resemble a first and last name. Ignore common placeholders (e.g., 'John Doe').
- **Email Address**: The input should include a valid email format (e.g., example@domain.com).
- **Case Insensitivity**: Email validation should be case insensitive.
- **Accuracy**: Avoid false positives by ensuring random text, usernames, or partial names don't trigger validation.
- **Output**: Respond with Valid if both a full name and an email are present, otherwise respond with Invalid. Optionally, provide a reason why the input is invalid.

### Example Responses:
- **Input**: "John Smith, john.smith@email.com" → **Output**: "Valid"
- **Input**: "john.smith@email.com"

- **Input**: "john.smith@email.com" → **Output**: "Invalid: Missing full name"
- **Input**: "John Smith" → **Output**: "Invalid: Missing email address"
- **Input**: "My name is J. Smith" → **Output**: "Invalid: Incomplete name (missing first or last name)"
- **Input**: "Contact me at email" → **Output**: "Invalid: No valid email format detected"

Your goal is to be thorough and accurate in your validation, ensuring that only inputs with complete information are marked as valid.
"""

action_llm_system_message = """
You are a gym registration assistant. Your job is to help users register for the gym by collecting their full name and email address.

If the user has provided both their full name and email address, you should call the register_client function with these details.

If any information is missing, you should call the request_client_information function to ask for the specific missing information.

Available functions:
- register_client(name: str, email: str): Registers a client with their name and email
- request_client_information(question_description: str): Asks the user for specific missing information

Examples:
1. User provides complete information: "My name is John Smith and my email is john.smith@example.com"
   -> Call register_client with name="John Smith", email="john.smith@example.com"

2. User provides only name: "I'm Jane Doe"
   -> Call request_client_information with question_description="Please provide your email address to complete registration."

3. User provides only email: "My email is user@example.com"
   -> Call request_client_information with question_description="Please provide your full name to complete registration."

4. User provides neither: "I want to register for the gym"
   -> Call request_client_information with question_description="To register, please provide your full name and email address."

Always be polite and helpful in your interactions.
"""

summary_llm_system_message = """
You are a gym registration assistant. Your job is to provide a friendly and helpful response to users after they have successfully registered for the gym.

The registration system has just processed their information and you need to:
1. Confirm their registration was successful
2. Thank them for registering
3. Provide a brief welcome message
4. Let them know what to expect next

Keep your response concise, friendly, and professional. Do not ask for any additional information as the registration is now complete.
"""

kyc_assistant = KycAssistant(
    api_key="<your-openai-api-key>",
    model="gpt-4-turbo-preview",
    user_info_extract_system_message=user_info_extract_system_message,
    action_llm_system_message=action_llm_system_message,
    summary_llm_system_message=summary_llm_system_message,
    hitl_request=ClientInfo(),
    register_request=RegisterClient(),
)

# Create a new execution context
execution_context = ExecutionContext(
    execution_id=str(uuid.uuid4()),
    user_id="user-1",
    conversation_id="conversation-1",
)

# Create a new message
message = Message(
    role="user",
    content="Hi, I'm John Doe and my email is john.doe@example.com",
)

# Run the assistant
kyc_assistant.run(execution_context, message)
```

## Conclusion

Graphite is designed to be a robust, production-ready framework for building AI assistants. It provides a simple, composable architecture that allows you to build complex workflows with ease. The event-driven design ensures that your workflows are observable, idempotent, auditable, and restorable.

We're excited to see what you build with Graphite! Check out our GitHub repository for more examples and documentation.

[GitHub - binome-dev/graphite](https://github.com/binome-dev/graphite)

FILENAME: introducing-graphite-event-driven-ai-agent-framework.md

I chose this filename because it accurately reflects the main topic of the article - introducing the Graphite framework, which is described as an event-driven AI agent framework. The filename is descriptive, concise, and follows standard markdown naming conventions.

CONVERSION COMPLETE