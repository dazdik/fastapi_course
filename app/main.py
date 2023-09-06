import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.models import User


app = FastAPI()


@app.get('/')
async def root():
    return FileResponse('index.html')


# новый роут
@app.get('/custom')
def read_custom_message():
    return {'message': 'This is a custom message!'}


class SNums(BaseModel):
    num1: int
    num2: int


@app.post('/calculate')
async def calculate(numbers: SNums):

    return JSONResponse({"result": numbers.num1 + numbers.num2})


def check_age(age):
    return age >= 18


@app.post('/user')
async def create_user(data: User):
    return {
        'name': data.name,
        'age': data.age,
        'is_adult': check_age(data.age)
            }


if __name__ == '__main__':
    uvicorn.run(app,
                host='127.0.0.1',
                port=80)