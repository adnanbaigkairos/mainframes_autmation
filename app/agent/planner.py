from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.logging import log
from app.agent.prompts import SYSTEM_PROMPT
from app.models.actions import Action, ActionType, Plan


class AIPlanner:
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key) if api_key else None

    def _heuristic_plan(self, options: list[str], instruction: str) -> Plan:
        lower_instruction = instruction.lower()
        for option in options:
            token = option.split(maxsplit=1)[0]
            if token.isdigit() and any(word in option.lower() for word in lower_instruction.split()):
                return Plan(
                    reasoning="Heuristic matching found a likely menu option.",
                    actions=[Action(action=ActionType.NAVIGATE_MENU, value=token)],
                )

        return Plan(
            reasoning="No confident menu match; defaulting to Enter for screen progression.",
            actions=[Action(action=ActionType.PRESS_ENTER)],
        )

    @staticmethod
    def _parse_response(content: str) -> Plan:
        payload: dict[str, Any] = json.loads(content)
        actions = [Action(**raw_action) for raw_action in payload.get("actions", [])]
        reasoning = str(payload.get("reasoning", ""))
        return Plan(reasoning=reasoning, actions=actions)

    def plan(self, screen_rows: list[str], options: list[str], instruction: str) -> Plan:
        if self.client is None:
            return self._heuristic_plan(options, instruction)

        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "instruction": instruction,
                            "screen_rows": screen_rows,
                            "options": options,
                        }
                    ),
                },
            ],
        )

        content = response.choices[0].message.content or "{}"

        try:
            return self._parse_response(content)
        except Exception:
            log.warning("Planner response parsing failed; fallback to heuristic.")
            return self._heuristic_plan(options, instruction)
