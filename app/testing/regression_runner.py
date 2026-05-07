from __future__ import annotations

from dataclasses import dataclass

from app.testing.validators import validate_expected_text


@dataclass
class RegressionResult:
    name: str
    passed: bool
    details: str


class RegressionRunner:
    def __init__(self, navigator):
        self.navigator = navigator

    def run(self, scenarios: list[dict[str, str]]) -> list[RegressionResult]:
        results: list[RegressionResult] = []
        for scenario in scenarios:
            name = scenario.get("name", "unnamed")
            expected_text = scenario.get("expected_text", "")
            rows = self.navigator.get_screen()
            passed = validate_expected_text(rows, expected_text)
            details = "Expected text found." if passed else "Expected text missing."
            results.append(RegressionResult(name=name, passed=passed, details=details))
        return results
