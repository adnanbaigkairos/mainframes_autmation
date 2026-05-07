from __future__ import annotations

from app.logging import log
from app.models.actions import ActionType, Plan


class AgentExecutor:
    def __init__(self, planner, navigator, parser):
        self.planner = planner
        self.navigator = navigator
        self.parser = parser

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
        rows = self.navigator.get_screen()
        options = self.parser.extract_menu_options(rows)
        plan = self.planner.plan(rows, options, instruction)
        log.info("Executing plan with {action_count} actions.", action_count=len(plan.actions))
        self._apply_plan(plan)
        return plan
