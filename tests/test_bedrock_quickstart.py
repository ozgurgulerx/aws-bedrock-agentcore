"""Offline contract tests for the first Bedrock Converse request."""

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError, NoCredentialsError

from bedrock_first_request import main, run_request


class RunRequestTests(unittest.TestCase):
    def make_client(self, content=None, usage=None):
        return Mock(
            converse=Mock(
                return_value={
                    "output": {
                        "message": {"content": content or [{"text": "Hello"}]}
                    },
                    "usage": usage or {"inputTokens": 5, "outputTokens": 2},
                }
            )
        )

    def test_sends_bounded_converse_request_and_returns_result(self):
        client = self.make_client()

        result = run_request(client, "amazon.example-v1:0", "Explain Bedrock")

        client.converse.assert_called_once_with(
            modelId="amazon.example-v1:0",
            messages=[
                {"role": "user", "content": [{"text": "Explain Bedrock"}]}
            ],
            inferenceConfig={"maxTokens": 128},
        )
        self.assertEqual(
            result,
            {
                "model_id": "amazon.example-v1:0",
                "text": "Hello",
                "usage": {"inputTokens": 5, "outputTokens": 2},
            },
        )

    def test_joins_text_blocks_and_ignores_nontext_content(self):
        usage = {"inputTokens": 12, "outputTokens": 4, "totalTokens": 16}
        client = self.make_client(
            content=[
                {"text": "First paragraph"},
                {"toolUse": {"name": "example", "input": {}}},
                {"text": "Second paragraph"},
            ],
            usage=usage,
        )

        result = run_request(client, "model", "prompt", max_tokens=64)

        self.assertEqual(result["text"], "First paragraph\nSecond paragraph")
        self.assertEqual(result["usage"], usage)
        self.assertEqual(
            client.converse.call_args.kwargs["inferenceConfig"],
            {"maxTokens": 64},
        )

    def test_rejects_blank_model_or_prompt_before_calling_service(self):
        for model_id, prompt in [("", "prompt"), ("  ", "prompt"),
                                 ("model", ""), ("model", " \n ")]:
            with self.subTest(model_id=model_id, prompt=prompt):
                client = self.make_client()
                with self.assertRaises(ValueError):
                    run_request(client, model_id, prompt)
                client.converse.assert_not_called()

    def test_rejects_out_of_range_token_limits_before_calling_service(self):
        for max_tokens in (-1, 0, 1025):
            with self.subTest(max_tokens=max_tokens):
                client = self.make_client()
                with self.assertRaises(ValueError):
                    run_request(client, "model", "prompt", max_tokens=max_tokens)
                client.converse.assert_not_called()

    def test_accepts_token_limit_boundaries(self):
        for max_tokens in (1, 1024):
            with self.subTest(max_tokens=max_tokens):
                client = self.make_client()
                run_request(client, "model", "prompt", max_tokens=max_tokens)
                self.assertEqual(
                    client.converse.call_args.kwargs["inferenceConfig"],
                    {"maxTokens": max_tokens},
                )

    def test_propagates_service_failure_to_cli(self):
        failure = RuntimeError("Service unavailable")
        client = Mock(converse=Mock(side_effect=failure))

        with self.assertRaises(RuntimeError) as raised:
            run_request(client, "model", "prompt")

        self.assertIs(raised.exception, failure)
        client.converse.assert_called_once()


class CommandLineTests(unittest.TestCase):
    @patch("bedrock_first_request.boto3.Session")
    def test_forwards_arguments_and_prints_json(self, session_factory):
        client = session_factory.return_value.client.return_value
        client.converse.return_value = {
            "output": {"message": {"content": [{"text": "Bedrock answer"}]}},
            "usage": {"inputTokens": 4, "outputTokens": 3},
        }
        output = io.StringIO()

        with redirect_stdout(output):
            status = main([
                "--profile", "demo", "--region", "eu-west-1",
                "--model-id", "custom-model", "--prompt", "Custom prompt",
                "--max-tokens", "64",
            ])

        self.assertEqual(status, 0)
        session_factory.assert_called_once_with(
            profile_name="demo", region_name="eu-west-1"
        )
        session_factory.return_value.client.assert_called_once()
        client_args = session_factory.return_value.client.call_args
        self.assertEqual(client_args.args, ("bedrock-runtime",))
        self.assertEqual(client_args.kwargs["config"].retries,
                         {"total_max_attempts": 1})
        self.assertEqual(client.converse.call_args.kwargs["modelId"], "custom-model")
        self.assertEqual(client.converse.call_args.kwargs["messages"], [
            {"role": "user", "content": [{"text": "Custom prompt"}]}
        ])
        self.assertEqual(client.converse.call_args.kwargs["inferenceConfig"],
                         {"maxTokens": 64})
        self.assertEqual(json.loads(output.getvalue()), {
            "region": "eu-west-1", "model_id": "custom-model",
            "text": "Bedrock answer", "usage": {"inputTokens": 4, "outputTokens": 3},
        })

    @patch("bedrock_first_request.boto3.Session")
    def test_reports_aws_service_error_without_success_output(self, session_factory):
        session_factory.return_value.client.return_value.converse.side_effect = ClientError(
            {"Error": {"Code": "AccessDeniedException", "Message": "Not authorized"}},
            "Converse",
        )
        output, errors = io.StringIO(), io.StringIO()

        with redirect_stdout(output), redirect_stderr(errors):
            status = main([])

        self.assertEqual(status, 1)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("Bedrock request failed:", errors.getvalue())
        self.assertIn("AccessDeniedException", errors.getvalue())
        self.assertNotIn("Traceback", errors.getvalue())

    @patch("bedrock_first_request.boto3.Session")
    def test_reports_missing_credentials(self, session_factory):
        session_factory.side_effect = NoCredentialsError()
        errors = io.StringIO()

        with redirect_stderr(errors):
            status = main([])

        self.assertEqual(status, 1)
        self.assertIn("Unable to locate credentials", errors.getvalue())

    @patch("bedrock_first_request.boto3.Session")
    def test_invalid_request_never_reaches_aws(self, session_factory):
        errors = io.StringIO()

        with redirect_stderr(errors):
            status = main(["--max-tokens", "1025"])

        self.assertEqual(status, 1)
        session_factory.return_value.client.return_value.converse.assert_not_called()
        self.assertIn("between 1 and 1024", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
