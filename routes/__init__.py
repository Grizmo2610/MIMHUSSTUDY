from .pages import router as page_route
from .engine import router as engine_route
from .auth import router as auth_route
routers = [page_route, engine_route, auth_route]
