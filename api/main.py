import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Grainy API")

default_allowed_origins = ["https://arie-chocron.github.io"]
configured_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(dict.fromkeys(default_allowed_origins + configured_origins)),
    allow_origin_regex=r"^http://localhost(?::\d+)?$",
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/hello")
def hello() -> dict[str, str]:
    return {"message": "Hi, i'm Grainy! nice to meet ya!"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
