from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("/", response_model=schemas.SourceResponse)
def create_source(
    source: schemas.SourceCreate,
    db: Session = Depends(get_db)
):
    """Создать источник (бота)"""
    db_source = models.Source(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@router.get("/", response_model=List[schemas.SourceResponse])
def get_sources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список источников"""
    sources = db.query(models.Source).offset(skip).limit(limit).all()
    return sources


@router.get("/{source_id}", response_model=schemas.SourceResponse)
def get_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """Получить источник по ID"""
    source = db.query(models.Source).filter(models.Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.post("/{source_id}/distribution", response_model=List[schemas.SourceOperatorWeightResponse])
def set_source_distribution(
    source_id: int,
    config: schemas.SourceDistributionConfig,
    db: Session = Depends(get_db)
):
    """Настроить распределение для источника (операторы и их веса)"""
    source = db.query(models.Source).filter(models.Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    db.query(models.SourceOperatorWeight).filter(
        models.SourceOperatorWeight.source_id == source_id
    ).delete()

    weights = []
    for weight_data in config.operator_weights:
        operator = db.query(models.Operator).filter(
            models.Operator.id == weight_data.operator_id
        ).first()
        if not operator:
            raise HTTPException(
                status_code=404,
                detail=f"Operator with id {weight_data.operator_id} not found"
            )

        weight_obj = models.SourceOperatorWeight(
            source_id=source_id,
            operator_id=weight_data.operator_id,
            weight=weight_data.weight
        )
        db.add(weight_obj)
        weights.append(weight_obj)

    db.commit()
    for weight in weights:
        db.refresh(weight)

    return weights


@router.get("/{source_id}/distribution", response_model=List[schemas.SourceOperatorWeightResponse])
def get_source_distribution(
    source_id: int,
    db: Session = Depends(get_db)
):
    """Получить настройки распределения для источника"""
    source = db.query(models.Source).filter(models.Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    weights = db.query(models.SourceOperatorWeight).filter(
        models.SourceOperatorWeight.source_id == source_id
    ).all()
    return weights

