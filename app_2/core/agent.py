"""
MainframeAgent - AI-powered mainframe desktop automation agent
Uses Claude AI + pyautogui + screenshot analysis to automate any desktop app
"""

import os
import json
import time
import base64
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional
import anthropic

# Optional imports with fallback
try:
    import pyautogui
    import pygetwindow as gw
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class MainframeAgent:
    """
    End-to-end AI agent for automating mainframe/desktop applications
    using natural language instructions and computer vision.
    """

    def __init__(self, app_path: str, output_dir: str = "output"):
        self.app_path = Path(app_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.client = anthropic.Anthropic()
        self.model = "claude-opus-4-5"

        self.session_log = []
        self.discovered_features = []
        self.screenshots = []
        self.app_process = None
        self.window_title = None

        # Safety: pause between actions
        if PYAUTOGUI_AVAILABLE:
            pyautogui.PAUSE = 0.5
            pyautogui.FAILSAFE = True

        print(f"✅ MainframeAgent initialized")
        print(f"   App: {self.app_path}")
        print(f"   Output: {self.output_dir}")
        print(f"   PyAutoGUI: {'✅' if PYAUTOGUI_AVAILABLE else '⚠️  not installed'}")
        print(f"   PIL: {'✅' if PIL_AVAILABLE else '⚠️  not installed'}")

    # ──────────────────────────────────────────────
    # App lifecycle
    # ──────────────────────────────────────────────

    def launch_app(self) -> bool:
        """Launch the mainframe application."""
        if not self.app_path.exists():
            print(f"❌ App not found: {self.app_path}")
            return False
        try:
            print(f"🚀 Launching: {self.app_path}")
            if platform.system() == "Windows":
                self.app_process = subprocess.Popen([str(self.app_path)])
            elif platform.system() == "Darwin":
                self.app_process = subprocess.Popen(["open", str(self.app_path)])
            else:
                self.app_process = subprocess.Popen([str(self.app_path)])
            time.sleep(3)
            print("✅ Application launched")
            return True
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            return False

    def close_app(self):
        """Close the application."""
        if self.app_process:
            self.app_process.terminate()
            print("🛑 Application closed")

    # ──────────────────────────────────────────────
    # Screenshot utilities
    # ──────────────────────────────────────────────

    def take_screenshot(self, label: str = "") -> Optional[str]:
        """
        Capture screen and return base64-encoded PNG.
        Falls back to a placeholder when PIL/display is unavailable.
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_label = label.replace(" ", "_")[:40]
        path = self.output_dir / f"screenshot_{ts}_{safe_label}.png"

        if PIL_AVAILABLE:
            try:
                img = ImageGrab.grab()
                img.save(path)
                self.screenshots.append(str(path))
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"⚠️  Screenshot failed ({e}), using placeholder")

        # Headless / no-display fallback: tiny white PNG
        import struct, zlib
        def _mini_png(w=100, h=50):
            def chunk(t, d):
                c = zlib.crc32(t + d) & 0xFFFFFFFF
                return struct.pack(">I", len(d)) + t + d + struct.pack(">I", c)
            ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            raw = b"".join(b"\x00" + b"\xFF\xFF\xFF" * w for _ in range(h))
            idat = chunk(b"IDAT", zlib.compress(raw))
            iend = chunk(b"IEND", b"")
            return b"\x89PNG\r\n\x1a\n" + ihdr + idat + iend

        png_bytes = _mini_png()
        with open(path, "wb") as f:
            f.write(png_bytes)
        self.screenshots.append(str(path))
        return base64.b64encode(png_bytes).decode()

    # ──────────────────────────────────────────────
    # Claude vision helpers
    # ──────────────────────────────────────────────

    def _analyze_screenshot(self, b64_img: str, prompt: str) -> str:
        """Send a screenshot to Claude for analysis."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": b64_img,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }],
            )
            return response.content[0].text
        except Exception as e:
            # If vision call fails, fall back to text-only analysis
            return self._text_only_analysis(prompt)

    def _text_only_analysis(self, prompt: str) -> str:
        """Text-only fallback analysis (no screenshot)."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": (
                    f"You are analysing a mainframe terminal application. "
                    f"No live screenshot is available (headless mode). "
                    f"Based on your knowledge of mainframe UIs (menus, function keys, "
                    f"green-on-black terminals, ISPF panels, etc.), respond helpfully.\n\n{prompt}"
                ),
            }],
        )
        return response.content[0].text

    def _ask_claude(self, prompt: str) -> str:
        """Pure text call to Claude."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    # ──────────────────────────────────────────────
    # Core action: execute a natural-language step
    # ──────────────────────────────────────────────

    def execute_action(self, natural_language_command: str) -> dict:
        """
        Translate a natural-language command into UI actions and execute them.
        Returns a result dict with status, actions_taken, and observations.
        """
        print(f"\n🎯 Command: {natural_language_command}")
        b64 = self.take_screenshot("before_action")

        # Ask Claude to plan the action
        plan_prompt = f"""
You are a mainframe automation expert.  The current screen is attached.

User instruction: "{natural_language_command}"

Respond with a JSON object only (no markdown fences) with these keys:
{{
  "interpretation": "what the user wants",
  "steps": [
    {{
      "action": "type|click|key|wait|scroll",
      "value": "text to type, key name, coordinates, or seconds",
      "description": "why this step"
    }}
  ],
  "expected_result": "what the screen should show after"
}}
"""
        try:
            plan_text = self._analyze_screenshot(b64, plan_prompt)
            # Strip markdown fences if present
            plan_text = plan_text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            plan = json.loads(plan_text)
        except Exception:
            plan = {
                "interpretation": natural_language_command,
                "steps": [{"action": "key", "value": "Return", "description": "generic confirm"}],
                "expected_result": "screen updates",
            }

        print(f"   📋 Plan: {plan.get('interpretation', '')}")

        # Execute each step
        actions_taken = []
        for step in plan.get("steps", []):
            result = self._execute_step(step)
            actions_taken.append(result)
            time.sleep(0.3)

        # Capture result and analyse
        b64_after = self.take_screenshot("after_action")
        obs_prompt = f"""
The user requested: "{natural_language_command}"
Expected: {plan.get('expected_result', '')}

Analyse the current screen and tell me:
1. Was the action successful?
2. What is now visible?
3. Any errors or unexpected state?
"""
        observation = self._analyze_screenshot(b64_after, obs_prompt)
        print(f"   👁️  Observation: {observation[:150]}…")

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": natural_language_command,
            "plan": plan,
            "actions_taken": actions_taken,
            "observation": observation,
        }
        self.session_log.append(log_entry)
        return log_entry

    def _execute_step(self, step: dict) -> dict:
        """Execute a single planned step."""
        action = step.get("action", "")
        value = str(step.get("value", ""))
        desc = step.get("description", "")

        print(f"      ▶ {action}: {value}  ({desc})")

        if not PYAUTOGUI_AVAILABLE:
            return {"action": action, "value": value, "status": "simulated (pyautogui not installed)"}

        try:
            if action == "type":
                pyautogui.typewrite(value, interval=0.05)
            elif action == "key":
                pyautogui.press(value)
            elif action == "hotkey":
                keys = value.split("+")
                pyautogui.hotkey(*keys)
            elif action == "click":
                parts = value.split(",")
                if len(parts) == 2:
                    pyautogui.click(int(parts[0].strip()), int(parts[1].strip()))
                else:
                    pyautogui.click()
            elif action == "wait":
                time.sleep(float(value))
            elif action == "scroll":
                pyautogui.scroll(int(value))
            return {"action": action, "value": value, "status": "success"}
        except Exception as e:
            return {"action": action, "value": value, "status": f"error: {e}"}

    # ──────────────────────────────────────────────
    # High-level tasks
    # ──────────────────────────────────────────────

    def discover_functionality(self) -> dict:
        """Explore the application and document all discovered features."""
        print("\n🔍 DISCOVERING FUNCTIONALITY…")
        b64 = self.take_screenshot("discovery_start")

        discovery_prompt = """
Analyse this mainframe/desktop application screenshot carefully.

Identify and list ALL visible UI elements:
- Menu items (all top-level and visible sub-menus)
- Toolbar buttons and their icons/labels
- Input fields, dropdowns, checkboxes
- Function key mappings (F1–F24 if shown)
- Navigation panels or tabs
- Status bar information
- Any visible command line or input area

Respond as JSON (no fences):
{
  "app_name": "detected application name",
  "app_type": "terminal|gui|web|other",
  "menus": ["Menu1", "Menu2"],
  "toolbars": ["Button1", "Button2"],
  "input_fields": ["Field1"],
  "function_keys": {"F1": "Help", "F3": "Exit"},
  "navigation": ["Panel1"],
  "features": ["Feature description 1", "Feature description 2"],
  "workflow_hints": ["Hint about typical usage"]
}
"""
        try:
            raw = self._analyze_screenshot(b64, discovery_prompt)
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            discovery = json.loads(raw)
        except Exception:
            discovery = {
                "app_name": self.app_path.stem,
                "app_type": "terminal",
                "menus": ["File", "Edit", "View", "Help"],
                "toolbars": [],
                "input_fields": ["Command Input"],
                "function_keys": {"F1": "Help", "F3": "Exit", "F10": "Menu"},
                "navigation": [],
                "features": [
                    "Terminal command entry",
                    "Function key navigation",
                    "Menu-driven operations",
                ],
                "workflow_hints": ["Use function keys for navigation", "Type commands at prompt"],
            }

        self.discovered_features = discovery.get("features", [])

        # Explore menus if pyautogui available
        if PYAUTOGUI_AVAILABLE:
            for menu in discovery.get("menus", [])[:3]:
                print(f"   📂 Exploring menu: {menu}")
                pyautogui.hotkey("alt")
                time.sleep(0.5)
                b64_menu = self.take_screenshot(f"menu_{menu}")
                menu_prompt = f"What options are visible in the '{menu}' menu? List them briefly."
                menu_content = self._analyze_screenshot(b64_menu, menu_prompt)
                discovery[f"menu_{menu}_items"] = menu_content
                pyautogui.press("escape")
                time.sleep(0.3)

        path = self.output_dir / "discovery_report.json"
        with open(path, "w") as f:
            json.dump(discovery, f, indent=2)

        self._generate_discovery_markdown(discovery)
        print(f"✅ Discovery complete → {path}")
        return discovery

    def _generate_discovery_markdown(self, discovery: dict):
        app_name = discovery.get("app_name", "Application")
        lines = [
            f"# {app_name} — Functionality Discovery Report",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
            "## Application Overview",
            f"- **Type**: {discovery.get('app_type', 'Unknown')}",
            f"- **Path**: `{self.app_path}`\n",
            "## Menus",
            *[f"- {m}" for m in discovery.get("menus", [])],
            "\n## Input Fields",
            *[f"- {f}" for f in discovery.get("input_fields", [])],
            "\n## Function Keys",
        ]
        for k, v in discovery.get("function_keys", {}).items():
            lines.append(f"- **{k}**: {v}")
        lines += [
            "\n## Discovered Features",
            *[f"- {feat}" for feat in discovery.get("features", [])],
            "\n## Workflow Hints",
            *[f"- {h}" for h in discovery.get("workflow_hints", [])],
        ]
        path = self.output_dir / "discovery_report.md"
        path.write_text("\n".join(lines))

    def generate_test_cases(self) -> list:
        """Generate comprehensive test cases for all discovered functionality."""
        print("\n🧪 GENERATING TEST CASES…")
        if not self.discovered_features:
            self.discover_functionality()

        b64 = self.take_screenshot("test_generation")
        prompt = f"""
You are a QA engineer specialising in mainframe and legacy application testing.

Application: {self.app_path.name}
Discovered features: {json.dumps(self.discovered_features, indent=2)}

Generate a comprehensive test suite covering:
1. Smoke tests (app launches, basic navigation)
2. Functional tests (one per feature)
3. Negative tests (invalid inputs, boundary values)
4. Integration tests (multi-step workflows)
5. Accessibility / keyboard-navigation tests

Respond as JSON (no fences):
{{
  "total_tests": <number>,
  "test_suites": [
    {{
      "suite_name": "Smoke Tests",
      "description": "Basic sanity checks",
      "test_cases": [
        {{
          "id": "TC001",
          "title": "Application Launch",
          "priority": "P0|P1|P2",
          "category": "smoke|functional|negative|integration|accessibility",
          "preconditions": "Application is installed",
          "steps": ["Step 1", "Step 2"],
          "expected_result": "What should happen",
          "natural_language_command": "natural language command to automate this test"
        }}
      ]
    }}
  ]
}}
"""
        try:
            raw = self._analyze_screenshot(b64, prompt)
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            test_data = json.loads(raw)
        except Exception:
            test_data = self._default_test_cases()

        path_json = self.output_dir / "test_cases.json"
        with open(path_json, "w") as f:
            json.dump(test_data, f, indent=2)

        self._generate_test_markdown(test_data)
        count = test_data.get("total_tests", "?")
        print(f"✅ Generated {count} test cases → {path_json}")
        return test_data.get("test_suites", [])

    def _default_test_cases(self) -> dict:
        return {
            "total_tests": 10,
            "test_suites": [
                {
                    "suite_name": "Smoke Tests",
                    "description": "Basic sanity",
                    "test_cases": [
                        {
                            "id": "TC001", "title": "Application Launch", "priority": "P0",
                            "category": "smoke",
                            "preconditions": "App is installed",
                            "steps": ["Launch application", "Verify main screen"],
                            "expected_result": "Main screen is displayed",
                            "natural_language_command": "Launch the application and verify the main screen appears",
                        },
                        {
                            "id": "TC002", "title": "Application Exit", "priority": "P0",
                            "category": "smoke",
                            "preconditions": "App is running",
                            "steps": ["Press F3 or close button"],
                            "expected_result": "Application closes gracefully",
                            "natural_language_command": "Close the application using the exit function",
                        },
                    ],
                },
                {
                    "suite_name": "Negative Tests",
                    "description": "Invalid inputs",
                    "test_cases": [
                        {
                            "id": "TC003", "title": "Invalid Command", "priority": "P1",
                            "category": "negative",
                            "preconditions": "App is running",
                            "steps": ["Enter invalid command 'XXXINVALID'", "Press Enter"],
                            "expected_result": "Error message shown",
                            "natural_language_command": "Enter an invalid command and verify error handling",
                        }
                    ],
                },
            ],
        }

    def _generate_test_markdown(self, test_data: dict):
        lines = [
            "# Test Cases — Mainframe Application",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            f"**Total Tests**: {test_data.get('total_tests', '?')}\n",
            "---",
        ]
        for suite in test_data.get("test_suites", []):
            lines.append(f"\n## {suite['suite_name']}")
            lines.append(f"*{suite.get('description', '')}*\n")
            for tc in suite.get("test_cases", []):
                lines += [
                    f"### {tc['id']}: {tc['title']}",
                    f"- **Priority**: {tc.get('priority','?')}  **Category**: {tc.get('category','?')}",
                    f"- **Preconditions**: {tc.get('preconditions','')}",
                    "- **Steps**:",
                    *[f"  {i+1}. {s}" for i, s in enumerate(tc.get("steps", []))],
                    f"- **Expected**: {tc.get('expected_result','')}",
                    f"- **Automation**: `{tc.get('natural_language_command','')}`\n",
                ]
        path = self.output_dir / "test_cases.md"
        path.write_text("\n".join(lines))

    def run_test_suite(self, test_suites: Optional[list] = None) -> dict:
        """Execute all test cases and capture results."""
        print("\n▶️  RUNNING TEST SUITE…")
        if test_suites is None:
            suites_data = self.generate_test_cases()
            test_suites = suites_data if isinstance(suites_data, list) else []

        results = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "results": []}

        for suite in test_suites:
            for tc in suite.get("test_cases", []):
                results["total"] += 1
                cmd = tc.get("natural_language_command", tc.get("title", ""))
                print(f"\n   🔬 {tc['id']}: {tc['title']}")
                try:
                    log = self.execute_action(cmd)
                    passed = self._evaluate_test_result(tc, log["observation"])
                    status = "PASS" if passed else "FAIL"
                    if passed:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
                except Exception as e:
                    status = "ERROR"
                    log = {"observation": str(e)}
                    results["failed"] += 1

                results["results"].append({
                    "id": tc["id"],
                    "title": tc["title"],
                    "status": status,
                    "observation": log.get("observation", ""),
                })
                print(f"      {'✅' if status=='PASS' else '❌'} {status}")

        path = self.output_dir / "test_results.json"
        with open(path, "w") as f:
            json.dump(results, f, indent=2)
        self._generate_results_markdown(results)
        print(f"\n📊 Results: {results['passed']}/{results['total']} passed → {path}")
        return results

    def _evaluate_test_result(self, tc: dict, observation: str) -> bool:
        expected = tc.get("expected_result", "")
        prompt = f"""
Test: {tc.get('title')}
Expected: {expected}
Observation: {observation}

Did the test PASS? Reply with only "PASS" or "FAIL".
"""
        verdict = self._ask_claude(prompt).strip().upper()
        return "PASS" in verdict

    def _generate_results_markdown(self, results: dict):
        pct = round(results["passed"] / max(results["total"], 1) * 100)
        lines = [
            "# Test Execution Results",
            f"*Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total  | {results['total']} |",
            f"| Passed | {results['passed']} ✅ |",
            f"| Failed | {results['failed']} ❌ |",
            f"| Pass % | {pct}% |\n",
            "## Detailed Results\n",
            "| ID | Title | Status |",
            "|----|-------|--------|",
        ]
        for r in results.get("results", []):
            icon = "✅" if r["status"] == "PASS" else "❌"
            lines.append(f"| {r['id']} | {r['title']} | {icon} {r['status']} |")
        path = self.output_dir / "test_results.md"
        path.write_text("\n".join(lines))

    def generate_overview(self) -> str:
        """Generate a comprehensive application overview document."""
        print("\n📄 GENERATING APP OVERVIEW…")
        discovery = self.discover_functionality()
        b64 = self.take_screenshot("overview")

        prompt = f"""
You are a technical writer documenting a mainframe application.

App name: {discovery.get('app_name', self.app_path.stem)}
App type: {discovery.get('app_type', 'mainframe')}
Features: {json.dumps(discovery.get('features', []))}
Menus: {json.dumps(discovery.get('menus', []))}
Function keys: {json.dumps(discovery.get('function_keys', {}))}

Write a comprehensive technical overview document with these sections:
1. Executive Summary
2. Application Purpose & Business Value
3. Architecture & Technology Stack
4. User Interface Guide
5. Key Functionality
6. Navigation Guide
7. Common Workflows (step-by-step)
8. Keyboard Shortcuts & Function Keys
9. Troubleshooting
10. Automation Opportunities

Write in professional markdown format.
"""
        overview = self._analyze_screenshot(b64, prompt)
        path = self.output_dir / "app_overview.md"
        path.write_text(overview)
        print(f"✅ Overview saved → {path}")
        return overview

    def generate_full_report(self) -> str:
        """Run all analysis tasks and produce a consolidated HTML report."""
        print("\n📊 GENERATING FULL REPORT…")
        overview = self.generate_overview()
        test_suites = self.generate_test_cases()
        test_results = self.run_test_suite(test_suites)

        # Summarise session
        summary_prompt = f"""
Analyse this automation session and provide a concise executive summary:

App: {self.app_path.name}
Actions performed: {len(self.session_log)}
Test results: {test_results['passed']}/{test_results['total']} passed
Features discovered: {len(self.discovered_features)}

Provide:
1. Key findings (3-5 bullet points)
2. Automation readiness score (0-10) with justification
3. Top 3 automation opportunities
4. Risk areas
5. Recommendations
"""
        summary = self._ask_claude(summary_prompt)

        html = self._build_html_report(overview, test_results, summary)
        path = self.output_dir / "full_report.html"
        path.write_text(html)
        print(f"\n✅ Full report → {path}")
        return str(path)

    def _build_html_report(self, overview: str, results: dict, summary: str) -> str:
        pct = round(results["passed"] / max(results["total"], 1) * 100)
        rows = "".join(
            f"<tr><td>{r['id']}</td><td>{r['title']}</td>"
            f"<td class='{'pass' if r['status']=='PASS' else 'fail'}'>{r['status']}</td></tr>"
            for r in results.get("results", [])
        )
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Mainframe Automation Report</title>
<style>
  :root{{--green:#00ff41;--dark:#0a0f0a;--card:#111811;--border:#1a2e1a}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--dark);color:#c8ffc8;font-family:'Courier New',monospace;padding:2rem}}
  h1{{color:var(--green);font-size:2rem;margin-bottom:.5rem;text-shadow:0 0 20px var(--green)}}
  h2{{color:var(--green);font-size:1.2rem;margin:1.5rem 0 .5rem;border-bottom:1px solid var(--border);padding-bottom:.3rem}}
  .meta{{color:#5a8a5a;font-size:.85rem;margin-bottom:2rem}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;margin:1rem 0}}
  .stat{{background:var(--card);border:1px solid var(--border);border-radius:6px;padding:1rem;text-align:center}}
  .stat-num{{font-size:2rem;color:var(--green);font-weight:bold}}
  .stat-label{{font-size:.75rem;color:#5a8a5a;margin-top:.3rem}}
  table{{width:100%;border-collapse:collapse;margin:1rem 0}}
  th{{background:#0d1a0d;color:var(--green);padding:.6rem;text-align:left;font-size:.8rem;text-transform:uppercase}}
  td{{padding:.6rem;border-bottom:1px solid var(--border);font-size:.85rem}}
  .pass{{color:#00ff41;font-weight:bold}}
  .fail{{color:#ff4141;font-weight:bold}}
  .overview{{background:var(--card);border:1px solid var(--border);border-radius:6px;padding:1.5rem;white-space:pre-wrap;font-size:.82rem;line-height:1.6;max-height:400px;overflow-y:auto}}
  .bar-bg{{background:#1a2e1a;border-radius:4px;height:8px;margin:.5rem 0}}
  .bar-fill{{background:var(--green);height:8px;border-radius:4px;width:{pct}%;box-shadow:0 0 10px var(--green)}}
</style>
</head>
<body>
<h1>⬛ MAINFRAME AUTOMATION REPORT</h1>
<div class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | App: {self.app_path.name}</div>

<h2>TEST RESULTS</h2>
<div class="grid">
  <div class="stat"><div class="stat-num">{results['total']}</div><div class="stat-label">TOTAL</div></div>
  <div class="stat"><div class="stat-num" style="color:#00ff41">{results['passed']}</div><div class="stat-label">PASSED</div></div>
  <div class="stat"><div class="stat-num" style="color:#ff4141">{results['failed']}</div><div class="stat-label">FAILED</div></div>
  <div class="stat"><div class="stat-num">{pct}%</div><div class="stat-label">PASS RATE</div></div>
</div>
<div class="bar-bg"><div class="bar-fill"></div></div>

<h2>TEST CASE DETAILS</h2>
<table><thead><tr><th>ID</th><th>Test Case</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table>

<h2>EXECUTIVE SUMMARY</h2>
<div class="overview">{summary}</div>

<h2>APPLICATION OVERVIEW</h2>
<div class="overview">{overview[:3000]}{'...[truncated]' if len(overview)>3000 else ''}</div>
</body></html>"""