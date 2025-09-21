from datetime import date
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ImportRequest(BaseModel):
    """Import request schema"""

    data_type: Literal["parts", "vehicles", "categories", "orders", "leads"] = Field(
        ...
    )
    mode: Literal["create", "update", "upsert"] = Field(default="upsert")
    validate_data: bool = Field(default=True)
    skip_errors: bool = Field(default=True)


class ImportResult(BaseModel):
    """Import result details"""

    processed_count: int = Field(ge=0)
    error_count: int = Field(ge=0)
    errors: List[str] = Field(default_factory=list)


class ImportResponse(BaseModel):
    """Import response"""

    success: bool
    message: str
    result: ImportResult


class ExportRequest(BaseModel):
    """Export request schema"""

    data_type: Literal[
        "parts", "vehicles", "categories", "orders", "leads", "all"
    ] = Field(...)
    format: Literal["csv", "xlsx", "json"] = Field(default="csv")
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    fields: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None


class ExportResponse(BaseModel):
    """Export response"""

    success: bool
    filename: str
    content_type: str
    data: Any  # Can be string or bytes
    record_count: int


class BatchOperationRequest(BaseModel):
    """Batch operation request"""

    operation_type: Literal[
        "update-status", "assign-category", "delete", "bulk-update"
    ] = Field(...)
    data_type: Literal[
        "parts", "vehicles", "categories", "orders", "leads", "users"
    ] = Field(...)
    item_ids: List[int] = Field(..., min_items=1)
    data: Optional[Dict[str, Any]] = None


class BatchOperationResponse(BaseModel):
    """Batch operation response"""

    success: bool
    message: str
    result: Dict[str, Any]


class BulkDeleteRequest(BaseModel):
    """Bulk delete request"""

    data_type: Literal[
        "parts", "vehicles", "categories", "orders", "leads", "users"
    ] = Field(...)
    item_ids: List[int] = Field(..., min_items=1)
    confirm: bool = Field(default=False)


class BulkUpdateRequest(BaseModel):
    """Bulk update request"""

    data_type: Literal[
        "parts", "vehicles", "categories", "orders", "leads", "users"
    ] = Field(...)
    item_ids: List[int] = Field(..., min_items=1)
    updates: Dict[str, Any] = Field(...)


class FileUploadResponse(BaseModel):
    """File upload response"""

    success: bool
    filename: str
    size: int
    message: str


class ValidationError(BaseModel):
    """Validation error details"""

    row: int
    field: str
    error: str
    value: Any


class ImportValidationResult(BaseModel):
    """Import validation result"""

    is_valid: bool
    total_rows: int
    valid_rows: int
    errors: List[ValidationError]


class ExportTemplate(BaseModel):
    """Export template definition"""

    data_type: str
    fields: List[str]
    sample_data: Dict[str, Any]
    required_fields: List[str]
    optional_fields: List[str]
