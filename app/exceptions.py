from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error_code: int
    error_details: str = None
    error_message: str
    url: str


class CustomException(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)


class CustomUsernameException(HTTPException):
    def __init__(self, detail: str, status_code: int = 401):
        super().__init__(status_code=status_code, detail=detail)


class CustomPasswordException(HTTPException):
    def __init__(self, detail: str, status_code: int = 401):
        super().__init__(status_code=status_code, detail=detail)


async def custom_exception_handler(request: Request, exc: CustomException):
    error_response = ErrorResponse(
        url=str(request.url),
        error_code=exc.status_code,
        error_details=str(exc.detail),
        error_message="Не расстрайвайся",
    )
    return JSONResponse(
        status_code=exc.status_code, content=error_response.model_dump()
    )


async def custom_exception_handler_username(
    request: Request, exc: CustomUsernameException
):
    error_response = ErrorResponse(
        url=str(request.url),
        error_code=exc.status_code,
        error_details=str(exc.detail),
        error_message="Не расстраивайся",
    )
    return JSONResponse(
        status_code=exc.status_code, content=error_response.model_dump()
    )


async def custom_exception_handler_password(
    request: Request, exc: CustomPasswordException
):
    error_response = ErrorResponse(
        url=str(request.url),
        error_code=exc.status_code,
        error_details=str(exc.detail),
        error_message="Не расстраивайся",
    )
    return JSONResponse(
        status_code=exc.status_code, content=error_response.model_dump()
    )


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "message": "Необработанная ошибка",
        },
    )


async def custom_request_validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"message": "Кастомный Validation Error", "errors": exc.errors()},
    )
