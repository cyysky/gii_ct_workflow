"""
FAQ routes for patient education content management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from src.database import get_db
from src.models.faq import FAQ
from src.api.middleware.auth_middleware import get_current_user_id

# Router
faq_router = APIRouter()
security = HTTPBearer()


# Pydantic schemas
class FAQCreate(BaseModel):
    """FAQ creation schema."""
    question: str
    answer: str
    category: str
    keywords: Optional[str] = None
    language: str = "en"


class FAQUpdate(BaseModel):
    """FAQ update schema."""
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[str] = None
    is_active: Optional[bool] = None


class FAQResponse(BaseModel):
    """FAQ response schema."""
    id: str
    question: str
    answer: str
    category: str
    keywords: Optional[str]
    language: str
    view_count: int
    helpful_count: int
    not_helpful_count: int
    is_active: bool
    created_at: str


def faq_to_response(faq: FAQ) -> FAQResponse:
    """Convert FAQ model to response."""
    return FAQResponse(
        id=faq.id,
        question=faq.question,
        answer=faq.answer,
        category=faq.category,
        keywords=faq.keywords,
        language=faq.language,
        view_count=faq.view_count,
        helpful_count=faq.helpful_count,
        not_helpful_count=faq.not_helpful_count,
        is_active=faq.is_active,
        created_at=faq.created_at.isoformat(),
    )


@faq_router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(
    faq_data: FAQCreate,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Create a new FAQ."""
    await get_current_user_id(credentials)

    new_faq = FAQ(**faq_data.model_dump())
    db.add(new_faq)
    await db.commit()
    await db.refresh(new_faq)

    return faq_to_response(new_faq)


@faq_router.get("/", response_model=list[FAQResponse])
async def list_faqs(
    category: Optional[str] = None,
    is_active: Optional[bool] = True,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List FAQs with optional filtering."""
    query = select(FAQ)
    if category:
        query = query.where(FAQ.category == category)
    if is_active is not None:
        query = query.where(FAQ.is_active == is_active)

    query = query.offset(skip).limit(limit).order_by(FAQ.category, FAQ.created_at)
    result = await db.execute(query)
    faqs = result.scalars().all()

    return [faq_to_response(f) for f in faqs]


@faq_router.get("/categories")
async def get_categories(
    db: AsyncSession = Depends(get_db),
):
    """Get list of FAQ categories."""
    result = await db.execute(
        select(FAQ.category).where(FAQ.is_active == True).distinct()
    )
    categories = result.scalars().all()
    return {"categories": [c for c in categories if c]}


@faq_router.get("/{faq_id}", response_model=FAQResponse)
async def get_faq(
    faq_id: str,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get FAQ by ID."""
    await get_current_user_id(credentials)

    result = await db.execute(select(FAQ).where(FAQ.id == faq_id))
    faq = result.scalar_one_or_none()

    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )

    # Increment view count
    faq.view_count += 1
    await db.commit()

    return faq_to_response(faq)


@faq_router.put("/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: str,
    faq_data: FAQUpdate,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Update FAQ."""
    await get_current_user_id(credentials)

    result = await db.execute(select(FAQ).where(FAQ.id == faq_id))
    faq = result.scalar_one_or_none()

    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )

    update_data = faq_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(faq, field, value)

    await db.commit()
    await db.refresh(faq)

    return faq_to_response(faq)


@faq_router.post("/{faq_id}/feedback")
async def provide_feedback(
    faq_id: str,
    helpful: bool,
    db: AsyncSession = Depends(get_db),
):
    """Provide feedback on FAQ helpfulness."""
    result = await db.execute(select(FAQ).where(FAQ.id == faq_id))
    faq = result.scalar_one_or_none()

    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )

    if helpful:
        faq.helpful_count += 1
    else:
        faq.not_helpful_count += 1

    await db.commit()

    return {"message": "Feedback recorded"}


@faq_router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    faq_id: str,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Delete an FAQ."""
    await get_current_user_id(credentials)

    result = await db.execute(select(FAQ).where(FAQ.id == faq_id))
    faq = result.scalar_one_or_none()

    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ not found",
        )

    await db.delete(faq)
    await db.commit()

    return None