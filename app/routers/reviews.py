from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.schemas import Review as ReviewSchema, ReviewCreate
from app.db_depends import get_async_db
from app.auth import get_current_buyer, get_current_user
from app.utils.update_product_rating import update_product_rating

# Создаём маршрутизатор для отзывов
router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)


@router.get("/", response_model=list[ReviewSchema])
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных отзывов.
    """
    result = await db.scalars(
        select(ReviewModel).where(ReviewModel.is_active == True)
    )
    return result.all()


@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_buyer)
):
    """
    Создаёт новый отзыв для указанного товара (только для 'buyer').
    После добавления пересчитывает средний рейтинг товара.
    """
    product_result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == review.product_id,
            ProductModel.is_active == True
        )
    )
    product = product_result.first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )

    db_review = ReviewModel(
        user_id=current_user.id,
        product_id=review.product_id,
        comment=review.comment,
        grade=review.grade
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)

    await update_product_rating(db, review.product_id)
    
    return db_review


@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Выполняет мягкое удаление отзыва, если пользователь - автор отзыва или admin.
    После удаления пересчитывает рейтинг товара.
    """
    review_result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.id == review_id,
            ReviewModel.is_active == True
        )
    )
    review = review_result.first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or inactive"
        )

    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only author or admin can delete review"
        )

    review.is_active = False
    await db.commit()

    await update_product_rating(db, review.product_id)
    
    return {"message": "Review deleted"}

