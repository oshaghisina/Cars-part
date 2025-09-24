"""
Image Management API Router
Handles image upload, processing, optimization, and serving for product images.
"""

import uuid
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from PIL import Image, ImageOps
import aiofiles

from app.db.database import get_db
from app.db.models import Part, PartImage, User
from app.api.dependencies import require_permission

router = APIRouter(prefix="/images", tags=["Image Management"])

# Configuration
UPLOAD_DIR = Path("uploads/images")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
IMAGE_SIZES = {
    "thumbnail": (150, 150),
    "small": (300, 300),
    "medium": (600, 600),
    "large": (1200, 1200),
    "xlarge": (1600, 1600),
}

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file."""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: "
            f"{', '.join(ALLOWED_EXTENSIONS)}",
        )


def generate_filename(original_filename: str, part_id: int, image_type: str = "main") -> str:
    """Generate unique filename for uploaded image."""
    file_ext = Path(original_filename).suffix.lower()
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"part_{part_id}_{image_type}_{timestamp}_{unique_id}{file_ext}"


def optimize_image(image_path: Path, max_size: tuple = (1200, 1200), quality: int = 85) -> None:
    """Optimize image for web usage."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background

            # Auto-orient based on EXIF data
            img = ImageOps.exif_transpose(img)

            # Resize if too large
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save optimized image
            img.save(image_path, format="JPEG", quality=quality, optimize=True, progressive=True)
    except Exception as e:
        print(f"Error optimizing image {image_path}: {e}")


def create_thumbnails(original_path: Path, part_id: int, image_type: str) -> Dict[str, str]:
    """Create multiple sized thumbnails from original image."""
    thumbnails = {}

    try:
        with Image.open(original_path) as img:
            # Convert to RGB if necessary
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background

            # Auto-orient based on EXIF data
            img = ImageOps.exif_transpose(img)

            for size_name, dimensions in IMAGE_SIZES.items():
                # Create thumbnail
                thumb = img.copy()
                thumb.thumbnail(dimensions, Image.Resampling.LANCZOS)

                # Generate filename
                thumb_filename = (
                    f"part_{part_id}_{image_type}_{size_name}_" f"{uuid.uuid4().hex[:8]}.jpg"
                )
                thumb_path = UPLOAD_DIR / thumb_filename

                # Save thumbnail
                thumb.save(thumb_path, format="JPEG", quality=85, optimize=True)

                thumbnails[size_name] = thumb_filename

    except Exception as e:
        print(f"Error creating thumbnails for {original_path}: {e}")

    return thumbnails


@router.post("/upload/{part_id}")
async def upload_part_image(
    part_id: int,
    file: UploadFile = File(...),
    image_type: str = Form("main", description="Image type: main, detail, installation, 360"),
    alt_text: Optional[str] = Form(None, description="Alt text for accessibility"),
    sort_order: int = Form(0, description="Display order"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("parts.update")),
):
    """Upload and process product image."""

    # Validate file
    validate_image_file(file)

    # Check if part exists
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")

    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    try:
        # Generate filename and save original
        filename = generate_filename(file.filename, part_id, image_type)
        file_path = UPLOAD_DIR / filename

        # Save uploaded file
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)

        # Optimize original image
        optimize_image(file_path)

        # Create thumbnails
        thumbnails = create_thumbnails(file_path, part_id, image_type)

        # Create database record
        part_image = PartImage(
            part_id=part_id,
            image_url=f"/api/v1/images/serve/{filename}",
            image_type=image_type,
            alt_text=alt_text or f"{part.part_name} - {image_type}",
            sort_order=sort_order,
            is_active=True,
        )

        db.add(part_image)
        db.commit()
        db.refresh(part_image)

        # Return response with thumbnail URLs
        thumbnail_urls = {
            size: f"/api/v1/images/serve/{thumb_filename}"
            for size, thumb_filename in thumbnails.items()
        }

        return {
            "id": part_image.id,
            "url": part_image.image_url,
            "thumbnails": thumbnail_urls,
            "type": image_type,
            "alt_text": part_image.alt_text,
            "sort_order": sort_order,
            "created_at": part_image.created_at,
            "message": "Image uploaded and processed successfully",
        }

    except Exception as e:
        # Clean up files on error
        if file_path.exists():
            file_path.unlink()
        for thumb_filename in thumbnails.values():
            thumb_path = UPLOAD_DIR / thumb_filename
            if thumb_path.exists():
                thumb_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}",
        )


@router.get("/serve/{filename}")
async def serve_image(filename: str):
    """Serve image file with proper headers."""
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    # Determine content type
    file_ext = file_path.suffix.lower()
    content_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    content_type = content_types.get(file_ext, "application/octet-stream")

    return FileResponse(
        file_path,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=31536000",  # 1 year
            "ETag": f'"{filename}"',
        },
    )


@router.get("/part/{part_id}")
async def get_part_images(
    part_id: int,
    image_type: Optional[str] = Query(None, description="Filter by image type"),
    include_thumbnails: bool = Query(True, description="Include thumbnail URLs"),
    db: Session = Depends(get_db),
):
    """Get all images for a specific part."""

    query = db.query(PartImage).filter(PartImage.part_id == part_id, PartImage.is_active)

    if image_type:
        query = query.filter(PartImage.image_type == image_type)

    images = query.order_by(PartImage.sort_order, PartImage.created_at).all()

    result = []
    for img in images:
        image_data = {
            "id": img.id,
            "url": img.image_url,
            "type": img.image_type,
            "alt_text": img.alt_text,
            "sort_order": img.sort_order,
            "created_at": img.created_at,
        }

        if include_thumbnails:
            # Generate thumbnail URLs based on original filename
            base_filename = Path(img.image_url).stem
            thumbnails = {}
            for size_name in IMAGE_SIZES.keys():
                thumb_filename = f"{base_filename}_{size_name}.jpg"
                thumb_path = UPLOAD_DIR / thumb_filename
                if thumb_path.exists():
                    thumbnails[size_name] = f"/api/v1/images/serve/{thumb_filename}"

            image_data["thumbnails"] = thumbnails

        result.append(image_data)

    return result


@router.put("/{image_id}")
async def update_part_image(
    image_id: int,
    image_type: Optional[str] = Form(None),
    alt_text: Optional[str] = Form(None),
    sort_order: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("parts.update")),
):
    """Update part image metadata."""

    image = db.query(PartImage).filter(PartImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    # Update fields
    if image_type is not None:
        image.image_type = image_type
    if alt_text is not None:
        image.alt_text = alt_text
    if sort_order is not None:
        image.sort_order = sort_order
    if is_active is not None:
        image.is_active = is_active

    db.commit()
    db.refresh(image)

    return {
        "id": image.id,
        "url": image.image_url,
        "type": image.image_type,
        "alt_text": image.alt_text,
        "sort_order": image.sort_order,
        "is_active": image.is_active,
        "message": "Image updated successfully",
    }


@router.delete("/{image_id}")
async def delete_part_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("parts.delete")),
):
    """Delete part image and associated files."""

    image = db.query(PartImage).filter(PartImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    try:
        # Delete physical files
        filename = Path(image.image_url).name
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            file_path.unlink()

        # Delete thumbnails
        base_filename = file_path.stem
        for size_name in IMAGE_SIZES.keys():
            thumb_filename = f"{base_filename}_{size_name}.jpg"
            thumb_path = UPLOAD_DIR / thumb_filename
            if thumb_path.exists():
                thumb_path.unlink()

        # Delete database record
        db.delete(image)
        db.commit()

        return {"message": "Image deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting image: {str(e)}",
        )


@router.post("/bulk-upload/{part_id}")
async def bulk_upload_images(
    part_id: int,
    files: List[UploadFile] = File(...),
    image_type: str = Form("main"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("parts.update")),
):
    """Upload multiple images for a part."""

    # Check if part exists
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")

    if len(files) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum 20 files allowed per upload"
        )

    uploaded_images = []
    failed_uploads = []

    for index, file in enumerate(files):
        try:
            # Validate file
            validate_image_file(file)

            # Check file size
            file_content = await file.read()
            if len(file_content) > MAX_FILE_SIZE:
                failed_uploads.append(
                    {
                        "filename": file.filename,
                        "error": f"File too large. Maximum size: "
                        f"{MAX_FILE_SIZE // (1024 * 1024)}MB",
                    }
                )
                continue

            # Generate filename and save
            filename = generate_filename(file.filename, part_id, f"{image_type}_{index}")
            file_path = UPLOAD_DIR / filename

            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_content)

            # Optimize and create thumbnails
            optimize_image(file_path)
            thumbnails = create_thumbnails(file_path, part_id, image_type)

            # Create database record
            part_image = PartImage(
                part_id=part_id,
                image_url=f"/api/v1/images/serve/{filename}",
                image_type=image_type,
                alt_text=f"{part.part_name} - {image_type} {index + 1}",
                sort_order=index,
                is_active=True,
            )

            db.add(part_image)
            db.flush()  # Get ID without committing

            thumbnail_urls = {
                size: f"/api/v1/images/serve/{thumb_filename}"
                for size, thumb_filename in thumbnails.items()
            }

            uploaded_images.append(
                {
                    "id": part_image.id,
                    "url": part_image.image_url,
                    "thumbnails": thumbnail_urls,
                    "filename": file.filename,
                }
            )

        except Exception as e:
            failed_uploads.append({"filename": file.filename, "error": str(e)})

    # Commit all successful uploads
    if uploaded_images:
        db.commit()

    return {
        "uploaded": len(uploaded_images),
        "failed": len(failed_uploads),
        "images": uploaded_images,
        "errors": failed_uploads,
    }


@router.get("/stats")
async def get_image_stats(
    db: Session = Depends(get_db), current_user: User = Depends(require_permission("parts.read"))
):
    """Get image storage statistics."""

    total_images = db.query(PartImage).count()
    active_images = db.query(PartImage).filter(PartImage.is_active).count()

    # Calculate storage usage
    total_size = 0
    file_count = 0

    if UPLOAD_DIR.exists():
        for file_path in UPLOAD_DIR.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1

    # Image type distribution
    type_stats = (
        db.query(PartImage.image_type, db.func.count(PartImage.id).label("count"))
        .filter(PartImage.is_active)
        .group_by(PartImage.image_type)
        .all()
    )

    return {
        "total_images": total_images,
        "active_images": active_images,
        "total_storage_bytes": total_size,
        "total_storage_mb": round(total_size / (1024 * 1024), 2),
        "total_files": file_count,
        "image_types": {stat.image_type: stat.count for stat in type_stats},
        "upload_directory": str(UPLOAD_DIR),
    }
