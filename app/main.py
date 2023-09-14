import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.models import User


app = FastAPI()


@app.get('/')
async def root():
    return FileResponse('index.html')

fake_users = {
    1: {'username': 'junior_dev', 'email': 'jundev@bk.ru'},
    2: {'username': 'middle_dev', 'email': 'middledev@bk.ru'},
}


@app.get('/users/{user_id}')
def get_users(user_id: int):
    if user_id in fake_users:
        return fake_users[user_id]
    return {'error': 'user not found'}


@app.get('/users/')
def get_limit_user(limit: int = 10):
    return dict(list(fake_users.items())[:limit])


if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8066, reload=True, workers=3)