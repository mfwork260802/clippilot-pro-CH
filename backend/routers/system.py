import os
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from backend.services.system_service import (
    auto_cleanup_expired_files,
    cleanup_expired_temp_files,
    clear_temp_files,
    get_current_git_info,
    get_temp_storage_summary,
    is_update_allowed,
)

router = APIRouter(tags=["System"])


def verify_admin_access(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
) -> bool:
    """
    Verifies administrative authorization.
    If ADMIN_API_KEY or CHEAT_CLIP_API_KEY is configured in .env, requires matching token.
    If no secret key is set, allows open access for local desktop installation.
    """
    admin_key = (os.environ.get("ADMIN_API_KEY") or os.environ.get("CHEAT_CLIP_API_KEY") or "").strip()
    if not admin_key:
        return True

    provided = (x_api_key or "").strip()
    if not provided and authorization and authorization.startswith("Bearer "):
        provided = authorization[7:].strip()

    if not secrets.compare_digest(provided, admin_key):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing administrator API key")
    return True


@router.get("/api/temp-storage-info")
async def get_temp_storage_info():
    """Returns total files, bytes, and formatted size of temp download storage."""
    return get_temp_storage_summary()


@router.post("/api/clear-temp")
async def clear_temp_folder(authorized: bool = Depends(verify_admin_access)):
    """
    Clears all temporary downloaded video clips, audio slices, ASS files, and frames
    from TEMP_DIR and backend/temp. Re-creates empty directories.
    PROTECTED: cookies.txt and any cookie files are strictly PRESERVED and NEVER deleted.
    """
    if not is_update_allowed():
        raise HTTPException(
            status_code=403,
            detail="Manual server-side cache clearing is disabled in server mode for safety. Background auto-cleanup manages server storage automatically."
        )
    return clear_temp_files()


@router.post("/api/cleanup-expired-temp")
async def cleanup_expired_temp(max_age_hours: int = 1, authorized: bool = Depends(verify_admin_access)):
    """Deletes temporary frame images and slices older than max_age_hours."""
    return cleanup_expired_temp_files(max_age_hours=max_age_hours)


@router.post("/api/auto-cleanup")
async def api_trigger_auto_cleanup(
    max_age_seconds: int = 3600,
    max_storage_gb: float = 5.0,
    authorized: bool = Depends(verify_admin_access)
):
    """Manually triggers dual-mode auto-cleanup (Option 1: TTL + Option 2: Quota)."""
    return auto_cleanup_expired_files(
        max_age_seconds=max_age_seconds,
        max_storage_bytes=int(max_storage_gb * 1024 * 1024 * 1024)
    )


@router.get("/api/system/version")
def api_system_version():
    """Returns local git version information. Self-update is disabled in this build."""
    return {**get_current_git_info(), "allow_update": False}
