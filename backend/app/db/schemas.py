from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class AgentLogSchema(BaseModel):
    id: int
    agent: str
    role: Optional[str]
    action: str
    status: str
    timestamp: datetime

    class Config:
        orm_mode = True


class AgentSchema(BaseModel):
    name: str
    role: str
    department: str
    tools: List[str]


class ExecuteResponse(BaseModel):
    agent: str
    task_id: int
    status: str
    message: str


class AgentListResponse(BaseModel):
    total: int
    agents: List[AgentSchema]


class LogListResponse(BaseModel):
    total: int
    logs: List[AgentLogSchema]
