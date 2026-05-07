from __future__ import annotations

from fastapi import FastAPI

from app.agent.executor import AgentExecutor
from app.agent.planner import AIPlanner
from app.api.routes import build_router
from app.config import settings
from app.logging import log
from app.mainframe.ehllapi import EHLLAPI
from app.mainframe.navigator import Navigator
from app.mainframe.screen_parser import ScreenParser
from app.mainframe.session import SessionManager

if settings.logfire_token:
    log.configure(token=settings.logfire_token)

app = FastAPI(title="Mainframe AI Agent")

executor = None
runtime_error = None
try:
    ehllapi = EHLLAPI(dll_name=settings.ehllapi_dll_path or "ehlapi32.dll")
    session = SessionManager(ehllapi, session_id=settings.session_id)
    session.ensure_connected()
    parser = ScreenParser(width=settings.screen_width)
    navigator = Navigator(ehllapi, parser, wait_seconds=settings.action_timeout_seconds)
    planner = AIPlanner(api_key=settings.openai_api_key, model=settings.openai_model)
    executor = AgentExecutor(planner, navigator, parser)
except Exception as exc:
    runtime_error = str(exc)
    log.warning("Mainframe runtime initialization failed: {error}", error=runtime_error)

app.include_router(build_router(executor, runtime_error=runtime_error))
