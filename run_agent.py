from __future__ import annotations

import json

from app.config import settings
from app.discovery.analyzer import MainframeAnalyzer
from app.discovery.crawler import MainframeCrawler
from app.logging import log
from app.mainframe.ehllapi import EHLLAPI
from app.mainframe.launcher import MainframeLauncher
from app.mainframe.navigator import Navigator
from app.mainframe.screen_parser import ScreenParser
from app.mainframe.session import SessionManager
from app.testing.testcase_generator import TestCaseGenerator


def run_discovery(max_depth: int = 3) -> dict[str, str]:
    if settings.logfire_token:
        log.configure(token=settings.logfire_token)

    launcher = MainframeLauncher(
        workspace_path=settings.pcomm_workspace_path,
        executable_path=settings.pcomm_exe_path,
    )
    launcher.launch()

    ehllapi = EHLLAPI()
    session = SessionManager(ehllapi, session_id=settings.session_id)
    session.ensure_connected()

    parser = ScreenParser(width=settings.screen_width)
    navigator = Navigator(ehllapi, parser, wait_seconds=settings.action_timeout_seconds)

    crawler = MainframeCrawler(navigator, parser)
    crawler.crawl(max_depth=max_depth)
    graph_path = crawler.save_graph(settings.data_dir / "screen_graph.json")

    analyzer = MainframeAnalyzer(api_key=settings.openai_api_key, model=settings.openai_model)
    overview = analyzer.generate_overview(crawler.graph)

    testcase_generator = TestCaseGenerator(api_key=settings.openai_api_key, model=settings.openai_model)
    testcases = testcase_generator.generate(crawler.graph)

    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    overview_path = settings.reports_dir / "functional_overview.md"
    testcase_path = settings.reports_dir / "generated_testcases.md"
    overview_path.write_text(overview, encoding="utf-8")
    testcase_path.write_text(testcases, encoding="utf-8")

    session.disconnect()
    return {
        "graph_path": str(graph_path),
        "overview_path": str(overview_path),
        "testcase_path": str(testcase_path),
    }


if __name__ == "__main__":
    result = run_discovery(max_depth=3)
    log.info("Discovery completed: {result}", result=json.dumps(result))
