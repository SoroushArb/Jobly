from .profile import router as profile_router
from .jobs import router as jobs_router
from .matches import router as matches_router
from .packets import router as packets_router
from .interview import router as interview_router
from .applications import router as applications_router
from .prefill import router as prefill_router
from .cvs import router as cvs_router

__all__ = [
    "profile_router",
    "jobs_router",
    "matches_router",
    "packets_router",
    "interview_router",
    "applications_router",
    "prefill_router",
    "cvs_router",
]
