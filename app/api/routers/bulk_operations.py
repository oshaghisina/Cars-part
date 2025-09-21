from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
import pandas as pd
import json
import io
from datetime import datetime

from app.db.database import get_db
from app.db.models import Part, VehicleBrand, VehicleModel, VehicleTrim, PartCategory, Order, Lead, User
from app.schemas.bulk_schemas import (
    ImportRequest, ImportResponse, ImportResult,
    ExportRequest, ExportResponse,
    BatchOperationRequest, BatchOperationResponse
)

router = APIRouter()


@router.post("/import", response_model=ImportResponse)
async def bulk_import(
    file: UploadFile = File(...),
    data_type: str = Form(...),
    mode: str = Form("upsert"),
    validate_data: bool = Form(True),
    skip_errors: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Import data from uploaded file
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.json')):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format")

        # Read file content
        content = await file.read()

        # Parse file based on extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(content))
        elif file.filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
            df = pd.DataFrame(data)

        # Process import based on data type
        result = await process_import(df, data_type, mode, validate_data, skip_errors, db)

        return ImportResponse(
            success=True,
            message=f"Successfully imported {result.processed_count}" records",
            result=result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}"")


@router.post("/export", response_model=ExportResponse)
async def bulk_export(
    export_request: ExportRequest,
    db: Session = Depends(get_db)
):
    """
    Export data to specified format
    """
    try:
        # Get data based on request
        data = await get_export_data(export_request, db)

        # Convert to requested format
        if export_request.format == 'csv':
            output = data.to_csv(index=False)
            content_type = 'text/csv'
            filename = f"{export_request.data_type}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}".csv"
        elif export_request.format == 'xlsx':
            output = io.BytesIO()
            data.to_excel(output, index=False)
            output.seek(0)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f"{
                export_request.data_type}_export_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        elif export_request.format == 'json':
            output = data.to_json(orient='records', date_format='iso')
            content_type = 'application/json'
            filename = f"{
                export_request.data_type}_export_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported export format")

        return ExportResponse(
            success=True,
            filename=filename,
            content_type=content_type,
            data=output if isinstance(output, str) else output.getvalue(),
            record_count=len(data)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}"")


@router.post("/batch", response_model=BatchOperationResponse)
async def batch_operation(
    operation_request: BatchOperationRequest,
    db: Session = Depends(get_db)
):
    """
    Perform batch operations on selected items
    """
    try:
        result = await process_batch_operation(operation_request, db)

        return BatchOperationResponse(
            success=True,
            message=f"Successfully processed {result.processed_count}" items",
            result=result
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch operation error: {str(e)}")


async def process_import(
        df: pd.DataFrame,
        data_type: str,
        mode: str,
        validate_data: bool,
        skip_errors: bool,
        db: Session):
    """Process import data"""
    processed_count = 0
    error_count = 0
    errors = []

    try:
        if data_type == 'parts':
            processed_count, error_count, errors = await import_parts(df, mode, validate_data, skip_errors, db)
        elif data_type == 'vehicles':
            processed_count, error_count, errors = await import_vehicles(df, mode, validate_data, skip_errors, db)
        elif data_type == 'categories':
            processed_count, error_count, errors = await import_categories(df, mode, validate_data, skip_errors, db)
        elif data_type == 'orders':
            processed_count, error_count, errors = await import_orders(df, mode, validate_data, skip_errors, db)
        elif data_type == 'leads':
            processed_count, error_count, errors = await import_leads(df, mode, validate_data, skip_errors, db)
        else:
            raise ValueError(f"Unsupported data type: {data_type}"")

        db.commit()

    except Exception as e:
        db.rollback()
        raise e

    return ImportResult(
        processed_count=processed_count,
        error_count=error_count,
        errors=errors[:10] if len(
            errors) > 10 else errors  # Limit error details
    )


async def import_parts(
        df: pd.DataFrame,
        mode: str,
        validate_data: bool,
        skip_errors: bool,
        db: Session):
    """Import parts data"""
    processed_count = 0
    error_count = 0
    errors = []

    required_columns = ['part_name', 'brand_oem', 'oem_code']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Missing required columns: {required_columns}"")

    for index, row in df.iterrows():
        try:
            # Validate data if requested
            if validate_data:
                if pd.isna(row['part_name']) or pd.isna(row['brand_oem']):
                    raise ValueError("Required fields cannot be empty")

            # Check if part exists
            existing_part = db.query(Part).filter(
                Part.oem_code == row['oem_code']).first()

            if existing_part and mode == 'create':
                if skip_errors:
                    errors.append(
                        f"Row {
                            index +
                            1}: Part with OEM code {
                            row['oem_code']} already exists")
                    error_count += 1
                    continue
                else:
                    raise ValueError(
                        f"Part with OEM code {
                            row['oem_code']} already exists")

            # Create or update part
            if existing_part and mode in ['update', 'upsert']:
                # Update existing part
                for col, value in row.items():
                    if hasattr(existing_part, col) and not pd.isna(value):
                        setattr(existing_part, col, value)
            else:
                # Create new part
                part_data = {col: value for col,
                             value in row.items() if not pd.isna(value)}
                new_part = Part(**part_data)
                db.add(new_part)

            processed_count += 1

        except Exception as e:
            error_count += 1
            errors.append(f"Row {index + 1}: {str(e)}"")
            if not skip_errors:
                raise e

    return processed_count, error_count, errors


async def import_vehicles(
        df: pd.DataFrame,
        mode: str,
        validate_data: bool,
        skip_errors: bool,
        db: Session):
    """Import vehicles data"""
    processed_count = 0
    error_count = 0
    errors = []

    for index, row in df.iterrows():
        try:
            if 'brand_name' in row and not pd.isna(row['brand_name']):
                # Import brand
                existing_brand = db.query(VehicleBrand).filter(
                    VehicleBrand.name == row['brand_name']).first()

                if existing_brand and mode == 'create':
                    if skip_errors:
                        errors.append(
                            f"Row {
                                index +
                                1}: Brand {
                                row['brand_name']} already exists")
                        error_count += 1
                        continue
                else:
                    if not existing_brand:
                        new_brand = VehicleBrand(name=row['brand_name'])
                        db.add(new_brand)
                        processed_count += 1

            # Import model if specified
            if 'model_name' in row and not pd.isna(row['model_name']):
                brand = db.query(VehicleBrand).filter(
                    VehicleBrand.name == row['brand_name']).first()
                if brand:
                    existing_model = db.query(VehicleModel).filter(
                        VehicleModel.name == row['model_name'],
                        VehicleModel.brand_id == brand.id
                    ).first()

                    if not existing_model:
                        new_model = VehicleModel(
                            name=row['model_name'],
                            brand_id=brand.id
                        )
                        db.add(new_model)
                        processed_count += 1

        except Exception as e:
            error_count += 1
            errors.append(f"Row {index + 1}: {str(e)}"")
            if not skip_errors:
                raise e

    return processed_count, error_count, errors


async def import_categories(
        df: pd.DataFrame,
        mode: str,
        validate_data: bool,
        skip_errors: bool,
        db: Session):
    """Import categories data"""
    processed_count = 0
    error_count = 0
    errors = []

    for index, row in df.iterrows():
        try:
            if pd.isna(row.get('name')):
                raise ValueError("Category name is required")

            existing_category = db.query(PartCategory).filter(
                PartCategory.name == row['name']).first()

            if existing_category and mode == 'create':
                if skip_errors:
                    errors.append(
                        f"Row {
                            index +
                            1}: Category {
                            row['name']} already exists")
                    error_count += 1
                    continue
            else:
                if not existing_category:
                    category_data = {
                        'name': row['name'], 'description': row.get(
                            'description', ''), 'parent_id': row.get('parent_id') if not pd.isna(
                            row.get('parent_id')) else None}
                    new_category = PartCategory(**category_data)
                    db.add(new_category)
                    processed_count += 1

        except Exception as e:
            error_count += 1
            errors.append(f"Row {index + 1}: {str(e)}"")
            if not skip_errors:
                raise e

    return processed_count, error_count, errors


async def import_orders(
        df: pd.DataFrame,
        mode: str,
        validate_data: bool,
        skip_errors: bool,
        db: Session):
    """Import orders data"""
    processed_count = 0
    error_count = 0
    errors = []

    for index, row in df.iterrows():
        try:
            if validate_data:
                required_fields = ['customer_name', 'customer_phone']
                for field in required_fields:
                    if field not in row or pd.isna(row[field]):
                        raise ValueError(f"Required field {field}" is missing")

            order_data = {
                'customer_name': row['customer_name'],
                'customer_phone': row['customer_phone'],
                'status': row.get('status', 'pending'),
                'total': row.get('total', 0),
                'notes': row.get('notes', '')
            }

            new_order = Order(**order_data)
            db.add(new_order)
            processed_count += 1

        except Exception as e:
            error_count += 1
            errors.append(f"Row {index + 1}: {str(e)}"")
            if not skip_errors:
                raise e

    return processed_count, error_count, errors


async def import_leads(
        df: pd.DataFrame,
        mode: str,
        validate_data: bool,
        skip_errors: bool,
        db: Session):
    """Import leads data"""
    processed_count = 0
    error_count = 0
    errors = []

    for index, row in df.iterrows():
        try:
            if validate_data:
                required_fields = ['first_name', 'last_name', 'phone_e164']
                for field in required_fields:
                    if field not in row or pd.isna(row[field]):
                        raise ValueError(f"Required field {field}" is missing")

            lead_data = {
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'phone_e164': row['phone_e164'],
                'city': row.get('city', ''),
                'notes': row.get('notes', ''),
                'consent': row.get('consent', True)
            }

            new_lead = Lead(**lead_data)
            db.add(new_lead)
            processed_count += 1

        except Exception as e:
            error_count += 1
            errors.append(f"Row {index + 1}: {str(e)}"")
            if not skip_errors:
                raise e

    return processed_count, error_count, errors


async def get_export_data(export_request: ExportRequest, db: Session):
    """Get data for export"""
    if export_request.data_type == 'parts':
        query = db.query(Part)
        if export_request.date_from:
            query = query.filter(Part.created_at >= export_request.date_from)
        if export_request.date_to:
            query = query.filter(Part.created_at <= export_request.date_to)
        parts = query.all()

        data = []
        for part in parts:
            data.append({
                'id': part.id,
                'part_name': part.part_name,
                'brand_oem': part.brand_oem,
                'oem_code': part.oem_code,
                'description': part.description,
                'price': part.price,
                'status': part.status,
                'category': part.category.name if part.category else None,
                'created_at': part.created_at.isoformat() if part.created_at else None
            })

        return pd.DataFrame(data)

    elif export_request.data_type == 'vehicles':
        brands = db.query(VehicleBrand).all()
        data = []
        for brand in brands:
            for model in brand.models:
                data.append({
                    'brand_name': brand.name,
                    'model_name': model.name,
                    'year_from': model.year_from,
                    'year_to': model.year_to
                })

        return pd.DataFrame(data)

    # Add other data types as needed

    return pd.DataFrame()


async def process_batch_operation(
        operation_request: BatchOperationRequest,
        db: Session):
    """Process batch operation"""
    processed_count = 0
    errors = []

    try:
        if operation_request.operation_type == 'update-status':
            for item_id in operation_request.item_ids:
                try:
                    # Update status based on data type
                    if operation_request.data_type == 'parts':
                        item = db.query(Part).filter(
                            Part.id == item_id).first()
                    elif operation_request.data_type == 'orders':
                        item = db.query(Order).filter(
                            Order.id == item_id).first()
                    # Add other types as needed

                    if item and hasattr(item, 'status'):
                        item.status = operation_request.data['status']
                        processed_count += 1

                except Exception as e:
                    errors.append(f"Item {item_id}: {str(e)}"")

        elif operation_request.operation_type == 'assign-category':
            for item_id in operation_request.item_ids:
                try:
                    if operation_request.data_type == 'parts':
                        item = db.query(Part).filter(
                            Part.id == item_id).first()
                        if item:
                            item.category_id = operation_request.data['category_id']
                            processed_count += 1

                except Exception as e:
                    errors.append(f"Item {item_id}: {str(e)}"")

        elif operation_request.operation_type == 'delete':
            for item_id in operation_request.item_ids:
                try:
                    if operation_request.data_type == 'parts':
                        item = db.query(Part).filter(
                            Part.id == item_id).first()
                    elif operation_request.data_type == 'orders':
                        item = db.query(Order).filter(
                            Order.id == item_id).first()
                    # Add other types as needed

                    if item:
                        db.delete(item)
                        processed_count += 1

                except Exception as e:
                    errors.append(f"Item {item_id}: {str(e)}"")

        db.commit()

    except Exception as e:
        db.rollback()
        raise e

    return {
        'processed_count': processed_count,
        'error_count': len(errors),
        'errors': errors
    }
