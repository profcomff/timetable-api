"""iCal import/export routes"""

import logging
from typing import BinaryIO

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi_sqlalchemy import db

from calendar_backend.methods.ical_import import import_ical_file, validate_ical_file, get_ical_preview
from calendar_backend.routes.models import PersonalEventGet

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/import", tags=["Calendar Import"])


def get_user_id_from_auth(auth_result: dict | None) -> int:
    """Extract user ID from auth result - placeholder implementation"""
    # TODO: Implement proper user ID extraction from auth system
    # For now, return a placeholder user ID
    if auth_result and isinstance(auth_result, dict):
        return auth_result.get('user_id', 1)
    return 1  # Default user ID for testing


@router.post("/ical/preview", response_model=dict)
async def preview_ical(
    file: UploadFile = File(...),
    max_events: int = Query(default=5, description="Maximum events to preview"),
    auth_result = Depends(UnionAuth(scopes=["timetable.calendar.import"])),
) -> dict:
    """Preview events from an iCal file before importing"""
    user_id = get_user_id_from_auth(auth_result)
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(('.ics', '.ical')):
        raise HTTPException(
            status_code=400,
            detail="File must be an iCal file (.ics or .ical extension)"
        )

    try:
        # Read file content
        content = await file.read()
        
        # Create a file-like object for preview
        from io import BytesIO
        file_obj = BytesIO(content)
        
        # Validate iCal format
        is_valid, validation_errors = validate_ical_file(file_obj)
        if not is_valid:
            return {
                "valid": False,
                "errors": validation_errors,
                "preview": {}
            }

        # Get preview
        file_obj.seek(0)  # Reset file pointer
        preview = get_ical_preview(file_obj, max_events)
        
        return {
            "valid": True,
            "errors": [],
            "preview": preview
        }

    except Exception as e:
        logger.error(f"Failed to preview iCal file: {e}")
        raise HTTPException(status_code=500, detail="Failed to process calendar file")
    finally:
        await file.close()


@router.post("/ical", response_model=dict, status_code=status.HTTP_201_CREATED)
async def import_ical(
    file: UploadFile = File(...),
    auth_result = Depends(UnionAuth(scopes=["timetable.calendar.import"])),
) -> dict:
    """Import events from an iCal file as personal events with detailed results"""
    user_id = get_user_id_from_auth(auth_result)
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(('.ics', '.ical')):
        raise HTTPException(
            status_code=400,
            detail="File must be an iCal file (.ics or .ical extension)"
        )

    try:
        # Read file content
        content = await file.read()
        
        # Create a file-like object for validation and import
        from io import BytesIO
        file_obj = BytesIO(content)
        
        # Validate iCal format
        is_valid, validation_errors = validate_ical_file(file_obj)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid iCal file: {'; '.join(validation_errors)}"
            )

        # Import events
        file_obj.seek(0)  # Reset file pointer
        import_result = await import_ical_file(file_obj, user_id, db.session)
        
        return {
            "success": True,
            "events_created": len(import_result.events_created),
            "events_skipped": len(import_result.events_skipped),
            "total_processed": import_result.total_events_processed,
            "created_events": [PersonalEventGet.model_validate(event) for event in import_result.events_created],
            "skipped_events": import_result.events_skipped,
            "errors": import_result.errors,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to import iCal file: {e}")
        raise HTTPException(status_code=500, detail="Failed to import calendar file")
    finally:
        await file.close()


@router.post("/ical/admin", response_model=dict, status_code=status.HTTP_201_CREATED)
async def import_ical_admin(
    file: UploadFile = File(...),
    auth_result = Depends(UnionAuth(scopes=["timetable.event.create"])),
) -> dict:
    """Import events from an iCal file as institutional events (admin only) with detailed results"""
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(('.ics', '.ical')):
        raise HTTPException(
            status_code=400,
            detail="File must be an iCal file (.ics or .ical extension)"
        )

    try:
        # Read file content
        content = await file.read()
        
        # Create a file-like object for validation and import
        from io import BytesIO
        file_obj = BytesIO(content)
        
        # Validate iCal format
        is_valid, validation_errors = validate_ical_file(file_obj)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid iCal file: {'; '.join(validation_errors)}"
            )

        # Import events (without user_id for institutional events)
        file_obj.seek(0)  # Reset file pointer
        import_result = await import_ical_file(file_obj, None, db.session)
        
        return {
            "success": True,
            "events_created": len(import_result.events_created),
            "events_skipped": len(import_result.events_skipped),
            "total_processed": import_result.total_events_processed,
            "created_events": [
                {
                    "id": event.id,
                    "name": event.name,
                    "start_ts": event.start_ts,
                    "end_ts": event.end_ts,
                    "is_personal": event.is_personal,
                    "created": True
                }
                for event in import_result.events_created
            ],
            "skipped_events": import_result.events_skipped,
            "errors": import_result.errors,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to import iCal file: {e}")
        raise HTTPException(status_code=500, detail="Failed to import calendar file")
    finally:
        await file.close()