from datetime import datetime
from uuid import UUID
from typing import Optional, List, Any, Dict
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """
    Schema representing a single audit log entry returned to the client.
    """
    id: UUID
    user_id: UUID
    action: str
    entity_type: str
    entity_id: Optional[UUID] = None
    description: str
    metadata_: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
        # Map the ORM attribute name (metadata_) to the JSON key (metadata)
        "populate_by_name": True,
    }

    @classmethod
    def model_validate(cls, obj, **kwargs):
        # Bridge ORM metadata_ -> response field metadata_
        return super().model_validate(obj, **kwargs)


class AuditLogListResponse(BaseModel):
    """
    Paginated schema representing a list of audit log entries.
    """
    items: List[AuditLogResponse]
    total: int
    page: int
    pages: int
    limit: int
