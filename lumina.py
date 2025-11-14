#!/usr/bin/env python3
"""
Lumina - AI Meeting Assistant
Main entry point for the application
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the FastAPI app
from src.core.lumina import app

if __name__ == "__main__":
    import uvicorn

    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║              ✨ Lumina - Meeting Assistant ✨         ║
    ║                                                       ║
    ║  Automatically joins and records Google Meet sessions ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    uvicorn.run(app, host="0.0.0.0", port=8000)
