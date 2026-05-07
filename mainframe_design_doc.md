# AI-Powered Mainframe Automation Agent (Python)

## Goal

Build an AI agent that can:

* Launch and connect to a desktop-based IBM mainframe terminal emulator
* Understand natural language commands
* Read terminal screens dynamically
* Navigate through the application automatically
* Discover workflows and functionality
* Generate application overviews
* Generate functional documentation
* Generate test cases automatically
* Execute automated test scenarios
* Capture screenshots and logs
* Work with local installed mainframe applications

This implementation is designed for:

* IBM Personal Communications (PCOMM)
* IBM 3270 / 5250 terminal emulators
* HLLAPI / EHLLAPI compatible applications
* Windows desktop environment

---

# High Level Architecture

```text
+---------------------------------------------------+
|              Natural Language Input               |
+--------------------------+------------------------+
                           |
                           v
+---------------------------------------------------+
|                  LLM Planner Agent                |
|  - Understands intent                             |
|  - Creates action plan                            |
|  - Decides next navigation                        |
+--------------------------+------------------------+
                           |
                           v
+---------------------------------------------------+
|               Mainframe Automation SDK            |
|                                                   |
|  - Launch terminal                                |
|  - Connect session                                |
|  - Read screen                                    |
|  - Send keys                                      |
|  - Detect fields                                  |
|  - Navigate menus                                 |
|  - OCR fallback                                   |
+--------------------------+------------------------+
                           |
                           v
+---------------------------------------------------+
|              Discovery + Analysis Engine          |
|                                                   |
|  - Workflow discovery                             |
|  - Screen graph generation                        |
|  - Menu extraction                                |
|  - Field detection                                |
|  - Transition mapping                             |
+--------------------------+------------------------+
                           |
                           v
+---------------------------------------------------+
|                Test Case Generator                |
|                                                   |
|  - Functional test cases                          |
|  - Edge cases                                     |
|  - Negative cases                                 |
|  - Regression suite                               |
+---------------------------------------------------+
```

---

# Mainframe Automation Approaches

There are 3 major ways to automate mainframe desktop applications.

| Method                    | Recommended | Notes                  |
| ------------------------- | ----------- | ---------------------- |
| EHLLAPI / HLLAPI          | YES         | Best and most reliable |
| OCR + Keyboard Automation | Backup      | Slower and less stable |
| Accessibility APIs        | Sometimes   | Depends on emulator    |

For IBM Personal Communications, use:

* EHLLAPI
* WinHLLAPI
* PCSAPI

IBM officially supports EHLLAPI for:

* Screen reading
* Keystroke automation
* Cursor handling
* Session management
* Field extraction
* File transfer

IBM documentation confirms EHLLAPI is intended for automated operator applications and screen automation. ([ibm.com](https://www.ibm.com/docs/en/personal-communications/14.0.0?topic=programming-introduction-emulator-apis&utm_source=chatgpt.com))

---

# Recommended Tech Stack

## Core

```text
Python 3.12+
Windows OS
IBM Personal Communications
OpenAI / Local LLM
FastAPI
SQLite/Postgres
```

## Python Libraries

```bash
pip install pywin32
pip install pyautogui
pip install pillow
pip install pytesseract
pip install openai
pip install fastapi
pip install uvicorn
pip install networkx
pip install pydantic
pip install python-dotenv
pip install loguru
```

Optional:

```bash
pip install langgraph
pip install langchain
pip install instructor
```

---

# Project Structure

```text
mainframe-ai-agent/
│
├── app/
│   ├── agent/
│   │   ├── planner.py
│   │   ├── executor.py
│   │   ├── memory.py
│   │   └── prompts.py
│   │
│   ├── mainframe/
│   │   ├── ehllapi.py
│   │   ├── screen_parser.py
│   │   ├── navigator.py
│   │   ├── session.py
│   │   └── launcher.py
│   │
│   ├── discovery/
│   │   ├── crawler.py
│   │   ├── graph_builder.py
│   │   └── analyzer.py
│   │
│   ├── testing/
│   │   ├── testcase_generator.py
│   │   ├── regression_runner.py
│   │   └── validators.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   └── models/
│
├── data/
├── screenshots/
├── logs/
├── reports/
├── requirements.txt
└── main.py
```

---

# Step 1 — Install IBM Personal Communications

Install:

* IBM Personal Communications
* Enable EHLLAPI support
* Create session profile

Example workspace file:

```text
C:\ProgramData\IBM\Personal Communications\IBMPLEX - IBMESYS.ws
```

Your earlier file:

```text
IBMPLEX - IBMESYS.ws
```

is a workspace/session configuration.

---

# Step 2 — Launch Mainframe Session

## launcher.py

```python
import subprocess
import time
from pathlib import Path


class MainframeLauncher:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path

    def launch(self):
        exe_path = r"C:\Program Files\IBM\Personal Communications\pcsws.exe"

        if not Path(exe_path).exists():
            raise FileNotFoundError("IBM PCOMM not installed")

        subprocess.Popen([
            exe_path,
            self.workspace_path
        ])

        time.sleep(10)

        return True
```

---

# Step 3 — EHLLAPI Wrapper

This is the most important part.

EHLLAPI allows:

* Read screen text
* Send Enter/PF keys
* Set cursor
* Detect fields
* Read status
* Automate navigation

---

# Step 4 — Python EHLLAPI Integration

## ehllapi.py

```python
import ctypes
from ctypes import byref, c_int, create_string_buffer


class EHLLAPI:
    def __init__(self):
        self.dll = ctypes.WinDLL("ehlapi32.dll")

    def hllapi(self, function, data, length, position):
        func = c_int(function)
        length = c_int(length)
        position = c_int(position)

        buffer = create_string_buffer(data.encode())

        self.dll.hllapi(
            byref(func),
            buffer,
            byref(length),
            byref(position)
        )

        return {
            "buffer": buffer.value.decode(errors="ignore"),
            "length": length.value,
            "position": position.value,
        }

    def connect(self, session="A"):
        result = self.hllapi(
            1,
            session,
            len(session),
            0
        )

        return result

    def disconnect(self):
        return self.hllapi(2, "", 0, 0)

    def send_keys(self, text):
        return self.hllapi(
            3,
            text,
            len(text),
            0
        )

    def copy_screen(self):
        length = 1920

        result = self.hllapi(
            5,
            " " * length,
            length,
            0
        )

        return result["buffer"]
```

---

# Step 5 — Read Mainframe Screen

## screen_parser.py

```python
class ScreenParser:
    def parse(self, raw_screen: str):
        rows = []

        for i in range(0, len(raw_screen), 80):
            rows.append(raw_screen[i:i+80])

        return rows

    def extract_menu_options(self, rows):
        options = []

        for row in rows:
            row = row.strip()

            if row.startswith("1"):
                options.append(row)
            elif row.startswith("2"):
                options.append(row)
            elif row.startswith("3"):
                options.append(row)

        return options

    def detect_input_fields(self, rows):
        fields = []

        for row_index, row in enumerate(rows):
            if "_" in row:
                fields.append({
                    "row": row_index,
                    "content": row
                })

        return fields
```

---

# Step 6 — Navigation Engine

## navigator.py

```python
import time


class Navigator:
    def __init__(self, ehllapi, parser):
        self.ehllapi = ehllapi
        self.parser = parser

    def get_screen(self):
        raw = self.ehllapi.copy_screen()
        return self.parser.parse(raw)

    def press_enter(self):
        self.ehllapi.send_keys("@E")
        time.sleep(1)

    def press_pf(self, number):
        self.ehllapi.send_keys(f"@{number}")
        time.sleep(1)

    def type_text(self, text):
        self.ehllapi.send_keys(text)

    def navigate_to_menu(self, option):
        self.type_text(option)
        self.press_enter()
```

---

# Step 7 — AI Planner Agent

The AI planner converts:

```text
"Generate customer report"
```

into:

```text
1. Go to Reports Menu
2. Select Customer Reports
3. Enter customer id
4. Submit
5. Export results
```

---

## planner.py

```python
from openai import OpenAI


SYSTEM_PROMPT = """
You are a mainframe automation AI.

You receive:
- Current screen
- Available options
- User instruction

Return:
- Next best action
- Keys to press
- Data to type
- Navigation logic
"""


class AIPlanner:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def plan(self, screen, instruction):
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"""
Instruction:
{instruction}

Current Screen:
{screen}
"""
                }
            ]
        )

        return response.choices[0].message.content
```

---

# Step 8 — Autonomous Discovery Engine

This crawler automatically explores screens.

It:

* Reads menu options
* Navigates recursively
* Builds screen graph
* Detects workflows
* Generates documentation

---

## crawler.py

```python
import hashlib
import json
import time


class MainframeCrawler:
    def __init__(self, navigator):
        self.navigator = navigator
        self.visited = set()
        self.graph = {}

    def screen_hash(self, rows):
        joined = "\n".join(rows)
        return hashlib.md5(joined.encode()).hexdigest()

    def crawl(self, depth=0, max_depth=5):
        if depth > max_depth:
            return

        rows = self.navigator.get_screen()

        screen_id = self.screen_hash(rows)

        if screen_id in self.visited:
            return

        self.visited.add(screen_id)

        options = []

        for row in rows:
            stripped = row.strip()

            if stripped[:1].isdigit():
                options.append(stripped)

        self.graph[screen_id] = {
            "screen": rows,
            "options": options,
        }

        for option in options:
            try:
                number = option.split()[0]

                self.navigator.navigate_to_menu(number)

                time.sleep(2)

                self.crawl(depth + 1, max_depth)

                self.navigator.press_pf(3)

            except Exception as e:
                print(e)

    def save_graph(self):
        with open("screen_graph.json", "w") as f:
            json.dump(self.graph, f, indent=2)
```

---

# Step 9 — Build Workflow Graph

## graph_builder.py

```python
import networkx as nx


class WorkflowGraphBuilder:
    def build(self, graph_data):
        graph = nx.DiGraph()

        for screen_id, data in graph_data.items():
            graph.add_node(screen_id)

            for option in data["options"]:
                graph.add_edge(screen_id, option)

        return graph
```

---

# Step 10 — Generate Functional Overview

## analyzer.py

```python
from openai import OpenAI


class MainframeAnalyzer:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_overview(self, graph_data):
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": "Analyze this mainframe application"
                },
                {
                    "role": "user",
                    "content": str(graph_data)
                }
            ]
        )

        return response.choices[0].message.content
```

---

# Step 11 — Generate Test Cases

## testcase_generator.py

```python
from openai import OpenAI


class TestCaseGenerator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate(self, workflow):
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": "Generate enterprise QA test cases"
                },
                {
                    "role": "user",
                    "content": workflow
                }
            ]
        )

        return response.choices[0].message.content
```

---

# Example Generated Test Cases

```text
Feature: Customer Search

Test Case 1:
- Login
- Navigate to Customer Menu
- Enter valid customer id
- Verify customer details displayed

Test Case 2:
- Enter invalid customer id
- Verify validation message

Test Case 3:
- Leave field blank
- Verify mandatory validation
```

---

# Step 12 — Natural Language Execution

## executor.py

```python
class AgentExecutor:
    def __init__(self, planner, navigator):
        self.planner = planner
        self.navigator = navigator

    def execute(self, instruction):
        rows = self.navigator.get_screen()

        plan = self.planner.plan(rows, instruction)

        print("PLAN:")
        print(plan)

        # parse structured response
        # execute actions dynamically
```

---

# Step 13 — FastAPI API Server

## main.py

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}
```

---

# Step 14 — Full Orchestrator

## run_agent.py

```python
from app.mainframe.launcher import MainframeLauncher
from app.mainframe.ehllapi import EHLLAPI
from app.mainframe.screen_parser import ScreenParser
from app.mainframe.navigator import Navigator
from app.discovery.crawler import MainframeCrawler
from app.discovery.analyzer import MainframeAnalyzer


WORKSPACE = r"C:\ProgramData\IBM\Personal Communications\IBMPLEX - IBMESYS.ws"


launcher = MainframeLauncher(WORKSPACE)
launcher.launch()


hll = EHLLAPI()
hll.connect("A")


parser = ScreenParser()

navigator = Navigator(hll, parser)

crawler = MainframeCrawler(navigator)

crawler.crawl()

crawler.save_graph()


analyzer = MainframeAnalyzer(api_key="YOUR_KEY")

summary = analyzer.generate_overview(crawler.graph)

print(summary)
```

---

# Natural Language Examples

## Example 1

```text
Discover all functionality in this application
```

## Example 2

```text
Generate test cases for customer workflow
```

## Example 3

```text
Login and generate monthly report
```

## Example 4

```text
Find all data entry forms
```

## Example 5

```text
Document all PF key navigation
```

---

# Advanced Features

## 1. Screen Classification

Use AI to classify:

* Menu screen
* Data entry screen
* Report screen
* Error screen
* Confirmation screen

---

## 2. OCR Fallback

If EHLLAPI unavailable:

```python
import pyautogui
import pytesseract

img = pyautogui.screenshot()
text = pytesseract.image_to_string(img)
```

---

## 3. Screenshot Capture

```python
import pyautogui

pyautogui.screenshot("screen.png")
```

---

## 4. Session Recovery

Automatically:

* reconnect sessions
* detect disconnects
* retry failed steps
* handle timeouts

---

## 5. Multi-Agent Architecture

You can create:

| Agent               | Responsibility      |
| ------------------- | ------------------- |
| Planner Agent       | Planning            |
| Navigation Agent    | Screen movement     |
| Discovery Agent     | Workflow discovery  |
| QA Agent            | Test generation     |
| Documentation Agent | Functional docs     |
| Validator Agent     | Output verification |

---

# Recommended Production Architecture

```text
FastAPI
  |
Redis Queue
  |
Worker Pool
  |
Mainframe Sessions
  |
AI Agents
```

---

# Enterprise Improvements

## Add Structured Output

Use Pydantic:

```python
from pydantic import BaseModel


class Action(BaseModel):
    action: str
    value: str | None = None
```

---

# Build Screen Memory

Store:

* screen hash
* screen title
* navigation path
* field metadata
* workflow mapping

This becomes your:

```text
Mainframe Knowledge Graph
```

---

# AI Prompt Example

```text
You are an enterprise mainframe analyst.

Analyze this screen.

Identify:
- business functionality
- menu options
- navigation paths
- mandatory fields
- validation rules
- workflow purpose
- possible test cases
```

---

# Recommended LLMs

## Best

* GPT-4.1
* GPT-5
* Claude Opus
* Gemini 2.5 Pro

## Local Models

* Qwen 3
* DeepSeek
* Llama 4

---

# Important Mainframe Key Mapping

| Action  | EHLLAPI Key |
| ------- | ----------- |
| Enter   | @E          |
| PF1     | @1          |
| PF2     | @2          |
| PF3     | @3          |
| PF12    | @C          |
| Tab     | @T          |
| Backtab | @B          |
| Clear   | @L          |
| Reset   | @R          |

---

# Real Enterprise Use Cases

## Functional Discovery

Automatically discover:

* all menus
* all workflows
* hidden navigation
* authorization paths
* data entry forms

---

## Test Automation

Generate:

* regression suites
* smoke tests
* edge cases
* validation tests
* integration tests

---

## Migration Analysis

Useful for:

* mainframe modernization
* API migration
* UI modernization
* process mining

---

# Common Challenges

## 1. Dynamic Screens

Solution:

* screen hashing
* fuzzy matching
* OCR fallback

---

## 2. Timing Issues

Use waits:

```python
import time
time.sleep(2)
```

Better:

* wait for keyboard unlock
* wait for host ready

IBM documents synchronization requirements for EHLLAPI automation. ([ibm.com](https://www.ibm.com/docs/en/personal-communications/15.0.0?topic=programming-partial-ehllapi-input-personal-communications-host-screen&utm_source=chatgpt.com))

---

## 3. Session IDs

Typical sessions:

```text
A
B
C
D
```

---

# Security Considerations

Never store:

* passwords
* RACF secrets
* production credentials

Use:

* Windows Credential Manager
* Vault
* Secret Manager

---

# Future Enhancements

## 1. Reinforcement Learning Navigation

Agent learns:

* best navigation path
* workflow optimization
* shortcut discovery

---

## 2. Visual Screen Understanding

Use:

* OCR
* Computer Vision
* LayoutLM
* Vision LLMs

---

## 3. Autonomous QA System

The system can:

* discover app
* generate tests
* execute tests
* validate output
* create reports
* detect regressions

---

# Final Recommended Flow

```text
1. Launch PCOMM
2. Connect EHLLAPI
3. Read current screen
4. Parse menus and fields
5. Ask LLM for next action
6. Execute navigation
7. Capture results
8. Build workflow graph
9. Generate overview
10. Generate test cases
11. Execute regression tests
```

---

# Why EHLLAPI is Best

EHLLAPI is:

* faster than OCR
* reliable
* enterprise standard
* supported by IBM
* supports direct screen access
* supports key automation
* stable for production automation

IBM documentation explicitly describes EHLLAPI as suitable for automated operator applications and host screen automation. ([ibm.com](https://www.ibm.com/docs/en/personal-communications/14.0.0?topic=programming-introduction-emulator-apis&utm_source=chatgpt.com))

---

# Additional Recommendations

## Strongly Recommended

Build:

```text
Screen Semantic Layer
```

Example:

```json
{
  "screen_name": "Customer Search",
  "type": "form",
  "fields": [
    {
      "name": "customer_id",
      "required": true
    }
  ],
  "actions": [
    "search",
    "clear"
  ]
}
```

This becomes extremely powerful for:

* autonomous agents
* workflow reasoning
* test generation
* modernization projects

---

# Recommended Next Step

Your best production implementation path:

## Phase 1

Build:

* launcher
* EHLLAPI wrapper
* screen reader
* navigation engine

## Phase 2

Build:

* workflow crawler
* graph engine
* AI analyzer

## Phase 3

Build:

* autonomous execution
* test generation
* self-healing automation

## Phase 4

Build:

* multi-agent orchestration
* memory system
* enterprise reporting
* regression automation

---

# IBM References

* IBM Personal Communications EHLLAPI APIs
* IBM Emulator APIs
* WinHLLAPI
* PCSAPI

IBM documents describe EHLLAPI, WinHLLAPI, and PCSAPI as supported automation interfaces for emulator interaction. ([ibm.com](https://www.ibm.com/docs/en/personal-communications/14.0.0?topic=programming-introduction-emulator-apis&utm_source=chatgpt.com))
