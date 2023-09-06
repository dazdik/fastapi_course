import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel


app = FastAPI()

@app.get('/')
async def root():
    return FileResponse('index.html')


class SNums(BaseModel):
    num1: int
    num2: int


@app.post('/calculate')
async def calculate(numbers: SNums):

    return JSONResponse({"result": numbers.num1 + numbers.num2})


if __name__ == '__main__':
    uvicorn.run(app,
                host='127.0.0.1',
                port=80)