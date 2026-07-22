from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Used to confirm that the Raspberry Pi server is running."""

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
