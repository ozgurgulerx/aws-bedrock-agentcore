# AgentCore learning-map example

This captures the learning-map structure used in this session. Recheck current AWS documentation before reusing technical claims. It is an example, not a requirement for other subjects.

## Structure and example notes

- Amazon Bedrock AgentCore
  - Agent implementation / harness responsibilities: model–tool loop, context, failures.
    - Managed AgentCore Harness
      - Configure: models, instructions, tools, skills, memory, environment.
        - Note example: configure an order-support assistant with a get_order tool and instructions to explain delivery status.
      - Extend behavior: supported lifecycle hooks.
        - Note example: emit an audit event at a supported lifecycle stage; verify which hook destinations can enforce decisions versus only receive notifications.
      - Customize environment: dependencies/container.
        - Note example: supply a container with pandas for data processing; this is distinct from replacing orchestration code.
      - Move to own implementation: export, customize, deploy.
        - Note example: export to Strands, inspect export limitations, implement custom approval routing, deploy to Runtime.
    - Custom harness: framework or application code.
      - Note example: a LangGraph refund workflow owns its routing and approval logic and runs on Runtime.
  - Hosting / execution: AgentCore Runtime.
    - Note example: separate user sessions execute in isolated environments; application authorization still controls access to orders and tools.
  - Architecture: multi-agent systems.
    - Define specialists: roles, instructions, tools, models, permissions.
    - Choose coordination: agents as tools, graphs, swarms.
      - Note example: a coordinator delegates order lookup and refund-policy research to separate specialists. A graph specifies routes; a swarm uses supported handoffs.
    - Connect and deploy: together or separate services.
    - Test and constrain: handoffs, retries, time/cost, permissions, end-to-end evaluation.
      - Note example: cap handoffs and tool retries, verify refund authorization, evaluate the complete answer and actions.

Keep these distinctions visible: orchestration is not hosting; a custom container is not necessarily a custom loop; multi-agent coordination is an architecture choice, not a prerequisite for an agent.

## Documentation starting points

These destinations were used for the map; verify availability and relevance before future edits.

| Topic | Official documentation |
|---|---|
| AgentCore overview | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/ |
| Harness versus Runtime | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-vs-runtime.html |
| Managed harness | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness.html |
| Configuration | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-get-started.html |
| Models and instructions | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-models.html |
| Lifecycle hooks | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-lifecycle-hooks.html |
| Environment | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-environment.html |
| Export to code | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-export.html |
| Deploy custom code | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli.html |
| Runtime | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html |
| Security controls | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-security.html |
| Observability | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-get-started.html |
| Multi-agent patterns | https://strandsagents.com/docs/user-guide/sdk/multi-agent/multi-agent-patterns/ |
| Graphs | https://strandsagents.com/docs/user-guide/sdk/multi-agent/graph/ |
| Swarms | https://strandsagents.com/docs/user-guide/sdk/multi-agent/swarm/ |
| Agent-to-agent communication | https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/ |

A broad node such as Test and constrain needs more than one reference: attach the most relevant primary link and put evaluation/observability and limits references in notes. Do not imply that a security page documents the whole topic.
