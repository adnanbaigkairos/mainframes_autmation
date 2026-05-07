#!/usr/bin/env python3
"""
demo.py — Run the MainframeAgent without a real app.
Demonstrates all features using simulated/headless mode.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core.agent import MainframeAgent


def main():
    print("=" * 60)
    print("  MAINFRAME AGENT — DEMO (headless / no real app)")
    print("=" * 60)

    # Point at a fake path — agent handles missing apps gracefully
    agent = MainframeAgent(
        app_path="C:/MainframeApp/mainframe.exe",
        output_dir="demo_output"
    )

    print("\n[1/4] Discovering functionality…")
    discovery = agent.discover_functionality()
    print(f"  → App: {discovery.get('app_name')}")
    print(f"  → Type: {discovery.get('app_type')}")
    print(f"  → Features: {len(discovery.get('features', []))}")

    print("\n[2/4] Generating overview…")
    try:
        agent.generate_overview()
        print("  → overview saved to demo_output/app_overview.md")
    except Exception as e:
        print(f"  ⚠️  Needs ANTHROPIC_API_KEY: {type(e).__name__}")

    print("\n[3/4] Generating test cases…")
    try:
        suites = agent.generate_test_cases()
        total = sum(len(s.get("test_cases", [])) for s in suites)
        print(f"  → {total} test cases across {len(suites)} suites")
    except Exception as e:
        print(f"  ⚠️  Needs ANTHROPIC_API_KEY: {type(e).__name__}")

    print("\n[4/4] Running a sample natural-language command…")
    try:
        result = agent.execute_action("Navigate to the main menu and list all options")
        print(f"  → Observation: {result['observation'][:100]}…")
    except Exception as e:
        print(f"  ⚠️  Needs ANTHROPIC_API_KEY: {type(e).__name__}")

    print("\n✅ Demo complete! Check demo_output/ for all generated files.")
    print("   • discovery_report.md")
    print("   • app_overview.md")
    print("   • test_cases.md")
    print("   • test_cases.json")


if __name__ == "__main__":
    main()