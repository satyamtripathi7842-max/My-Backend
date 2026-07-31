"""
database.py
SQLAlchemy models + session management for SentinelX-AI.
Uses SQLite by default (file: sentinelx.db). Swap DATABASE_URL for Postgres in prod.
"""

import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///./sentinelx.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="analyst")  # analyst | admin
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    category = Column(String, default="general")
    lat = Column(Float, default=0.0)
    lng = Column(Float, default=0.0)
    financial_health = Column(Float, default=70.0)     # 0-100
    delivery_delay_days = Column(Float, default=0.0)    # avg delay
    geopolitical_risk = Column(Float, default=20.0)     # 0-100
    news_sentiment = Column(Float, default=0.0)         # -1..1
    risk_score = Column(Float, default=0.0)             # computed, 0-100
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

    alerts = relationship("Alert", back_populates="supplier")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    severity = Column(String, default="medium")  # low | medium | high | critical
    message = Column(Text, nullable=False)
    recommendation = Column(Text, default="")
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    supplier = relationship("Supplier", back_populates="alerts")


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    scenario = Column(String, nullable=False)
    disruption_pct = Column(Float, default=0.0)
    projected_impact_score = Column(Float, default=0.0)
    summary = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
