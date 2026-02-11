#!/usr/bin/env python3
"""
FastAPI backend for the Intelligent Music Agent.

This service provides a web API that can be consumed by the Next.js frontend.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from music_agent import ComprehensiveMusicAgent


def _cors_origins_from_env() -> List[str]:
    raw = os.getenv(
        "MUSIC_AGENT_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or ["http://localhost:3000", "http://127.0.0.1:3000"]


@lru_cache(maxsize=1)
def get_agent() -> ComprehensiveMusicAgent:
    return ComprehensiveMusicAgent()


app = FastAPI(
    title="Intelligent Music Agent API",
    description="Web API backend for music command processing and Spotify integration.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins_from_env(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommandRequest(BaseModel):
    command: str = Field(min_length=1, max_length=500)


class CommandResponse(BaseModel):
    status: str
    message: str


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "music-agent-api",
        "playback_backend": "spotify_web_api",
    }


@app.get("/api/status")
def status() -> Dict[str, Any]:
    agent = get_agent()
    current_track = agent.get_current_track()

    return {
        "status": "success",
        "music_agent_ready": True,
        "spotify_connected": bool(agent.sp),
        "spotify_auth_mode": agent.spotify_auth_mode,
        "playback_backend": "spotify_web_api",
        "current_track": current_track,
    }


@app.post("/api/command", response_model=CommandResponse)
def command(request: CommandRequest) -> CommandResponse:
    command_text = request.command.strip()
    if not command_text:
        raise HTTPException(status_code=400, detail="Command cannot be empty.")

    agent = get_agent()
    try:
        message = agent.handle_command(command_text)
        return CommandResponse(status="success", message=message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Command failed: {exc}") from exc

