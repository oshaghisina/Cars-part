"""SMS-related database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, DECIMAL, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base


class SMSTemplate(Base):
    """SMS template model for storing message templates."""

    __tablename__ = "sms_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    template_type = Column(String(50), nullable=False, index=True)  # order_confirmation, stock_alert, etc.
    content_en = Column(Text, nullable=True)  # English content
    content_fa = Column(Text, nullable=True)  # Persian content
    variables = Column(JSON, nullable=True)  # Template variables like {order_id}, {customer_name}
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships (commented out to avoid circular import issues)
    # sms_logs = relationship("SMSLog", back_populates="template")


class SMSLog(Base):
    """SMS log model for tracking sent messages."""

    __tablename__ = "sms_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient_phone = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=False)
    template_id = Column(Integer, ForeignKey("sms_templates.id"), nullable=True)
    status = Column(String(20), default="pending", nullable=False, index=True)  # pending, sent, delivered, failed
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    cost = Column(DECIMAL(10, 4), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships (commented out to avoid circular import issues)
    # template = relationship("SMSTemplate", back_populates="sms_logs")


class StockAlert(Base):
    """Stock alert model for tracking customer stock notifications."""

    __tablename__ = "stock_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    phone_number = Column(String(20), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_notified = Column(Boolean, default=False, nullable=False)
    notified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships (commented out to avoid circular import issues)
    # user = relationship("User", back_populates="stock_alerts")
    # part = relationship("Part", back_populates="stock_alerts")


class SMSCampaign(Base):
    """SMS campaign model for marketing campaigns."""

    __tablename__ = "sms_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    template_id = Column(Integer, ForeignKey("sms_templates.id"), nullable=False)
    target_audience = Column(String(50), nullable=False)  # all, registered, pro, etc.
    status = Column(String(20), default="draft", nullable=False)  # draft, scheduled, running, completed, cancelled
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    total_recipients = Column(Integer, default=0, nullable=False)
    sent_count = Column(Integer, default=0, nullable=False)
    delivered_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    total_cost = Column(DECIMAL(10, 4), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships (commented out to avoid circular import issues)
    # template = relationship("SMSTemplate")


class SMSDeliveryReport(Base):
    """SMS delivery report model for tracking delivery status."""

    __tablename__ = "sms_delivery_reports"

    id = Column(Integer, primary_key=True, index=True)
    sms_log_id = Column(Integer, ForeignKey("sms_logs.id"), nullable=False)
    external_id = Column(String(100), nullable=True, index=True)  # Melipayamak message ID
    status = Column(String(20), nullable=False, index=True)  # delivered, failed, pending
    status_code = Column(String(10), nullable=True)
    status_message = Column(Text, nullable=True)
    delivery_time = Column(DateTime, nullable=True)
    cost = Column(DECIMAL(10, 4), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships (commented out to avoid circular import issues)
    # sms_log = relationship("SMSLog")
