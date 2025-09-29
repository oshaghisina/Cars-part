"""
Stock management models for parts inventory tracking.
"""

# from datetime import datetime  # Unused import
# from typing import Optional  # Unused import

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, JSON
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
    
    # Version tracking columns
    version = Column(Integer, nullable=False, default=1)
    updated_by = Column(String(100), nullable=True)
    lock_timestamp = Column(DateTime, nullable=True)

    # Relationships
    part = relationship("Part", back_populates="stock_level")
    version_history = relationship("StockVersion", back_populates="stock", cascade="all, delete-orphan")


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


class PartVersion(Base):
    """Version history for parts changes."""
    
    __tablename__ = "part_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    version = Column(Integer, nullable=False)
    changes = Column(JSON, nullable=False)  # Field-level changes
    changed_by = Column(String(100), nullable=True)
    change_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationship
    part = relationship("Part", back_populates="version_history")


class StockVersion(Base):
    """Version history for stock changes."""
    
    __tablename__ = "stock_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stock_levels.id"), nullable=False)
    version = Column(Integer, nullable=False)
    changes = Column(JSON, nullable=False)  # Field-level changes
    changed_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationship
    stock = relationship("StockLevel", back_populates="version_history")
