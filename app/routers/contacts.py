from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.services import DistributionService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=schemas.ContactResponse)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db)
):
    """
    Зарегистрировать обращение от лида.
    Система автоматически:
    - найдет или создаст лида
    - выберет оператора по правилам распределения
    - создаст обращение
    """
    source = db.query(models.Source).filter(models.Source.id == contact.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    db_contact = DistributionService.distribute_contact(db=db, contact_data=contact)

    return schemas.ContactResponse(
        id=db_contact.id,
        lead_id=db_contact.lead_id,
        source_id=db_contact.source_id,
        operator_id=db_contact.operator_id,
        status=db_contact.status,
        created_at=db_contact.created_at,
        lead=schemas.LeadResponse.model_validate(db_contact.lead),
        source=schemas.SourceResponse.model_validate(db_contact.source),
        operator=schemas.OperatorResponse.model_validate(db_contact.operator) if db_contact.operator else None
    )


@router.get("/", response_model=List[schemas.ContactResponse])
def get_contacts(
    skip: int = 0,
    limit: int = 100,
    lead_id: int = None,
    source_id: int = None,
    operator_id: int = None,
    db: Session = Depends(get_db)
):
    """Получить список обращений с фильтрацией"""
    query = db.query(models.Contact)

    if lead_id:
        query = query.filter(models.Contact.lead_id == lead_id)
    if source_id:
        query = query.filter(models.Contact.source_id == source_id)
    if operator_id:
        query = query.filter(models.Contact.operator_id == operator_id)

    contacts = query.offset(skip).limit(limit).all()

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


@router.get("/{contact_id}", response_model=schemas.ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):
    """Получить обращение по ID"""
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    return schemas.ContactResponse(
        id=contact.id,
        lead_id=contact.lead_id,
        source_id=contact.source_id,
        operator_id=contact.operator_id,
        status=contact.status,
        created_at=contact.created_at,
        lead=schemas.LeadResponse.model_validate(contact.lead),
        source=schemas.SourceResponse.model_validate(contact.source),
        operator=schemas.OperatorResponse.model_validate(contact.operator) if contact.operator else None
    )

