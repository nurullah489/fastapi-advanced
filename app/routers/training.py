from fastapi import APIRouter, Depends
from app.services import training_service
from app.dependencies import verify_all
from app.schemas.training import (
    TrainingRequest,
    TrainingResponse,
    EvaluateRequest,
    EvaluationResponse,
    ModelInfoResponse,
    TrainingStatusResponse
)

router = APIRouter(
    prefix="/training",
    tags=["RL Training"],
    dependencies=[Depends(verify_all)]
)

@router.get("/status", response_model=TrainingStatusResponse, dependencies=[Depends(verify_all)])
async def get_status():
    return training_service.get_status()

@router.post("/train", response_model=TrainingResponse, status_code=201, dependencies=[Depends(verify_all)])
async def train_agent(request: TrainingRequest):
    
    """
    Train an RL agent.

    - **env_id**: Gymnasium environment (CartPole-v1, MountainCar-v0, Acrobot-v1)
    - **algorithm**: PPO, A2C, or DQN
    - **total_timesteps**: Training steps (1000–500000)
    - **model_name**: Optional custom name
    """

    return training_service.train_agent(
        env_id=request.env_id,
        algorithm=request.algorithm,
        total_timesteps=request.total_timesteps,
        model_name=request.model_name
    )

@router.post("/evaluate", response_model=EvaluationResponse, dependencies=[Depends(verify_all)])
async def evaluate_agent(request: EvaluateRequest):
    
    """
    Evaluate a trained model.

    - **model_name**: Name of the trained model
    - **episodes**: Number of evaluation episodes
    """
    
    return training_service.evaluate_agent(
        model_name=request.model_name,
        episodes=request.episodes
    )

@router.get("/models", response_model=list[ModelInfoResponse], dependencies=[Depends(verify_all)])
async def list_models():
    """
    List all trained models with their details.
    """
    return training_service.list_models()

@router.get("/models/{model_name}", response_model=ModelInfoResponse, dependencies=[Depends(verify_all)])
async def get_model(model_name: str):
    """
    Get details of a specific trained model.
    """
    return training_service.get_model_info(model_name)

@router.delete("/models/{model_name}", status_code=204, dependencies=[Depends(verify_all)])
async def delete_model(model_name: str):
    """
    Delete a trained model and its metadata.
    """
    return training_service.delete_model(model_name)