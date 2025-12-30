from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.reviews import Review
from app.models.products import Product



async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(Review.grade)).where(
            Review.product_id == product_id,
            Review.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(Product, product_id)
    product.rating = avg_rating
    await db.commit()
