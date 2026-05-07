from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel


class ExecuteRequest(BaseModel):
    instruction: str


def build_router(executor=None, runtime_error: str | None = None) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.post("/execute")
    def execute(payload: ExecuteRequest) -> dict[str, object]:
        if executor is None:
            raise HTTPException(
                status_code=503,
                detail=runtime_error or "Mainframe runtime is not initialized.",
            )
        try:
            plan = executor.execute(payload.instruction)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return plan.model_dump()

    return router
