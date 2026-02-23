"""API routes for ED CT Brain Workflow System."""

from src.api.routes.auth import auth_router
from src.api.routes.patients import patients_router
from src.api.routes.scans import scans_router
from src.api.routes.users import users_router
from src.api.routes.resources import resources_router
from src.api.routes.faq import faq_router
from src.api.routes.dashboard import dashboard_router

__all__ = [
    "auth_router",
    "patients_router",
    "scans_router",
    "users_router",
    "resources_router",
    "faq_router",
    "dashboard_router",
]