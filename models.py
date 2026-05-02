from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class ContextPayload(BaseModel):
    scope: str  # 'merchant', 'category', or 'customer'
    context_id: str
    data: Dict[str, Any]

class TriggerPayload(BaseModel):
    id: str
    merchant_id: str
    type: str
    description: str
    metrics: Optional[Dict[str, Any]] = None

class BotResponse(BaseModel):
    message: str
    cta: str
    rationale: str