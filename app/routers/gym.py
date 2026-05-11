from fastapi import APIRouter, Depends
from app.schemas.gym import (
    EnvCreateRequest, EnvCreateResponse,
    StepRequest, StepResponse,
    ResetResponse, SessionInfoResponse,
    BenchmarkRequest, BenchmarkResponse
)
from app.services import gym_service
from app.dependencies import verify_all


router = APIRouter(
    prefix="/gym",
    tags=["RL gym"]
)

@router.post("/environments", status_code=201, response_model=EnvCreateResponse, dependencies=[Depends(verify_all)])
async def create_environment(request: EnvCreateRequest):
    # Create new RL environment session
    return gym_service.create_environment(
        env_id=request.env_id,
        render_mode= request.render_mode
    )

@router.post("/environments/{session_id}/reset", response_model=ResetResponse, dependencies=[Depends(verify_all)])
async def reset_environment(session_id: str):
    # Reset environment to initial state
    return gym_service.reset_environment(session_id)

@router.post("/environments/{session_id}/step", response_model=StepResponse, dependencies=[Depends(verify_all)])
async def step_environment(session_id: str, requst: StepRequest):
    # Take one action step in the environment
    return gym_service.step_environment(session_id, requst.action)

@router.get("/environments/{session_id}", response_model=SessionInfoResponse, dependencies= [Depends(verify_all)])
async def get_session_info(session_id: str):
    # Get current session statistics
    return gym_service.get_session_info(session_id)

@router.get("/environments", response_model=list[SessionInfoResponse], dependencies=[Depends(verify_all)])
async def list_environments():
    # List all active environment session
    return gym_service.list_session()

@router.delete("/environments/{session_id}", status_code=200, dependencies=[Depends(verify_all)])
async def close_environment(session_id: str):
    # Close and Clean up environment session
    return gym_service.close_environment(session_id)

@router.post("/benchmark", response_model=BenchmarkResponse, dependencies=[Depends(verify_all)])
async def benchmark_environment(request: BenchmarkRequest):
    # Run multiple episodes with random agent and return statistics
    return gym_service.run_benchmark(
        env_id=request.env_id,
        episodes=request.episodes,
        max_step= request.max_steps
    )