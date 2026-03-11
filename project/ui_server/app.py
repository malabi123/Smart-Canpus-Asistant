from fastapi import FastAPI, Request
import uuid
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routes import routers


app = FastAPI()


BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.mount("/static", StaticFiles(directory=BASE_DIR/"static"), name="static")

for r in routers:
    app.include_router(r)


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(r"index.html", {"request": request})


@app.get("/get_token")
def get_token():
    user_token = str(uuid.uuid4())
    return {"user_token": user_token}
