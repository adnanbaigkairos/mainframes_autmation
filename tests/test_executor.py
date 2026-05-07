from app.agent.executor import AgentExecutor
from app.models.actions import Action, ActionType, Plan


class FakePlanner:
    def plan(self, screen_rows, options, instruction):
        _ = (screen_rows, options, instruction)
        return Plan(actions=[Action(action=ActionType.PRESS_ENTER)])


class FakeParser:
    def extract_menu_options(self, rows):
        _ = rows
        return []


class FakeNavigator:
    def __init__(self, screens):
        self.screens = screens
        self.index = 0
        self.wait_calls = 0
        self.enter_calls = 0

    def get_screen(self):
        screen = self.screens[min(self.index, len(self.screens) - 1)]
        self.index += 1
        return screen

    def wait_for_host(self):
        self.wait_calls += 1

    def press_enter(self):
        self.enter_calls += 1


def test_executor_retries_blank_screen_before_success():
    navigator = FakeNavigator(
        screens=[
            [" " * 80 for _ in range(2)],
            ["Main Menu", "1 Search"],
        ]
    )
    executor = AgentExecutor(FakePlanner(), navigator, FakeParser(), blank_screen_retries=2)
    plan = executor.execute("open search")
    assert plan.actions[0].action == ActionType.PRESS_ENTER
    assert navigator.wait_calls == 1
    assert navigator.enter_calls == 1


def test_executor_raises_on_persistent_blank_screen():
    navigator = FakeNavigator(screens=[[" " * 80], [" " * 80], [" " * 80]])
    executor = AgentExecutor(FakePlanner(), navigator, FakeParser(), blank_screen_retries=2)
    try:
        executor.execute("anything")
        assert False, "Expected RuntimeError for blank screen."
    except RuntimeError as exc:
        assert "blank" in str(exc).lower()
