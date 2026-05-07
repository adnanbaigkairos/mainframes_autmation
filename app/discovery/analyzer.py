from __future__ import annotations

import json

from openai import OpenAI


class MainframeAnalyzer:
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate_overview(self, graph_data: dict[str, dict[str, object]]) -> str:
        if self.client is None:
            return self._local_overview(graph_data)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Analyze this mainframe application graph and summarize workflows."},
                {"role": "user", "content": json.dumps(graph_data)},
            ],
        )
        return response.choices[0].message.content or ""

    @staticmethod
    def _local_overview(graph_data: dict[str, dict[str, object]]) -> str:
        screen_count = len(graph_data)
        option_count = sum(len(data.get("options", [])) for data in graph_data.values())
        return (
            "Mainframe discovery completed.\n"
            f"- Discovered screens: {screen_count}\n"
            f"- Discovered menu options: {option_count}\n"
        )
