"""iCal import/export routes"""

import logging
from typing import BinaryIO

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi_sqlalchemy import db

from calendar_backend.methods.ical_import import import_ical_file, validate_ical_file
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


@router.post("/ical", response_model=list[PersonalEventGet], status_code=status.HTTP_201_CREATED)
async def import_ical(
    file: UploadFile = File(...),
    auth_result = Depends(UnionAuth(scopes=["timetable.calendar.import"])),
) -> list[PersonalEventGet]:
    """Import events from an iCal file as personal events"""
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
        if not validate_ical_file(file_obj):
            raise HTTPException(
                status_code=400,
                detail="Invalid iCal file format"
            )

        # Import events
        file_obj.seek(0)  # Reset file pointer
        events = await import_ical_file(file_obj, user_id, db.session)
        
        if not events:
            return []

        return [PersonalEventGet.model_validate(event) for event in events]

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to import iCal file: {e}")
        raise HTTPException(status_code=500, detail="Failed to import calendar file")
    finally:
        await file.close()


@router.post("/ical/admin", response_model=list[dict], status_code=status.HTTP_201_CREATED)
async def import_ical_admin(
    file: UploadFile = File(...),
    auth_result = Depends(UnionAuth(scopes=["timetable.event.create"])),
) -> list[dict]:
    """Import events from an iCal file as institutional events (admin only)"""
    
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
        if not validate_ical_file(file_obj):
            raise HTTPException(
                status_code=400,
                detail="Invalid iCal file format"
            )

        # Import events (without user_id for institutional events)
        file_obj.seek(0)  # Reset file pointer
        events = await import_ical_file(file_obj, None, db.session)
        
        if not events:
            return []

        # Return basic event info for institutional events
        return [
            {
                "id": event.id,
                "name": event.name,
                "start_ts": event.start_ts,
                "end_ts": event.end_ts,
                "is_personal": event.is_personal,
                "created": True
            }
            for event in events
        ]

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to import iCal file: {e}")
        raise HTTPException(status_code=500, detail="Failed to import calendar file")
    finally:
        await file.close()