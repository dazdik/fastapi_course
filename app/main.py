import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse


from app.models import Feedback, UserCreate
from app.data import sample_products


app = FastAPI()


@app.get('/')
async def root():
    return FileResponse('index.html')


msg = []


@app.post('/feedback')
async def send_message(data: Feedback):
    msg.append({'name': data.name, 'message': data.message})
    return {"message": f"Feedback received. Thank you, {data.name}!"}


@app.get('/comments')
async def get_comments():
    return msg

users: list[UserCreate] = []


@app.post('/create_user')
async def user_create(data: UserCreate):
    users.append(data)
    return data


@app.get('/show_users')
async def get_users():
    return users


@app.get('/product/{product_id}')
async def get_product_by_id(product_id: int):
    product_by_id = [product for product in sample_products if product['product_id'] == product_id]
    return product_by_id[0] if product_by_id else 'Такого айди нет'


@app.get('/products/search/')
async def search_products(keyword: str, category:  str | None = None, limit: int = Query(10, ge=1)):
    list_of_key = [product for product in sample_products if keyword.lower() in product['name'].lower()]
    if category:
        list_of_key = [product for product in list_of_key if product['category'].lower() == category.lower()]
    return list_of_key[:limit]


if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8066, reload=True, workers=3)