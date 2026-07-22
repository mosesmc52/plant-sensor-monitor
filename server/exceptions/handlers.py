from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


async def handle_unexpected_error(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    print(f"Unexpected server error: {exception}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "accepted": False,
            "error": "Internal server error",
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        Exception,
        handle_unexpected_error,
    )
