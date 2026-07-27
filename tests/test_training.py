import pytest

pytestmark = pytest.mark.asyncio

CARTPOLE = "CartPole-v1"
MOUNTAINCAR = "MountainCar-v0"


async def test_get_status(client, auth_headers):
    response = await client.get("/training/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "available_algorithms" in data
    assert "PPO" in data["available_algorithms"]
    assert "trained_model_count" in data
    
async def test_train_ppo_agent(client, auth_headers):
    request_data = {
        "env_id": CARTPOLE,
        "algorithm": "PPO",
        "total_timesteps": 1000,
        "model_name": "test_ppo_cartpole"
    }
    response = await client.post("/training/train", json=request_data, headers=auth_headers)
    print(response.text)
    assert response.status_code == 201
    data = response.json()
    assert data["model_name"] == "test_ppo_cartpole"
    assert data["algorithm"] == "PPO"
    assert data["env_id"] == CARTPOLE
    assert data["training_time_seconds"] > 0
    assert "model_path" in data
    
async def test_train_a2c_agent(client, auth_headers):
    request_data = {
        "env_id": CARTPOLE,
        "algorithm": "A2C",
        "total_timesteps": 1000,
        "model_name": "test_a2c_cartpole"
    }
    response = await client.post("/training/train", json=request_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["model_name"] == "test_a2c_cartpole"
    assert data["algorithm"] == "A2C"
    assert data["env_id"] == CARTPOLE
    assert data["training_time_seconds"] > 0
    assert "model_path" in data
    assert response.json()["algorithm"] == "A2C"
    
async def test_train_dqn_agent(client, auth_headers):
    request_data = {
        "env_id": MOUNTAINCAR,
        "algorithm": "DQN",
        "total_timesteps": 1000,
        "model_name": "test_dqn_mountaincar"
    }
    response = await client.post("/training/train", json=request_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["model_name"] == "test_dqn_mountaincar"
    assert data["algorithm"] == "DQN"
    assert data["env_id"] == MOUNTAINCAR
    assert data["training_time_seconds"] > 0
    assert "model_path" in data
    assert response.json()["algorithm"] == "DQN"
    
async def test_train_invalid_algorithm(client, auth_headers):
    request_data = {
        "env_id": CARTPOLE,
        "algorithm": "INVALID_ALGO",
        "total_timesteps": 1000,
        "model_name": "test_invalid_algo"
    }
    response = await client.post("/training/train", json=request_data, headers=auth_headers)
    #assert response.status_code == 422
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    
async def test_train_invalid_environment(client, auth_headers):
    request_data = {
        "env_id": "InvalidEnv-v0",
        "algorithm": "PPO",
        "total_timesteps": 1000,
        "model_name": "test_invalid_env"
    }
    response = await client.post("/training/train", json=request_data, headers=auth_headers)
    #assert response.status_code == 422
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    
async def test_train_duplicate_model_name(client, auth_headers):
    request_data = {
        "env_id": CARTPOLE,
        "algorithm": "PPO",
        "total_timesteps": 1000,
        "model_name": "duplicate_model_cartpole"
    }
    # First training should succeed
    response1 = await client.post("/training/train", json=request_data, headers=auth_headers)
    assert response1.status_code == 201
    
    # Second training with the same model name should fail
    response2 = await client.post("/training/train", json=request_data, headers=auth_headers)
    assert response2.status_code == 400
    data = response2.json()
    assert "detail" in data
    
async def test_evaluate_trained_model(client, auth_headers):
    # First, train a model
    train_request_data = {
        "env_id": CARTPOLE,
        "algorithm": "PPO",
        "total_timesteps": 1000,
        "model_name": "eval_test_model"
    }
    train_response = await client.post("/training/train", json=train_request_data, headers=auth_headers)
    assert train_response.status_code == 201
    
    # Now evaluate the trained model
    eval_request_data = {
        "model_name": "eval_test_model",
        "episodes": 3
    }
    eval_response = await client.post("/training/evaluate", json=eval_request_data, headers=auth_headers)
    assert eval_response.status_code == 200
    data = eval_response.json()
    assert data["model_name"] == "eval_test_model"
    assert data["episodes"] == 3
    assert "mean_reward" in data
    assert "std_reward" in data
    assert data["min_reward"] <= data["mean_reward"] <= data["max_reward"]
    
async def test_evaluate_nonexistent_model(client, auth_headers):
    eval_request_data = {
        "model_name": "nonexistent_model",
        "episodes": 3
    }
    eval_response = await client.post("/training/evaluate", json=eval_request_data, headers=auth_headers)
    assert eval_response.status_code == 404
    data = eval_response.json()
    assert "detail" in data

async def test_list_models(client, auth_headers):
    # Train a model to ensure at least one exists
    train_request_data = {
        "env_id": CARTPOLE,
        "algorithm": "PPO",
        "total_timesteps": 1000,
        "model_name": "list_test_model"
    }
    await client.post("/training/train", json=train_request_data, headers=auth_headers)
    
    # Now list models
    response = await client.get("/training/models", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(model["model_name"] == "list_test_model" for model in data)
    
async def test_get_model_info(client, auth_headers):
    # Train a model to ensure it exists
    train_request_data = {
        "env_id": CARTPOLE,
        "algorithm": "PPO",
        "total_timesteps": 1000,
        "model_name": "info_test_model"
    }
    await client.post("/training/train", json=train_request_data, headers=auth_headers)
    
    # Now get model info
    response = await client.get("/training/models/info_test_model", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "info_test_model"
    assert data["algorithm"] == "PPO"
    assert data["env_id"] == CARTPOLE
    
async def test_get_nonexistent_model_info(client, auth_headers):
    response = await client.get("/training/models/nonexistent_model", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    
async def test_delete_model(client, auth_headers):
    # Train a model to ensure it exists
    train_request_data = {
        "env_id": CARTPOLE,
        "algorithm": "PPO",
        "total_timesteps": 1000,
        "model_name": "delete_test_model"
    }
    await client.post("/training/train", json=train_request_data, headers=auth_headers)
    
    # Now delete the model
    response = await client.delete("/training/models/delete_test_model", headers=auth_headers)
    assert response.status_code == 204
    #assert response.status_code == 200
    
    # Verify that the model no longer exists
    get_response = await client.get("/training/models/delete_test_model", headers=auth_headers)
    assert get_response.status_code == 404
    
async def test_delete_nonexistent_model(client, auth_headers):
    response = await client.delete("/training/models/nonexistent_model", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    
async def test_delete_model_no_auth(client):
    response = await client.delete("/training/models/some_model")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data

async def test_training_no_auth(client):
    request_data = {
        "env_id": CARTPOLE,
        "algorithm": "PPO",
        "total_timesteps": 1000,
        "model_name": "no_auth_model"
    }
    response = await client.post("/training/train", json=request_data)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data