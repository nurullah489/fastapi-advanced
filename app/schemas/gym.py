from pydantic import BaseModel
from typing import Any, Optional

class EnvCreateRequest(BaseModel):
    env_id: str
    render_mode: Optional[str] = None
    
class EnvCreateResponse(BaseModel):
    session_id: str
    env_id: str
    observation_space: str
    action_space: str
    message: str

class StepRequest(BaseModel):
    action: int
    
class StepResponse(BaseModel):
    session_id: str
    observation: list[float]
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, Any]
    step_count: int
    
class ResetRequest(BaseModel):
    session_id: str
    
class ResetResponse(BaseModel):
    session_id: str
    observation: list[float]
    info: dict[str, Any]
    
class SessionInfoResponse(BaseModel):
    session_id: str
    env_id: str
    step_count: int
    total_reward: float
    is_active: bool
    
class BenchmarkRequest(BaseModel):
    env_id: str
    episodes: int = 5
    max_steps: int = 500
    
class BenchmarkResponse(BaseModel):
    env_id: str
    episodes: int
    mean_reward: float
    min_reward: float
    max_reward: float
    mean_steps: int