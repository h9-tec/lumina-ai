"""API endpoints modules"""
from .meetings import router as meetings_router
from .recordings import router as recordings_router
from .transcripts import router as transcripts_router
from .minutes import router as minutes_router
from .config import router as config_router

__all__ = [
    'meetings_router',
    'recordings_router',
    'transcripts_router',
    'minutes_router',
    'config_router'
]
