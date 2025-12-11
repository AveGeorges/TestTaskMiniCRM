from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/stats", tags=["Статистика"])


@router.get("/contacts")
def get_contact_stats(db: Session = Depends(get_db)):
    """Получить статистику по обращениям"""
    total_contacts = db.query(models.Contact).count()

    contacts_by_source = db.query(
        models.Source.name,
        func.count(models.Contact.id).label("count")
    ).join(
        models.Contact, models.Contact.source_id == models.Source.id
    ).group_by(models.Source.id).all()

    source_dict = {name: count for name, count in contacts_by_source}

    contacts_by_operator = db.query(
        models.Operator.name,
        func.count(models.Contact.id).label("count")
    ).join(
        models.Contact, models.Contact.operator_id == models.Operator.id
    ).group_by(models.Operator.id).all()

    operator_dict = {name: count for name, count in contacts_by_operator}

    return {
        "total_contacts": total_contacts,
        "contacts_by_source": source_dict,
        "contacts_by_operator": operator_dict
    }


@router.get("/distribution")
def get_distribution_stats(db: Session = Depends(get_db)):
    """Получить статистику распределения обращений по источникам и операторам"""
    stats = db.query(
        models.Source.name.label("source_name"),
        models.Operator.name.label("operator_name"),
        func.count(models.Contact.id).label("contact_count")
    ).join(
        models.Contact, models.Contact.source_id == models.Source.id
    ).join(
        models.Operator, models.Contact.operator_id == models.Operator.id
    ).group_by(
        models.Source.id, models.Operator.id
    ).all()

    result = {}
    for source_name, operator_name, count in stats:
        if source_name not in result:
            result[source_name] = {}
        result[source_name][operator_name] = count

    return result

