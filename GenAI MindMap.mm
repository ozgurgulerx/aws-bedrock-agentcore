<?xml version="1.0" encoding="utf-8"?>
<map version="1.0.1">
    <node BACKGROUND_COLOR="#000000" COLOR="#FFFFFF" ID="ID_6DF58270-2424-46EB-99E9-A6EF57955A92" POSITION="right" STYLE="bubble" TEXT="GenAI MindMap ">
        <font BOLD="true" NAME="Avenir-Heavy" SIZE="35"/>
        <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="7"/>
        <node COLOR="#FFFFFF" ID="ID_2446EA0A-5716-43DB-9361-82FE9987C1FC" POSITION="right" STYLE="fork" TEXT="Amazon Bedrock AgentCore">
            <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
            <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="6"/>
            <node COLOR="#FFFFFF" ID="ID_7E1DF585-2179-4575-AF8F-467CF1A1E261" POSITION="right" STYLE="fork" TEXT="Agent implementation
Harness responsibilities:
• Run the model–tool loop
• Maintain context
• Handle failures">
                <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="5"/>
                <richcontent TYPE="NOTE">
                    <html>
                        <head/>
                        <body>Example — one agent, several steps
• User question. model requests a tool. tool runs. result returns to model. final answer.
• Carry relevant messages and tool results between calls.
• On a failed lookup, return an error or retry within limits.
• A harness is useful for a single agent; multi-agent coordination is a separate design choice.</body>
                    </html>
                </richcontent>
                <node COLOR="#FFFFFF" ID="ID_8BD03A8A-6DBF-47F7-A02E-0ABB5B76FFE9" POSITION="right" STYLE="fork" TEXT="Managed: AgentCore Harness
• AWS-provided agent software, powered by Strands
• AWS manages the loop and integrations
• Runs on AgentCore Runtime">
                    <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                    <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="4"/>
                    <richcontent TYPE="NOTE">
                        <html>
                            <head/>
                            <body>Example — configured order assistant
• Configure a model, support instructions and an order-lookup tool.
• A customer asks: Where is my order?
• The harness calls the model, executes the requested lookup and returns the result to the model.
• The model then produces the customer-facing answer.</body>
                        </html>
                    </richcontent>
                    <node COLOR="#FFFFFF" ID="ID_34EC317A-918B-4AFE-986F-49B0453627FA" POSITION="right" STYLE="fork" TEXT="Configure
• Model and instructions
• Tools and skills
• Memory and environment settings">
                        <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                        <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="3"/>
                        <richcontent TYPE="NOTE">
                            <html>
                                <head/>
                                <body>Example — support agent
• Choose a model and instruct it to explain order status clearly.
• Connect an order-lookup tool.
• Change the model or instructions through harness configuration.</body>
                            </html>
                        </richcontent>
                    </node>
                    <node COLOR="#FFFFFF" ID="ID_EF8174D6-4B07-4998-8DED-AE2F1D8ECA72" POSITION="right" STYLE="fork" TEXT="Extend behavior
• Use supported lifecycle hooks
• Add custom behavior at defined stages">
                        <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                        <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="3"/>
                        <richcontent TYPE="NOTE">
                            <html>
                                <head/>
                                <body>Example — custom execution logging
• At a supported lifecycle hook, record an application-specific audit event.
• Include the tool name and outcome, without sensitive arguments.
• The managed harness still controls the agent loop.</body>
                            </html>
                        </richcontent>
                    </node>
                    <node COLOR="#FFFFFF" ID="ID_889D0A52-E801-418A-A893-9C8B32B86BF5" POSITION="right" STYLE="fork" TEXT="Customize the environment
• Bring a container with your dependencies
• This does not replace the managed agent loop">
                        <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                        <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="3"/>
                        <richcontent TYPE="NOTE">
                            <html>
                                <head/>
                                <body>Example — spreadsheet analysis
• Supply a custom container containing pandas and your approved Python packages.
• The agent can use those dependencies in its environment.
• Changing the container does not itself replace the managed orchestration loop.</body>
                            </html>
                        </richcontent>
                    </node>
                    <node COLOR="#FFFFFF" ID="ID_657C2FF3-421F-465E-BF52-BBB8E301AB61" POSITION="right" STYLE="fork" TEXT="Move to your own implementation
• Export the harness to Strands code
• Customize the orchestration in code
• Deploy your agent to AgentCore Runtime">
                        <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                        <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="3"/>
                        <richcontent TYPE="NOTE">
                            <html>
                                <head/>
                                <body>Example — configuration is no longer enough
• Start with a configured support agent.
• Export it to Strands code.
• Add custom routing, bounded retries and approval logic in your code.
• Deploy the resulting agent to AgentCore Runtime.</body>
                            </html>
                        </richcontent>
                    </node>
                </node>
                <node COLOR="#FFFFFF" ID="ID_BCD49C5B-4AF3-4708-8B7B-A03401805006" POSITION="right" STYLE="fork" TEXT="Custom harness: your agent code / framework
• Strands Agents, LangGraph or your own code
• You own the orchestration implementation
• Deploy directly to AgentCore Runtime
• No managed Harness resource required">
                    <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                    <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="4"/>
                    <richcontent TYPE="NOTE">
                        <html>
                            <head/>
                            <body>Example — your own refund workflow
• Implement a LangGraph workflow: look up order. verify eligibility. obtain approval. issue refund.
• Your code manages state, retries and stopping conditions.
• AgentCore Runtime hosts this code; no managed Harness resource is needed.</body>
                        </html>
                    </richcontent>
                </node>
            </node>
            <node COLOR="#FFFFFF" ID="ID_2B1139FC-7208-4EBF-930F-6B7E62B1D0C0" POSITION="right" STYLE="fork" TEXT="Hosting / execution: AgentCore Runtime
• Isolated compute environment
• Session isolation and scaling
• Hosts managed Harness or your own agent code">
                <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="5"/>
                <richcontent TYPE="NOTE">
                    <html>
                        <head/>
                        <body>Example — two customer sessions
• Alice and Bob invoke the hosted agent in separate sessions.
• Runtime provides isolated execution environments.
• The harness or your framework runs the model–tool loop inside each environment.
• Your application must still authorize access to customer data.</body>
                    </html>
                </richcontent>
            </node>
            <node COLOR="#FFFFFF" ID="ID_4E328D02-B976-49A4-9E21-4DC3382AAA24" POSITION="right" STYLE="fork" TEXT="Agent architecture: multi-agent systems">
                <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="5"/>
                <richcontent TYPE="NOTE">
                    <html>
                        <head/>
                        <body>Example — customer-support team
• Coordinator: understands the request and delegates.
• Orders specialist: looks up delivery details.
• Refund specialist: checks refund eligibility.

Agents as tools: coordinator calls the needed specialist and combines its result into the answer.
Graph: a developer defines order lookup. eligibility check. approval. response.
Swarm: specialists decide which agent should handle the next step.

Creating several agents does not automatically connect them. Define delegation or handoffs and what context is passed. Agents may run together in one application or be separately hosted. Runtime supplies hosting; your chosen orchestration controls collaboration.

Official examples:
https://strandsagents.com/docs/learning/multi-agent-patterns-graph-workflows/
https://strandsagents.com/docs/user-guide/sdk/multi-agent/swarm/</body>
                    </html>
                </richcontent>
                <node COLOR="#FFFFFF" ID="ID_6269B843-A0E8-49E2-B1A9-AAF3A3DFF9FC" POSITION="right" STYLE="fork" TEXT="1. Define specialist agents
• Give each a role, instructions and tools
• Choose models and permissions per agent">
                    <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                    <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="4"/>
                </node>
                <node COLOR="#FFFFFF" ID="ID_4C641A3D-3F32-4974-A490-15896D6E903B" POSITION="right" STYLE="fork" TEXT="2. Choose coordination
• Agents as tools: coordinator delegates
• Graph: code defines routes and dependencies
• Swarm: agents choose handoffs">
                    <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                    <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="4"/>
                </node>
                <node COLOR="#FFFFFF" ID="ID_4147362C-3483-467E-8DF0-672AE7D9EE5B" POSITION="right" STYLE="fork" TEXT="3. Connect and deploy
• Implement coordination in Strands or LangGraph
• Run agents together or as separate services
• Use AgentCore Runtime for hosting">
                    <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                    <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="4"/>
                </node>
                <node COLOR="#FFFFFF" ID="ID_8514D367-2367-4C8B-83D3-035EBECAEA1A" POSITION="right" STYLE="fork" TEXT="4. Test and constrain
• Bound handoffs, retries, time and cost
• Authorize each tool and data access
• Evaluate the complete workflow">
                    <font BOLD="true" NAME="Avenir-Heavy" SIZE="25"/>
                    <edge COLOR="#FFFFFF" STYLE="bezier" WIDTH="4"/>
                </node>
            </node>
        </node>
    </node>
</map>