# Mainframe Automation Agent

AI-powered agent that automates any mainframe or desktop application using natural language.

## Architecture

```
mainframe_agent/
├── core/
│   └── agent.py        ← MainframeAgent class (all logic)
├── main.py             ← CLI entry point
├── demo.py             ← Headless demo (no real app needed)
├── requirements.txt
└── output/             ← Generated reports, screenshots
```

## Installation

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

### CLI

```bash
# Discover all functionality
python main.py --app /path/to/app.exe --task discover

# Generate application overview
python main.py --app /path/to/app.exe --task overview

# Generate & run test cases
python main.py --app /path/to/app.exe --task test

# Full HTML report (overview + tests + summary)
python main.py --app /path/to/app.exe --task report

# Run a single natural-language command
python main.py --app /path/to/app.exe --task run \
  --command "Navigate to the account enquiry screen"

# Interactive REPL
python main.py --app /path/to/app.exe --task interactive
```

### Python API

```python
from core.agent import MainframeAgent

agent = MainframeAgent(
    app_path="C:/Apps/mainframe.exe",
    output_dir="output"
)

agent.launch_app()

# Natural-language automation
agent.execute_action("Open the transaction history screen")
agent.execute_action("Search for account number 1234567")
agent.execute_action("Export the results to CSV")

# Analysis tasks
discovery = agent.discover_functionality()
agent.generate_overview()
suites    = agent.generate_test_cases()
results   = agent.run_test_suite(suites)
report    = agent.generate_full_report()  # → output/full_report.html

agent.close_app()
```

## How It Works

1. **Screenshot** — captures current screen via PIL/ImageGrab
2. **Vision AI** — sends screenshot + prompt to Claude (vision model)
3. **Action Plan** — Claude returns JSON plan (click / type / key / wait)
4. **Execution** — pyautogui executes the plan on the real UI
5. **Observation** — re-screenshot + Claude confirms outcome
6. **Repeat** — loop until task is done

## Output Files

| File | Description |
|------|-------------|
| `discovery_report.md/json` | All discovered UI elements & features |
| `app_overview.md` | Full technical documentation |
| `test_cases.md/json` | Generated test suite |
| `test_results.md/json` | Test execution results |
| `full_report.html` | Combined HTML dashboard |
| `screenshot_*.png` | Step-by-step screenshots |

## Notes

- Works on Windows, macOS, and Linux
- Falls back to headless/simulation mode when no display is available
- Requires `ANTHROPIC_API_KEY` environment variable
- Set `pyautogui.PAUSE` to adjust speed (default 0.5s between actions)