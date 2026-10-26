"""
Simple password gate for single-owner deployments (e.g. Railway).

Set APP_PASSWORD to enable it. When enabled, every /api/* route except the
auth endpoints and the health check requires a signed session cookie that is
issued by POST /api/auth/login. Changing APP_PASSWORD invalidates all sessions.
"""
import hashlib
import hmac
import os
import secrets
import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

COOKIE_NAME = "chp_session"
SESSION_MAX_AGE = 30 * 24 * 3600
OPEN_PATHS = {"/api/health", "/api/auth/login", "/api/auth/logout", "/api/auth/status"}

# Login throttling: at most MAX_ATTEMPTS failed logins per IP within WINDOW seconds.
MAX_ATTEMPTS = 10
WINDOW = 600
_failed_attempts: dict[str, deque] = defaultdict(deque)

router = APIRouter(tags=["Auth"])


def _password() -> str:
    return os.environ.get("APP_PASSWORD", "")


def auth_enabled() -> bool:
    return bool(_password())


def _signing_key() -> bytes:
    secret = os.environ.get("SESSION_SECRET", "")
    return hashlib.sha256(f"{secret}|{_password()}".encode()).digest()


def _sign(issued_at: int) -> str:
    mac = hmac.new(_signing_key(), str(issued_at).encode(), hashlib.sha256).hexdigest()
    return f"{issued_at}.{mac}"


def _valid_token(token: str | None) -> bool:
    if not token or "." not in token:
        return False
    issued, _, _mac = token.partition(".")
    if not issued.isdigit():
        return False
    if time.time() - int(issued) > SESSION_MAX_AGE:
        return False
    return hmac.compare_digest(token, _sign(int(issued)))


def is_authenticated(request: Request) -> bool:
    return not auth_enabled() or _valid_token(request.cookies.get(COOKIE_NAME))


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    return forwarded.split(",")[0].strip() or (request.client.host if request.client else "unknown")


async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if (
        auth_enabled()
        and path.startswith("/api/")
        and path not in OPEN_PATHS
        and request.method != "OPTIONS"
        and not is_authenticated(request)
    ):
        return JSONResponse(status_code=401, content={"detail": "Login required."})
    return await call_next(request)


class LoginRequest(BaseModel):
    password: str


@router.get("/api/auth/status")
def auth_status(request: Request):
    return {"required": auth_enabled(), "authenticated": is_authenticated(request)}


@router.post("/api/auth/login")
def login(body: LoginRequest, request: Request, response: Response):
    if not auth_enabled():
        return {"ok": True}

    ip = _client_ip(request)
    attempts = _failed_attempts[ip]
    now = time.time()
    while attempts and now - attempts[0] > WINDOW:
        attempts.popleft()
    if len(attempts) >= MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many attempts. Try again in a few minutes.")

    if not secrets.compare_digest(body.password.encode(), _password().encode()):
        attempts.append(now)
        raise HTTPException(status_code=401, detail="Wrong password.")

    attempts.clear()
    secure = request.headers.get("x-forwarded-proto", request.url.scheme) == "https"
    response.set_cookie(
        COOKIE_NAME,
        _sign(int(now)),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )
    return {"ok": True}


@router.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}
