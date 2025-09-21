"""SQLAlchemy models based on data-model.md specifications."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, DECIMAL, Float, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import json
import hashlib
import secrets


class Part(Base):
    """Parts table - Core part definitions."""
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    part_name = Column(String(255), nullable=False, index=True)
    brand_oem = Column(String(100), nullable=False)
    vehicle_make = Column(String(100), nullable=False)
    vehicle_model = Column(String(100), nullable=False, index=True)
    vehicle_trim = Column(String(100), nullable=True)
    model_year_from = Column(Integer, nullable=True)
    model_year_to = Column(Integer, nullable=True)
    engine_code = Column(String(50), nullable=True)
    position = Column(String(50), nullable=True)
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100), nullable=True)
    category_id = Column(Integer, ForeignKey(
        "part_categories.id"), nullable=True)
    oem_code = Column(String(100), nullable=True, index=True)
    alt_codes = Column(Text, nullable=True)
    dimensions_specs = Column(Text, nullable=True)
    compatibility_notes = Column(Text, nullable=True)
    unit = Column(String(20), nullable=False, default='pcs')
    pack_size = Column(Integer, nullable=True, default=1)
    status = Column(String(20), nullable=False, default='active', index=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now())

    # Relationships
    prices = relationship("Price", back_populates="part")
    synonyms = relationship("Synonym", back_populates="part")
    order_items = relationship("OrderItem", back_populates="matched_part")
    category_obj = relationship("PartCategory", back_populates="parts")
    specifications = relationship(
        "PartSpecification",
        back_populates="part",
        cascade="all, delete-orphan")
    images = relationship(
        "PartImage",
        back_populates="part",
        cascade="all, delete-orphan")


class Price(Base):
    """Prices table - Multiple price points per part."""
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(
        Integer,
        ForeignKey("parts.id"),
        nullable=False,
        index=True)
    seller_name = Column(String(255), nullable=False)
    seller_url = Column(String(500), nullable=True)
    currency = Column(String(3), nullable=False, default='IRR')
    price = Column(DECIMAL(12, 2), nullable=False)
    min_order_qty = Column(Integer, nullable=True, default=1)
    available_qty = Column(Integer, nullable=True)
    warranty = Column(String(100), nullable=True)
    source_type = Column(String(20), nullable=False, default='manual')
    scraped_at = Column(DateTime, nullable=True)
    valid_from = Column(Date, nullable=True, index=True)
    valid_to = Column(Date, nullable=True, index=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    part = relationship("Part", back_populates="prices")


class Synonym(Base):
    """Synonyms table - Keywords and aliases for search."""
    __tablename__ = "synonyms"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(
        Integer,
        ForeignKey("parts.id"),
        nullable=True,
        index=True)
    keyword = Column(String(255), nullable=False, index=True)
    lang = Column(String(2), nullable=False, default='fa', index=True)
    weight = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    part = relationship("Part", back_populates="synonyms")


class Lead(Base):
    """Leads table - Customer information."""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_e164 = Column(String(20), nullable=False, unique=True, index=True)
    city = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    consent = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now())

    # Relationships
    orders = relationship("Order", back_populates="lead")


class Order(Base):
    """Orders table - Formal purchase requests."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(
        Integer,
        ForeignKey("leads.id"),
        nullable=False,
        index=True)
    status = Column(String(20), nullable=False, default='new', index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        index=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """Order items table - Individual line items within orders."""
    __tablename__ = "order_items"

    order_id = Column(Integer, ForeignKey("orders.id"), primary_key=True)
    line_no = Column(Integer, primary_key=True)
    query_text = Column(Text, nullable=False)
    matched_part_id = Column(
        Integer,
        ForeignKey("parts.id"),
        nullable=True,
        index=True)
    qty = Column(Integer, nullable=False, default=1)
    unit = Column(String(20), nullable=False, default='pcs')
    notes = Column(Text, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    matched_part = relationship("Part", back_populates="order_items")


class Setting(Base):
    """Settings table - System configuration and feature flags."""
    __tablename__ = "settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class User(Base):
    """Users table - System users with authentication and profile information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(32), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(
        String(20),
        nullable=False,
        index=True,
        default='user')  # Simple role field
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=False, default=func.now())
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now())

    # Profile information
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default='UTC', nullable=False)
    language = Column(String(10), default='en', nullable=False)
    preferences = Column(JSON, nullable=True)  # User preferences as JSON

    def set_password(self, password: str) -> None:
        """Set password with salt and hash."""
        self.salt = secrets.token_hex(16)
        self.password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            self.salt.encode('utf-8'),
            100000
        ).hex()
        self.password_changed_at = func.now()

    def check_password(self, password: str) -> bool:
        """Check password against hash."""
        if not self.password_hash or not self.salt:
            return False
        hash_to_check = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            self.salt.encode('utf-8'),
            100000
        ).hex()
        return hash_to_check == self.password_hash

    def get_full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return self.role == role_name

    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission based on role."""
        # Simple permission mapping for now
        role_permissions = {
            'super_admin': ['*'],  # All permissions
            'admin': ['users.read', 'users.create', 'users.update', 'users.delete',
                      'parts.read', 'parts.create', 'parts.update', 'parts.delete',
                      'orders.read', 'orders.create', 'orders.update', 'orders.delete',
                      'leads.read', 'leads.create', 'leads.update', 'leads.delete'],
            'manager': ['users.read', 'parts.read', 'parts.create', 'parts.update',
                        'orders.read', 'orders.create', 'orders.update',
                        'leads.read', 'leads.create', 'leads.update'],
            'user': ['parts.read', 'orders.read', 'leads.read']
        }

        permissions = role_permissions.get(self.role, [])
        return '*' in permissions or permission_name in permissions

    def is_locked(self) -> bool:
        """Check if user account is locked."""
        if not self.locked_until:
            return False
        return self.locked_until > func.now()

    def increment_login_attempts(self) -> None:
        """Increment login attempts and lock account if necessary."""
        self.login_attempts += 1
        if self.login_attempts >= 5:  # Lock after 5 failed attempts
            from datetime import datetime, timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)

    def reset_login_attempts(self) -> None:
        """Reset login attempts and unlock account."""
        self.login_attempts = 0
        self.locked_until = None


class WizardSession(Base):
    """Wizard sessions table - Stores wizard state and data."""
    __tablename__ = "wizard_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    state = Column(String(50), nullable=False)
    vehicle_data = Column(Text, nullable=True)  # JSON string
    part_data = Column(Text, nullable=True)     # JSON string
    contact_data = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now())

    def get_vehicle_data(self):
        """Parse vehicle data from JSON string."""
        if self.vehicle_data is not None:
            return json.loads(self.vehicle_data)  # type: ignore[arg-type]
        return {}

    def set_vehicle_data(self, data):
        """Store vehicle data as JSON string."""
        self.vehicle_data = json.dumps(data) if data else None

    def get_part_data(self):
        """Parse part data from JSON string."""
        if self.part_data is not None:
            return json.loads(self.part_data)  # type: ignore[arg-type]
        return {}

    def set_part_data(self, data):
        """Store part data as JSON string."""
        self.part_data = json.dumps(data) if data else None

    def get_contact_data(self):
        """Parse contact data from JSON string."""
        if self.contact_data is not None:
            return json.loads(self.contact_data)  # type: ignore[arg-type]
        return {}

    def set_contact_data(self, data):
        """Store contact data as JSON string."""
        self.contact_data = json.dumps(data) if data else None


# Enhanced Vehicle Models
class VehicleBrand(Base):
    """Vehicle brands/manufacturers table."""
    __tablename__ = "vehicle_brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    name_fa = Column(String(100), nullable=True)  # Persian name
    name_cn = Column(String(100), nullable=True)  # Chinese name
    logo_url = Column(String(500), nullable=True)
    country = Column(String(50), nullable=True)
    website = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now())

    # Relationships
    models = relationship(
        "VehicleModel",
        back_populates="brand",
        cascade="all, delete-orphan")


class VehicleModel(Base):
    """Vehicle models table."""
    __tablename__ = "vehicle_models"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("vehicle_brands.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    name_fa = Column(String(100), nullable=True)  # Persian name
    name_cn = Column(String(100), nullable=True)  # Chinese name
    generation = Column(String(50), nullable=True)  # e.g., "First Generation"
    # SUV, Sedan, Hatchback, etc.
    body_type = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now())

    # Relationships
    brand = relationship("VehicleBrand", back_populates="models")
    trims = relationship(
        "VehicleTrim",
        back_populates="model",
        cascade="all, delete-orphan")


class VehicleTrim(Base):
    """Vehicle trims/variants table."""
    __tablename__ = "vehicle_trims"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("vehicle_models.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    name_fa = Column(String(100), nullable=True)  # Persian name
    trim_code = Column(String(50), nullable=True)  # Internal trim code
    engine_type = Column(String(100), nullable=True)  # e.g., "1.6L Turbo"
    engine_code = Column(String(50), nullable=True)  # e.g., "SQRF4J16"
    transmission = Column(String(50), nullable=True)  # Manual, Automatic, CVT
    drivetrain = Column(String(50), nullable=True)  # FWD, RWD, AWD, 4WD
    # Gasoline, Diesel, Hybrid, Electric
    fuel_type = Column(String(50), nullable=True)
    year_from = Column(Integer, nullable=True)
    year_to = Column(Integer, nullable=True)
    specifications = Column(JSON, nullable=True)  # Additional specs as JSON
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now())

    # Relationships
    model = relationship("VehicleModel", back_populates="trims")


# Enhanced Parts Categories
class PartCategory(Base):
    """Hierarchical parts categories table."""
    __tablename__ = "part_categories"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(
        Integer,
        ForeignKey("part_categories.id"),
        nullable=True)
    name = Column(String(100), nullable=False, index=True)
    name_fa = Column(String(100), nullable=True)  # Persian name
    name_cn = Column(String(100), nullable=True)  # Chinese name
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)  # Icon class or URL
    color = Column(String(7), nullable=True)  # Hex color code
    # Category level (0=root, 1=sub, 2=sub-sub)
    level = Column(Integer, default=0)
    # Full path like "/Engine/Engine Parts/Filters"
    path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now())

    # Relationships
    children = relationship("PartCategory", backref="parent", remote_side=[id])
    parts = relationship("Part", back_populates="category_obj")


class PartSpecification(Base):
    """Part specifications and attributes table."""
    __tablename__ = "part_specifications"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    # e.g., "Length", "Material", "Weight"
    spec_name = Column(String(100), nullable=False)
    # e.g., "120mm", "Steel", "2.5kg"
    spec_value = Column(String(200), nullable=False)
    spec_unit = Column(String(20), nullable=True)  # e.g., "mm", "kg", "V"
    # text, number, boolean, enum
    spec_type = Column(String(20), default="text")
    is_required = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    part = relationship("Part", back_populates="specifications")


class PartImage(Base):
    """Part images table."""
    __tablename__ = "part_images"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    # main, thumbnail, detail, installation
    image_type = Column(String(20), default="main")
    alt_text = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    part = relationship("Part", back_populates="images")
