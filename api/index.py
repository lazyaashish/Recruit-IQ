"""
Vercel serverless entry point for RecruitIQ FastAPI backend.
Vercel Python runtime calls the `app` ASGI object from this module.
"""
import sys
import os

# Make the backend package importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app  # noqa: F401 — Vercel discovers this ASGI app
