from __future__ import annotations

import json

from openai import OpenAI


class TestCaseGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate(self, workflow: dict[str, object] | str) -> str:
        if self.client is None:
            return self._local_generate(workflow)

        content = workflow if isinstance(workflow, str) else json.dumps(workflow)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Generate enterprise QA test cases from this workflow."},
                {"role": "user", "content": content},
            ],
        )
        return response.choices[0].message.content or ""

    @staticmethod
    def _local_generate(workflow: dict[str, object] | str) -> str:
        workflow_text = workflow if isinstance(workflow, str) else json.dumps(workflow)
        return (
            "Feature: Mainframe Workflow\n\n"
            "Test Case 1: Happy path navigation\n"
            "- Open menu\n"
            "- Select valid option\n"
            "- Verify expected output\n\n"
            "Test Case 2: Invalid input validation\n"
            "- Enter invalid value\n"
            "- Verify validation or error response\n\n"
            f"Workflow Source: {workflow_text[:200]}"
        )
