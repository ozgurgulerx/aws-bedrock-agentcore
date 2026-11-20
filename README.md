# AWS GenAI engineering labs

How do you test a model client before it has access to a model? Which part of an agent owns a tool call? When should a prediction request go into a queue? This repository explores those questions through a runnable Amazon Bedrock client, a searchable AgentCore reference library, and architecture exercises for technical interviews.

| Explore | What to look for |
| --- | --- |
| [Bedrock Converse client](bedrock_first_request.py) · [tests](tests/test_bedrock_quickstart.py) | Follow one prompt from input validation to a model response. The client caps output tokens, sets timeouts, and returns text and usage as JSON. |
| [AgentCore architecture notes](skills/mindmap/references/agentcore-example.md) · [editable mind map](GenAI%20MindMap.mm) | Trace an order-support agent across its model loop, tools, session context, and execution environment. Compare a managed harness with a custom workflow. |
| [SageMaker inference guide](documentation/mindmaps/sagemaker-capabilities.md) | Choose among real-time, serverless, asynchronous, and batch inference using payload size, accelerator needs, traffic, and latency. |
| [Documentation search tool](documentation/tools/library.py) · [source registry](documentation/sources.json) | Build a local full-text index of selected AWS guides. Refreshes record source URLs and content hashes so a result can be traced back to its source. |

## Run the Bedrock lab

Start with the offline tests. They exercise the request payload, mixed response blocks, token limits, missing credentials, and service errors. They use a mocked AWS client and require no cloud account.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q tests --cov=bedrock_first_request
```

For a live call, use an AWS profile with permission to invoke a Converse-compatible model in your chosen region. Set the three variables below to values from your AWS environment. A successful invocation can incur model usage charges.

```sh
python bedrock_first_request.py \
  --profile "${AWS_PROFILE:?Set AWS_PROFILE}" \
  --region "${AWS_REGION:?Set AWS_REGION}" \
  --model-id "${BEDROCK_MODEL_ID:?Set BEDROCK_MODEL_ID}" \
  --prompt "Explain when an agent should ask for human approval." \
  --max-tokens 128
```

The client makes one attempt and reports the region, model ID, response text, and token usage on success. Verification for this release covers the offline request and response path. Live inference remains unverified.

## Work through two interview scenarios

**An order-support agent can look up orders and issue refunds. Where should authorization happen?** Walk through a refund from the user's request to the tool call. Identify which component carries session context, where the caller's permission is checked, and what happens if the tool times out after issuing the refund. The [AgentCore notes](skills/mindmap/references/agentcore-example.md) outline the harness and runtime responsibilities.

**An image-generation request has a 50 MB input, needs a GPU, and can return its result later. How would you serve it?** Sketch the path from an S3 upload to a queued invocation and an S3 result. Explain how queue time, startup, and execution affect the deadline. Use the [SageMaker guide](documentation/mindmaps/sagemaker-capabilities.md) to compare serving options.

## Search the AgentCore guides

From the repository root, refresh the local index once with Python 3 and curl, then search by topic. The refresh reads public AWS documentation and requires internet access. Subsequent searches run locally.

```sh
python3 documentation/tools/library.py refresh
python3 documentation/tools/library.py search "session isolation"
python3 documentation/tools/library.py search "execution role" --topic runtime
```
