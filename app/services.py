import random
from sqlalchemy.orm import Session
from typing import Optional, List
from app import models, schemas


class DistributionService:
    """Сервис для распределения обращений между операторами"""

    @staticmethod
    def find_or_create_lead(
        db: Session,
        external_id: str,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> models.Lead:
        lead = db.query(models.Lead).filter(
            models.Lead.external_id == external_id
        ).first()

        if not lead:
            lead = models.Lead(
                external_id=external_id,
                phone=phone,
                email=email
            )
            db.add(lead)
            db.commit()
            db.refresh(lead)

        return lead

    @staticmethod
    def get_available_operators(
        db: Session,
        source_id: int
    ) -> List[models.Operator]:
        source_weights = db.query(models.SourceOperatorWeight).filter(
            models.SourceOperatorWeight.source_id == source_id
        ).all()

        if not source_weights:
            return []

        operator_ids = [sw.operator_id for sw in source_weights]
        operators = db.query(models.Operator).filter(
            models.Operator.id.in_(operator_ids),
            models.Operator.is_active == True
        ).all()

        available_operators = []
        for operator in operators:
            current_load = operator.get_current_load(db)
            if current_load < operator.max_load:
                available_operators.append(operator)

        return available_operators

    @staticmethod
    def select_operator_by_weights(
        db: Session,
        source_id: int,
        available_operators: List[models.Operator]
    ) -> Optional[models.Operator]:
        """Выбрать оператора с учетом весов (вероятностный алгоритм)"""
        if not available_operators:
            return None

        operator_weights_map = {}
        total_weight = 0

        for operator in available_operators:
            weight_obj = db.query(models.SourceOperatorWeight).filter(
                models.SourceOperatorWeight.source_id == source_id,
                models.SourceOperatorWeight.operator_id == operator.id
            ).first()

            if weight_obj:
                weight = weight_obj.weight
                operator_weights_map[operator.id] = weight
                total_weight += weight

        if total_weight == 0:
            return random.choice(available_operators)

        random_value = random.uniform(0, total_weight)
        cumulative = 0

        for operator in available_operators:
            weight = operator_weights_map.get(operator.id, 0)
            cumulative += weight
            if random_value <= cumulative:
                return operator

        return available_operators[0]

    @staticmethod
    def distribute_contact(
        db: Session,
        contact_data: schemas.ContactCreate
    ) -> models.Contact:
        """
        Распределить обращение:
        1. Найти/создать лида
        2. Найти доступных операторов
        3. Выбрать оператора по весам
        4. Создать обращение
        """
        lead = DistributionService.find_or_create_lead(
            db=db,
            external_id=contact_data.external_id,
            phone=contact_data.phone,
            email=contact_data.email
        )

        available_operators = DistributionService.get_available_operators(
            db=db,
            source_id=contact_data.source_id
        )

        operator = None
        if available_operators:
            operator = DistributionService.select_operator_by_weights(
                db=db,
                source_id=contact_data.source_id,
                available_operators=available_operators
            )

        contact = models.Contact(
            lead_id=lead.id,
            source_id=contact_data.source_id,
            operator_id=operator.id if operator else None,
            status=schemas.ContactStatus.ACTIVE
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)

        return contact
