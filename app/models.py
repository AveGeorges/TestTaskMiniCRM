from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Operator(Base):
    """Оператор"""
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    max_load = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)

    contacts = relationship("Contact", back_populates="operator")
    source_weights = relationship("SourceOperatorWeight", back_populates="operator", cascade="all, delete-orphan")

    def get_current_load(self, db):
        from app.models import Contact
        return db.query(Contact).filter(
            Contact.operator_id == self.id,
            Contact.status == "active"
        ).count()


class Source(Base):
    """Источник"""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    contacts = relationship("Contact", back_populates="source")
    operator_weights = relationship("SourceOperatorWeight", back_populates="source", cascade="all, delete-orphan")


class SourceOperatorWeight(Base):
    """Вес оператора для конкретного источника"""
    __tablename__ = "source_operator_weights"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False)
    weight = Column(Integer, nullable=False, default=1)

    source = relationship("Source", back_populates="operator_weights")
    operator = relationship("Operator", back_populates="source_weights")


class Lead(Base):
    """Лид"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    contacts = relationship("Contact", back_populates="lead")


class Contact(Base):
    """Обращение"""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")
