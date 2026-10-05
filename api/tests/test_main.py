import pytest
from httpx import ASGITransport, AsyncClient

from main import app

transport = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_health_returns_ok() -> None:
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_hello_returns_greeting() -> None:
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hi, i'm Grainy! nice to meet ya!"}


@pytest.mark.asyncio
async def test_cors_allows_github_pages_origin() -> None:
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/health",
            headers={"Origin": "https://arie-chocron.github.io"},
        )

    assert response.headers["access-control-allow-origin"] == (
        "https://arie-chocron.github.io"
    )


@pytest.mark.asyncio
async def test_cors_allows_localhost_with_arbitrary_port() -> None:
    origin = "http://localhost:5173"
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health", headers={"Origin": origin})

    assert response.headers["access-control-allow-origin"] == origin
