from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ReviewCreate(BaseModel):
    product_id: int = Field(description="ID товара, к которому относится отзыв")
    comment: str | None = Field(None, description="Текст отзыва")
    grade: int = Field(ge=1, le=5, description="Оценка товара (от 1 до 5)")

class Review(BaseModel):
    id: int = Field(description="Уникальный идентификатор отзыва")
    user_id: int = Field(description="ID пользователя, оставившего отзыв")
    product_id: int = Field(description="ID товара")
    comment: str | None = Field(None, description="Текст отзыва")
    comment_date: datetime = Field(description="Дата и время создания отзыва")
    grade: int = Field(description="Оценка товара (1-5)")
    is_active: bool = Field(description="Активность отзыва")

    model_config = ConfigDict(from_attributes=True)