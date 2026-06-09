from pydantic import BaseModel, Field
from typing import Optional

class TrainingRequest(BaseModel):
    env_id: str = "CartPole-v1"
    algorithm: str = "PPO" # A2C, DQN
    total_timesteps: int = Field(default=10000, ge=1000, le=500000)
    model_name: Optional[str] = None # will generate automatically if not provided
    
    
class TrainingResponse(BaseModel):
    model_name: str
    env_id: str
    alrithm: str
    total_timesteps: int
    training_time: int
    model_path: str
    message: str
    
    
class EvaluateRequest(BaseModel):
    model_name: str
    episodes: int = Field(default=5, ge=1, le=20)
    
class EvaluationResponse(BaseModel):
    model_name: str
    env_id: str
    algorithm: str
    episodes: int
    mean_reward: float
    std_reward: float
    min_reward: float
    max_reward: float
    mean_steps: float
    
class ModelInfoResponse(BaseModel):
    model_name: str
    env_id: str
    algorithm: str
    total_timesteps: int
    model_path: str

class TrainingStatusResponse(BaseModel):
    available_algorithms: list[str]
    available_models: list[ModelInfoResponse]
    trained_model_count: str