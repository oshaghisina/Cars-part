"""
Stock management models for parts inventory tracking.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class StockLevel(Base):
    """Stock level tracking for parts."""
    
    __tablename__ = "stock_levels"
    
    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, unique=True)
    current_stock = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    min_stock_level = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    part = relationship("Part", back_populates="stock_level")


class PartPrice(Base):
    """Pricing information for parts."""
    
    __tablename__ = "prices_new"  # New normalized prices table
    
    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    list_price = Column(String, nullable=False)  # Store as string to avoid precision issues
    sale_price = Column(String, nullable=True)
    currency = Column(String, nullable=False, default="IRR")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    part = relationship("Part", back_populates="price_info")
