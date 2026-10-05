from fastapi import FastAPI

app = FastAPI(title="Grainy API")


@app.get("/hello")
def hello() -> dict[str, str]:
    return {"message": "Hi, i'm Grainy! nice to meet ya!"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
