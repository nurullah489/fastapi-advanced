import uuid
import gymnasium as gym
from typing import Optional
from fastapi import HTTPException

# session: for local - in memory, for production Redis is the best choice 
_session: dict[str, dict] = {}

def create_environment(env_id: str, render_mode: Optional[str] = None) -> dict:
    #Create new Gym environment session
    try:
        environment = gym.make(env_id, render_mode=render_mode)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Unknown environment: {env_id}"
                            f"Try 'CartPole-v1', 'MountainCar-v0', 'Acrobot-v1' ")
    
    session_id: str =  str(uuid.uuid4())
    observation, info = environment.reset()
    
    _session[session_id] = {
        "env_id": env_id,
        "env": environment,
        "step_count": 0,
        "total_reward": 0.0,
        "is_active": True
    }
    return {
        "session_id": session_id,
        "env_id": env_id,
        "observation_space": str(environment.observation_space),
        "action_space": str(environment.action_space),
        "message": f"Environment '{env_id}' created, Session: {session_id}"
    }
    
def get_session(session_id: str) -> dict:
    # get active session or raise 404
    session = _session.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    if not session["is_active"]:
        raise HTTPException(status_code=400, detail=f"Session {session_id} is closed")
    return session

def reset_environment(session_id: str) -> dict:
    # Reset environment to initial state
    
    session = get_session(session_id)
    observation, info = session["env"].reset()
    session["step_count"] = 0
    session["total_reward"] = 0.0
    
    return {
        "session_id": session_id,
        "observation": observation.tolist(),
        "info": info
    }
        
def step_environment(session_id: str, action: int) -> dict:
    # take one step in the environment
    
    session = get_session(session_id)
    env = session["env"]
    
    #validate action
    if not env.action_space.contains(action):
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}."
                            f"Valid range: 0 to {env.action_space.n -1}")
    
    observation, reward, terminated, truncated, info = env.step(action)
    
    session["step_count"] += 1
    session["total_reward"] += float(reward)
    
    # auto reset if episode ended
    if terminated or truncated:
        env.reset()
    
    return {
        "session_id": session_id,
        "observation": observation.tolist(),
        "reward": float(reward),
        "terminated": terminated,
        "truncated": truncated,
        "info": info,
        "step_count": session["step_count"]
        }
    
def get_session_info(session_id: str) -> dict:
    # get current session statistics
    
    session = get_session(session_id)
    return {
        "session_id": session_id,
        "env_id": session["env_id"],
        "step_count": session["step_count"],
        "total_reward": session["total_reward"],
        "is_active": session["is_active"]
    }
    
    
def close_environment(session_id: str) -> dict:
    # Close and Clean up environment session
    
    session = get_session(session_id)
    session["env"].close()
    session["is_active"] = False
    return {"Message: ": f"Session {session_id} closed successfully"}


def list_session() -> list[dict]:
    return [
        {
            "session_id": sid,
            "env_id": s["env_id"],
            "step_count": s["step_count"],
            "total_reward": s["total_reward"],
            "is_active": s["is_active"]
        }
        for sid, s in _session.item() if s["is_active"]
    ]
    
def run_benchmark(env_id: str, episodes: int = 5, max_step: int = 500) -> dict:
    # run multiple episodes with random agent and return statistics
    try:
        environment = gym.make(env_id)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Unknown environment: {env_id}")
    
    episod_reward = []
    episode_steps = []
    
    for _ in range(episodes):
        
        observation, _ = environment.reset()
        total_reward = 0.0
        steps = 0
        
        for step in range(max_step):
            action = environment.action_space.sample() # random agent
            observation, reward, terminated, truncated, _ = environment.step(action)
            total_reward += float(reward)
            step += 1
            
            if terminated or truncated:
                break
        episod_reward.append(total_reward)
        episode_steps.append(steps)
    
    environment.close()   
    
    return {
        "env_id": env_id,
        "episodes": episodes,
        "mean_reward": round(sum(episod_reward) / len(episod_reward), 3),
        "min_reward": round(min(episod_reward), 3),
        "max_reward": round(max(episod_reward), 3),
        "mean_steps": round(sum(episode_steps) / len(episode_steps), 1)
    }
    