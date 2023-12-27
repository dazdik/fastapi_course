from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_config import get_db_session
from app.models import Product
from app.schemas import ProductSchema

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "/",
)
async def get_products(session: AsyncSession = Depends(get_db_session)):
    stmt = select(Product).order_by(Product.id)
    res: Result = await session.execute(stmt)
    products = res.scalars().all()
    return list(products)


@router.post(
    "/create_products/",
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product: ProductSchema, session: AsyncSession = Depends(get_db_session)
) -> ProductSchema:
    product = Product(
        name=product.name,
        description=product.description,
        category=product.category,
        price=product.price,
    )
    session.add(product)
    await session.commit()
    return product


@router.get("/{product_id}")
async def get_product_by_id(
    product_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    stmt = await session.execute(select(Product).filter(Product.id == product_id))
    product = stmt.scalar_one_or_none()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="id not found"
        )
    return product


@router.get("/products/search")
async def search_exactly_product(
    keyword: str,
    category: str | None = None,
    limit: int = Query(10, le=10),
    session: AsyncSession = Depends(get_db_session),
):
    stmt = select(Product).where(Product.name.ilike(f"%{keyword}%"))
    if category:
        stmt = stmt.where(Product.category.ilike(f"%{category}%"))
    stmt = stmt.limit(limit)
    result: Result = await session.execute(stmt)
    products = result.scalars().all()
    return list(products)
