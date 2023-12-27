import re
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status

from fastapi.exceptions import RequestValidationError

from app.exceptions import (
    global_exception_handler,
    CustomException,
    custom_exception_handler,
    CustomUsernameException,
    custom_exception_handler_username,
    CustomPasswordException,
    custom_exception_handler_password,
    custom_request_validation_exception_handler,
)
from products.views import router as product_router
from todos.views import router as todo_router
from user.views import router as user_router
from user.auth import router as auth_router
from app.db_config import sessionmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if sessionmanager.engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan)
app.include_router(product_router)
app.include_router(todo_router)
app.include_router(user_router)
app.include_router(auth_router)


app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(CustomUsernameException, custom_exception_handler_username)
app.add_exception_handler(CustomPasswordException, custom_exception_handler_password)
app.add_exception_handler(
    RequestValidationError, custom_request_validation_exception_handler
)
app.add_exception_handler(HTTPException, global_exception_handler)


ACCEPT_LANGUAGE_PATTERN = (
    r"(?i:(?:\*|[a-z\-]{2,5})(?:;q=\d\.\d)?,)+(?:\*|[a-z\-]{2,5})(?:;q=\d\.\d)?"
)


@app.get("/headers")
async def get_headers(request: Request):
    headers = request.headers
    user_agent = headers.get("User-Agent")
    accept_language = headers.get("Accept-Language")
    if user_agent is None and accept_language is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="необходимые заголовки отсутствуют",
        )
    if not re.match(ACCEPT_LANGUAGE_PATTERN, accept_language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="неправильный формат Accept-Language",
        )
    return {"User-Agent": user_agent, "Accept-Language": accept_language}


@app.get("/sum/")
def calculate_sum(a: int, b: int):
    return {"result": a + b}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8066,
        reload=True,
        workers=3,
    )
