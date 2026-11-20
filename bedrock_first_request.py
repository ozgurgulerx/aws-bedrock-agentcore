"""A bounded Bedrock Converse request using the AWS credential provider chain."""

import argparse
import json
import sys

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError


def run_request(client, model_id, prompt, max_tokens=128):
    """Send one request and return text and usage without credential material."""
    if not isinstance(model_id, str) or not model_id.strip():
        raise ValueError("Model ID must not be blank.")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must not be blank.")
    if type(max_tokens) is not int or not 1 <= max_tokens <= 1024:
        raise ValueError("max_tokens must be an integer between 1 and 1024.")
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens},
    )
    blocks = response["output"]["message"]["content"]
    return {
        "model_id": model_id,
        "text": "\n".join(block["text"] for block in blocks if "text" in block),
        "usage": response.get("usage", {}),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default="eu-north-1")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--model-id", default="amazon.nova-lite-v1:0")
    parser.add_argument("--prompt", default="Explain Amazon Bedrock in two short sentences.")
    parser.add_argument("--max-tokens", type=int, default=128)
    args = parser.parse_args(argv)
    try:
        session = boto3.Session(profile_name=args.profile, region_name=args.region)
        client = session.client(
            "bedrock-runtime",
            config=Config(connect_timeout=10, read_timeout=90,
                          retries={"total_max_attempts": 1}),
        )
        result = run_request(client, args.model_id, args.prompt, args.max_tokens)
    except (BotoCoreError, ClientError, ValueError) as exc:
        print(f"Bedrock request failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"region": args.region, **result}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
