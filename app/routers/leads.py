from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("/", response_model=List[schemas.LeadResponse])
def get_leads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список лидов"""
    leads = db.query(models.Lead).offset(skip).limit(limit).all()
    return leads


@router.get("/{lead_id}", response_model=schemas.LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Получить лида по ID"""
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.get("/{lead_id}/contacts", response_model=List[schemas.ContactResponse])
def get_lead_contacts(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Получить все обращения конкретного лида"""
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    contacts = db.query(models.Contact).filter(models.Contact.lead_id == lead_id).all()

    result = []
    for contact in contacts:
        result.append(schemas.ContactResponse(
            id=contact.id,
            lead_id=contact.lead_id,
            source_id=contact.source_id,
            operator_id=contact.operator_id,
            status=contact.status,
            created_at=contact.created_at,
            lead=schemas.LeadResponse.model_validate(contact.lead),
            source=schemas.SourceResponse.model_validate(contact.source),
            operator=schemas.OperatorResponse.model_validate(contact.operator) if contact.operator else None
        ))
    return result

