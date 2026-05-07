from __future__ import annotations

from app.logging import log
from app.models.actions import ActionType, Plan


class AgentExecutor:
    def __init__(self, planner, navigator, parser, blank_screen_retries: int = 3):
        self.planner = planner
        self.navigator = navigator
        self.parser = parser
        self.blank_screen_retries = max(0, blank_screen_retries)

    @staticmethod
    def _has_visible_content(rows: list[str]) -> bool:
        return any(row.strip() for row in rows)

    def _get_non_blank_screen(self) -> list[str]:
        for attempt in range(self.blank_screen_retries + 1):
            rows = self.navigator.get_screen()
            if self._has_visible_content(rows):
                return rows
            if attempt < self.blank_screen_retries:
                log.warning(
                    "Blank screen detected; waiting before retry {attempt}.",
                    attempt=attempt + 1,
                )
                self.navigator.wait_for_host()

        raise RuntimeError(
            "Mainframe screen is blank after retries. Verify active host session, "
            "session ID, and EHLLAPI connection."
        )

    def _apply_plan(self, plan: Plan) -> None:
        for action in plan.actions:
            if action.action == ActionType.TYPE and action.value is not None:
                self.navigator.type_text(action.value)
            elif action.action == ActionType.PRESS_ENTER:
                self.navigator.press_enter()
            elif action.action == ActionType.PRESS_PF and action.value is not None:
                self.navigator.press_pf(int(action.value))
            elif action.action == ActionType.NAVIGATE_MENU and action.value is not None:
                self.navigator.navigate_to_menu(action.value)
            elif action.action == ActionType.WAIT:
                self.navigator.wait_for_host()

    def execute(self, instruction: str) -> Plan:
        rows = self._get_non_blank_screen()
        options = self.parser.extract_menu_options(rows)
        plan = self.planner.plan(rows, options, instruction)
        log.info("Executing plan with {action_count} actions.", action_count=len(plan.actions))
        self._apply_plan(plan)
        return plan
