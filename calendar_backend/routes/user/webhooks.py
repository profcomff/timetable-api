"""Webhook management routes"""

import logging
import secrets
from typing import List

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_sqlalchemy import db
from pydantic import BaseModel, HttpUrl

from calendar_backend.models.webhook import Webhook, WebhookEventType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["Webhook Management"])


def get_user_id_from_auth(auth_result: dict | None) -> int:
    """Extract user ID from auth result - placeholder implementation"""
    # TODO: Implement proper user ID extraction from auth system
    if auth_result and isinstance(auth_result, dict):
        return auth_result.get('user_id', 1)
    return 1


class WebhookCreate(BaseModel):
    name: str
    url: HttpUrl
    event_types: List[WebhookEventType]


class WebhookResponse(BaseModel):
    id: int
    user_id: int
    name: str
    url: str
    event_types: List[str]
    is_active: bool
    secret: str | None = None  # Only returned on creation
    create_ts: str
    update_ts: str


class WebhookUpdate(BaseModel):
    name: str | None = None
    url: HttpUrl | None = None
    event_types: List[WebhookEventType] | None = None
    is_active: bool | None = None


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreate,
    auth_result = Depends(UnionAuth(scopes=["timetable.webhook.create"])),
) -> WebhookResponse:
    """Create a new webhook for calendar synchronization"""
    user_id = get_user_id_from_auth(auth_result)
    
    # Generate a random secret for webhook signature verification
    secret = secrets.token_urlsafe(32)
    
    webhook = Webhook.create(
        user_id=user_id,
        name=webhook_data.name,
        url=str(webhook_data.url),
        secret=secret,
        event_types=[event_type.value for event_type in webhook_data.event_types],
        session=db.session,
    )
    db.session.commit()
    
    response = WebhookResponse.model_validate(webhook)
    response.secret = secret  # Include secret only in creation response
    return response


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    auth_result = Depends(UnionAuth(scopes=["timetable.webhook.read"])),
) -> List[WebhookResponse]:
    """List user's webhooks"""
    user_id = get_user_id_from_auth(auth_result)
    
    webhooks = db.session.query(Webhook).filter(
        Webhook.user_id == user_id
    ).all()
    
    return [WebhookResponse.model_validate(webhook) for webhook in webhooks]


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: int,
    auth_result = Depends(UnionAuth(scopes=["timetable.webhook.read"])),
) -> WebhookResponse:
    """Get a specific webhook"""
    user_id = get_user_id_from_auth(auth_result)
    
    webhook = Webhook.get(webhook_id, session=db.session)
    if not webhook or webhook.user_id != user_id:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return WebhookResponse.model_validate(webhook)


@router.patch("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: int,
    webhook_update: WebhookUpdate,
    auth_result = Depends(UnionAuth(scopes=["timetable.webhook.update"])),
) -> WebhookResponse:
    """Update a webhook"""
    user_id = get_user_id_from_auth(auth_result)
    
    webhook = Webhook.get(webhook_id, session=db.session)
    if not webhook or webhook.user_id != user_id:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # Update fields
    update_data = webhook_update.model_dump(exclude_unset=True)
    if 'url' in update_data:
        update_data['url'] = str(update_data['url'])
    if 'event_types' in update_data:
        update_data['event_types'] = [event_type.value for event_type in update_data['event_types']]
    
    updated_webhook = Webhook.update(webhook_id, session=db.session, **update_data)
    db.session.commit()
    
    return WebhookResponse.model_validate(updated_webhook)


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: int,
    auth_result = Depends(UnionAuth(scopes=["timetable.webhook.delete"])),
) -> None:
    """Delete a webhook"""
    user_id = get_user_id_from_auth(auth_result)
    
    webhook = Webhook.get(webhook_id, session=db.session)
    if not webhook or webhook.user_id != user_id:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    Webhook.delete(webhook_id, session=db.session)
    db.session.commit()


@router.post("/{webhook_id}/test", status_code=status.HTTP_200_OK)
async def test_webhook(
    webhook_id: int,
    auth_result = Depends(UnionAuth(scopes=["timetable.webhook.test"])),
) -> dict:
    """Test a webhook by sending a test payload"""
    user_id = get_user_id_from_auth(auth_result)
    
    webhook = Webhook.get(webhook_id, session=db.session)
    if not webhook or webhook.user_id != user_id:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # TODO: Implement actual webhook delivery testing
    # For now, just return a success message
    return {
        "success": True,
        "message": f"Test webhook delivery initiated for webhook {webhook_id}",
        "webhook_url": webhook.url
    }