"""Application entry point.

Run with:
    uvicorn src.main:app --reload
"""

from src.app import create_app

app = create_app()
