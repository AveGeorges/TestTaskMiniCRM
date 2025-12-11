from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/operators", tags=["operators"])


@router.post("/", response_model=schemas.OperatorResponse)
def create_operator(
    operator: schemas.OperatorCreate,
    db: Session = Depends(get_db)
):
    """Создать оператора"""
    db_operator = models.Operator(**operator.dict())
    db.add(db_operator)
    db.commit()
    db.refresh(db_operator)
    return db_operator


@router.get("/", response_model=List[schemas.OperatorResponse])
def get_operators(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список операторов"""
    operators = db.query(models.Operator).offset(skip).limit(limit).all()
    result = []
    for op in operators:
        op_dict = schemas.OperatorResponse.model_validate(op).model_dump()
        op_dict["current_load"] = op.get_current_load(db)
        result.append(op_dict)
    return result


@router.get("/{operator_id}", response_model=schemas.OperatorResponse)
def get_operator(
    operator_id: int,
    db: Session = Depends(get_db)
):
    """Получить оператора по ID"""
    operator = db.query(models.Operator).filter(models.Operator.id == operator_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    result = schemas.OperatorResponse.model_validate(operator).model_dump()
    result["current_load"] = operator.get_current_load(db)
    return result


@router.patch("/{operator_id}", response_model=schemas.OperatorResponse)
def update_operator(
    operator_id: int,
    operator_update: schemas.OperatorUpdate,
    db: Session = Depends(get_db)
):
    """Обновить оператора (активность, лимит нагрузки)"""
    operator = db.query(models.Operator).filter(models.Operator.id == operator_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")

    update_data = operator_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(operator, field, value)

    db.commit()
    db.refresh(operator)
    result = schemas.OperatorResponse.model_validate(operator).model_dump()
    result["current_load"] = operator.get_current_load(db)
    return result


@router.delete("/{operator_id}")
def delete_operator(
    operator_id: int,
    db: Session = Depends(get_db)
):
    """Удалить оператора"""
    operator = db.query(models.Operator).filter(models.Operator.id == operator_id).first()
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    db.delete(operator)
    db.commit()
    return {"message": "Operator deleted"}

