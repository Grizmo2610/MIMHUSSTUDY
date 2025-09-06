from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import routers

app = FastAPI()

for r in routers:
    app.include_router(r)

app.mount("/static", StaticFiles(directory="static"), name="static")