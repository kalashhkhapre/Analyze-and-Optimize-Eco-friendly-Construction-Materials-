# server/models.py

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    material = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    source = Column(String, nullable=False)
    carbon_savings = Column(Float, nullable=False)
    project_location = Column(String, nullable=False)
    used_in_project = Column(String, nullable=False)
    date_added = Column(String, nullable=False)
    actual_usage = Column(Integer, nullable=True)
