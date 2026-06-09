import os
import time
import json
import uuid
from pathlib import Path
from typing import Optional
import numpy as np
from fastapi import HTTPException

MODEL_DIR = Path("trained_models")
MODEL_DIR.mkdir(exist_ok=True)

SUPPORTED_ALGORITHMS = ["PPO", "A2C", "DQN"]

# METADATA STORE

_model_registry: dict[str, dict] = {}

def _load_registry():
    #Load model registry from disk on start up
    registry_path = MODEL_DIR / "registry.json"
    if registry_path.exists:
        with open (registry_path, "r") as f:
            return json.load(f)
    return {}

def _save_registry():
    # persist registry to disk
    registry_path = MODEL_DIR
    if registry_path.exists:
        with open(registry_path, "w") as f:
            json.dump(_model_registry, f, indent=2)
            
# load on module import
_model_registry.update(_load_registry())


def train_agent(
    env_id: str,
    algorithm: str,
    total_timesteps: int,
    model_name: Optional[str] = None
) -> dict:
    
    # train an RL agent and save the model
    algorithm = algorithm.upper()
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise HTTPException(status_code=400, detail=f"Unsupported algorithm: {algorithm}."
                            f" Supported algorithms are: {', '.join(SUPPORTED_ALGORITHMS)}")
    
    # import SB3 algorithm here to avoid slow startup
    try:
        import gymnasium as gym
        from stable_baselines3 import PPO, A2C, DQN
    except ImportError:
        raise HTTPException(status_code=500, detail="Stable Baselines3 not installed. Run: pip install stable-baseline3")
    
    # DQN only workds with discrete action spaces, but we can check that after creating the env
    algo_map = {"PPO": PPO, "A2C": A2C, "DQN": DQN}
    
    #create environment
    try:
        env = gym.make(env_id)
    except gym.error.Error:
        raise HTTPException(status_code=400, detail=f"Invalid environment ID: {env_id}.")
    
    # DQN requires discrete action space
    if algorithm == "DQN":
        import gymnasium as gym_module
        if not isinstance(env.action_space, gym_module.spaces.Discrete):
            env.close()
            raise HTTPException(status_code=400, detail=f"DQN algorithm requires a discrete action space. Environment {env_id} has {type(env.action_space)}.")
    
    # Generate a unique model name if not provided
    
    """ 
    #claude
    if not model_name:
        short_id = str(uuid.uuid4())[:8]
        model_name = f"{algorithm}_{env_id.replace('-', '_')}_{short_id}"
    #copilot   
    if not model_name:
        model_name = f"{algorithm}_{env_id}_{uuid.uuid4().hex[:8]}"
         """
    
    #gemini
    if not model_name:
        clean_env = env_id.replace("-", "_")
        model_name = f"{algorithm}_{clean_env}_{uuid.uuid4().hex[:8]}"
        
    #check for duplicate name
    if model_name in _model_registry:
        raise HTTPException(status_code=400,
                            detail=f"Model {model_name} already exists. Choose a different name.")
    
    model_path = MODEL_DIR / f"{model_name}.zip"
    
    # Simulate training time
    start_time = time.time()
    try:
        AlgoClass = algo_map[algorithm]
        model = AlgoClass("MlpPolicy", env, verbose=0)
        model.learn(total_timesteps=total_timesteps)
        model.save(model_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")
    finally:
        env.close()
        
    training_time = round(time.time() - start_time, 2)
    
    
    # Simulate saving a trained model file
    with open(model_path, "w") as f:
        f.write("This simulates a trained model file.")
    
    # Register model
    _model_registry[model_name] = {
        "model_name": model_name,
        "env_id": env_id,
        "algorithm": algorithm,
        "total_timesteps": total_timesteps,
        "training_time": training_time,
        "model_path": str(model_path)
    }
    _save_registry()
    
    return {
        "model_name": model_name,
        "env_id": env_id,
        "algorithm": algorithm,
        "total_timesteps": total_timesteps,
        "training_time_seconds": training_time,
        "model_path": str(model_path), 
        "message": f"Trained successfully in {training_time} seconds. Model saved at {model_path}."
    }
    
    
def evaluate_agent(model_name: str, num_episodes: int = 5) -> dict:
    # evaluate a trained agent model, evaluate it and return average reward
    if model_name not in _model_registry:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found. Train it first")
    
    info = _model_registry[model_name]
    model_path = info["model_path"]
    
    if not Path(model_path).exists():
        raise HTTPException(status_code=404, detail=f"Model file not found at {model_path}. It may have been deleted.")
    

    # import SB3 algorithm here to avoid slow startup
    try:
        import gymnasium as gym
        from stable_baselines3 import PPO, A2C, DQN
    except ImportError:
        raise HTTPException(status_code=500, detail="Stable Baselines3 not installed. Run: pip install stable-baseline3")
    
    algo_map = {"PPO": PPO, "A2C": A2C, "DQN": DQN}
    AlgoClass = algo_map[info["algorithm"]]
    
    # Load environment and model
    try:
        env = gym.make(info["env_id"])
        model = AlgoClass.load(model_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model or environment: {str(e)}")
    
    episode_rewards = []
    episode_steps = []
    
    for _ in range(num_episodes):
        obs, _ = env.reset()
        done = False
        total_reward = 0
        steps = 0
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, _ = env.step(action)
            total_reward += reward
            steps += 1
            done = terminated or truncated
        
        episode_rewards.append(total_reward)
        episode_steps.append(steps)  
    
    env.close()
    rewards = np.array(episode_rewards)
        
    return {
        "model_name": model_name,
        "env_id": info["env_id"],
        "algorithm": info["algorithm"],
        "episodes": num_episodes,
        "mean_reward": round(float(np.mean(rewards)), 3),
        "std_reward": round(float(np.std(rewards)), 3),
        "min_reward": round(float(np.min(rewards)), 3),
        "max_reward": round(float(np.max(rewards)), 3),
        "mean_steps": round(float(np.mean(episode_steps)), 1)
    }
    
def get_model_info(model_name: str) -> dict:
    # get model metadata info
    if model_name not in _model_registry:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found.")
    
    return _model_registry[model_name]

def list_models() -> list[dict]:
    # list all trained models with metadata
    return list(_model_registry.values())

def delete_model(model_name: str) -> dict:
    # delete a trained model and its metadata
    if model_name not in _model_registry:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found.")
    
    model_path = _model_registry[model_name]["model_path"]
    
    # Delete model file
    try:
        if Path(model_path).exists():
            os.remove(model_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete model file: {str(e)}")
    
    # Remove from registry
    del _model_registry[model_name]
    _save_registry()
    
    return {"message": f"Model {model_name} and its metadata have been deleted."}

def get_status() -> dict:
    # get overall status of the training service
    return {
        "available_algorithms": SUPPORTED_ALGORITHMS,
        "available_models": list(_model_registry.values()),
        "trained_model_count": len(_model_registry)
    }