"""
Patient routes for CRUD operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid

from src.database import get_db
from src.models.patient import Patient, PatientStatus, Gender, AnxietyLevel
from src.api.middleware.auth_middleware import get_current_user_id

# Router
patients_router = APIRouter()
security = HTTPBearer()


# Pydantic schemas
class PatientCreate(BaseModel):
    """Patient creation schema."""
    mrn: str
    name: str
    ic_number: Optional[str] = None
    date_of_birth: datetime
    gender: Gender
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    ed_visit_id: Optional[str] = None
    ward: Optional[str] = None
    bed_number: Optional[str] = None
    chief_complaint: Optional[str] = None
    clinical_notes: Optional[str] = None
    allergies: Optional[str] = None


class PatientUpdate(BaseModel):
    """Patient update schema."""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    ward: Optional[str] = None
    bed_number: Optional[str] = None
    chief_complaint: Optional[str] = None
    clinical_notes: Optional[str] = None
    allergies: Optional[str] = None
    status: Optional[PatientStatus] = None
    anxiety_level: Optional[AnxietyLevel] = None
    consent_given: Optional[bool] = None
    consent_timestamp: Optional[datetime] = None


class PatientResponse(BaseModel):
    """Patient response schema."""
    id: str
    mrn: str
    name: str
    ic_number: Optional[str]
    date_of_birth: datetime
    gender: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    ed_visit_id: Optional[str]
    ward: Optional[str]
    bed_number: Optional[str]
    chief_complaint: Optional[str]
    clinical_notes: Optional[str]
    allergies: Optional[str]
    status: str
    anxiety_level: str
    consent_given: bool
    consent_timestamp: Optional[datetime]
    registered_at: datetime
    updated_at: datetime


def patient_to_response(patient: Patient) -> PatientResponse:
    """Convert patient model to response."""
    return PatientResponse(
        id=patient.id,
        mrn=patient.mrn,
        name=patient.name,
        ic_number=patient.ic_number,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender.value,
        phone=patient.phone,
        email=patient.email,
        address=patient.address,
        ed_visit_id=patient.ed_visit_id,
        ward=patient.ward,
        bed_number=patient.bed_number,
        chief_complaint=patient.chief_complaint,
        clinical_notes=patient.clinical_notes,
        allergies=patient.allergies,
        status=patient.status.value,
        anxiety_level=patient.anxiety_level.value,
        consent_given=patient.consent_given,
        consent_timestamp=patient.consent_timestamp,
        registered_at=patient.registered_at,
        updated_at=patient.updated_at,
    )


@patients_router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Create a new patient."""
    await get_current_user_id(credentials)

    # Check if MRN already exists
    result = await db.execute(select(Patient).where(Patient.mrn == patient_data.mrn))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MRN already exists",
        )

    new_patient = Patient(**patient_data.model_dump())
    db.add(new_patient)
    await db.commit()
    await db.refresh(new_patient)

    return patient_to_response(new_patient)


@patients_router.get("/", response_model=list[PatientResponse])
async def list_patients(
    status: Optional[PatientStatus] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """List patients with optional filtering."""
    await get_current_user_id(credentials)

    query = select(Patient)
    if status:
        query = query.where(Patient.status == status)

    query = query.offset(skip).limit(limit).order_by(Patient.registered_at.desc())
    result = await db.execute(query)
    patients = result.scalars().all()

    return [patient_to_response(p) for p in patients]


@patients_router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get patient by ID."""
    await get_current_user_id(credentials)

    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient_to_response(patient)


@patients_router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Update patient information."""
    await get_current_user_id(credentials)

    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    patient.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(patient)

    return patient_to_response(patient)


@patients_router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Delete a patient (soft delete by setting inactive)."""
    await get_current_user_id(credentials)

    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    await db.delete(patient)
    await db.commit()

    return None


@patients_router.get("/mrn/{mrn}", response_model=PatientResponse)
async def get_patient_by_mrn(
    mrn: str,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get patient by MRN."""
    await get_current_user_id(credentials)

    result = await db.execute(select(Patient).where(Patient.mrn == mrn))
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient_to_response(patient)