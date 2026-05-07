#!/usr/bin/env python3
"""
mainframe_agent CLI
Usage:
  python main.py --app /path/to/app.exe --task discover
  python main.py --app /path/to/app.exe --task test
  python main.py --app /path/to/app.exe --task report
  python main.py --app /path/to/app.exe --task run --command "Navigate to transaction screen"
  python main.py --app /path/to/app.exe --task interactive
"""

import argparse
import sys
import os
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent))
from core.agent import MainframeAgent


BANNER = r"""
╔══════════════════════════════════════════════════════╗
║   ███╗   ███╗ █████╗ ██╗███╗   ██╗███████╗          ║
║   ████╗ ████║██╔══██╗██║████╗  ██║██╔════╝          ║
║   ██╔████╔██║███████║██║██╔██╗ ██║█████╗            ║
║   ██║╚██╔╝██║██╔══██║██║██║╚██╗██║██╔══╝            ║
║   ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║██║               ║
║   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝               ║
║                                                      ║
║   FRAME  AUTOMATION  AGENT   v1.0                    ║
║   AI-Powered Desktop App Automation                  ║
╚══════════════════════════════════════════════════════╝
"""


def interactive_mode(agent: MainframeAgent):
    """REPL loop for natural-language commands."""
    print("\n🟢 Interactive mode. Type 'help' for commands, 'quit' to exit.\n")

    COMMANDS = {
        "discover":  "Discover all app functionality",
        "test":      "Generate & run test cases",
        "overview":  "Generate application overview",
        "report":    "Generate full HTML report",
        "log":       "Show session log",
        "help":      "Show this help",
        "quit":      "Exit",
    }

    while True:
        try:
            cmd = input("agent> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not cmd:
            continue
        if cmd == "quit":
            break
        elif cmd == "help":
            for k, v in COMMANDS.items():
                print(f"  {k:<12} {v}")
            print("  Or type any natural-language instruction.")
        elif cmd == "discover":
            agent.discover_functionality()
        elif cmd == "test":
            suites = agent.generate_test_cases()
            agent.run_test_suite(suites)
        elif cmd == "overview":
            agent.generate_overview()
        elif cmd == "report":
            path = agent.generate_full_report()
            print(f"\n📄 Report: {path}")
        elif cmd == "log":
            for i, entry in enumerate(agent.session_log, 1):
                print(f"  [{i}] {entry['timestamp']}  {entry['command'][:60]}")
        else:
            agent.execute_action(cmd)


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="AI-powered mainframe/desktop automation agent"
    )
    parser.add_argument(
        "--app", required=True,
        help="Path to the mainframe/desktop application executable"
    )
    parser.add_argument(
        "--task",
        choices=["discover", "test", "report", "run", "interactive", "overview"],
        default="interactive",
        help="Task to perform (default: interactive)"
    )
    parser.add_argument(
        "--command",
        help="Natural language command (used with --task run)"
    )
    parser.add_argument(
        "--output", default="output",
        help="Output directory for reports and screenshots (default: output)"
    )
    parser.add_argument(
        "--no-launch", action="store_true",
        help="Skip launching the app (assume it is already running)"
    )

    args = parser.parse_args()

    # Validate app path
    app_path = Path(args.app)
    if not app_path.exists():
        print(f"⚠️  App path not found: {app_path}")
        print("   Continuing in analysis/simulation mode…")

    # Create agent
    agent = MainframeAgent(app_path=str(app_path), output_dir=args.output)

    # Launch app
    if not args.no_launch and app_path.exists():
        launched = agent.launch_app()
        if not launched:
            print("⚠️  Could not launch app, continuing anyway…")

    # Execute task
    try:
        if args.task == "discover":
            result = agent.discover_functionality()
            print(f"\n✅ Discovered {len(result.get('features', []))} features")

        elif args.task == "overview":
            agent.generate_overview()

        elif args.task == "test":
            suites = agent.generate_test_cases()
            results = agent.run_test_suite(suites)
            print(f"\n📊 {results['passed']}/{results['total']} tests passed")

        elif args.task == "report":
            path = agent.generate_full_report()
            print(f"\n📄 Full report: {path}")

        elif args.task == "run":
            if not args.command:
                print("❌ --command is required with --task run")
                sys.exit(1)
            agent.execute_action(args.command)

        elif args.task == "interactive":
            interactive_mode(agent)

    finally:
        agent.close_app()
        print(f"\n📁 Outputs saved to: {args.output}/")
        print("   Files:")
        for f in Path(args.output).glob("*"):
            print(f"   • {f.name}")


if __name__ == "__main__":
    main()