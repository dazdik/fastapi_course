import uuid

import uvicorn
from fastapi import FastAPI, Response, HTTPException, Cookie

from fastapi.responses import FileResponse


from app.models import Feedback, UserCreate
from app.data import sample_products


app = FastAPI()


@app.get('/')
async def root():
    return FileResponse('index.html')


users: list[UserCreate] = []
sessions: dict = {}


@app.post('/create_user')
async def user_create(data: UserCreate):
    users.append(data)
    return data


@app.get('/show_users')
async def get_users():
    return users


@app.post('/login')
async def login(user: UserCreate, response: Response):
    for person in users:
        if person.email != user.email and person.password != user.password:
            raise HTTPException(status_code=400, detail='Введены некорректные данные, попробуйте снова')

        session_token = str(uuid.uuid1())
        sessions[session_token] = user
        response.set_cookie('session_token', session_token, httponly=True)
        return {'message': 'Куки установлены'}


@app.get('/user')
async def get_current_user(session_token = Cookie()):
    user = sessions.get(session_token)
    if not user:
        raise HTTPException(status_code=401, detail='Вы не авторизованы')
    return user.dict()


if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8066, reload=True, workers=3)