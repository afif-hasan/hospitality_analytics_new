from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ):
        errors = [
            {
                "field": ".".join(str(loc) for loc in err["loc"]),
                "message": err["msg"],
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation error", "errors": errors},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )