import asyncio
import pytest

pytestmark = pytest.mark.asyncio

CARTPOLE = "CartPole-v1"
MOUNTAIN_CAR = "MountainCar-v0"

# Create environment

async def test_create_environment_success(client, auth_headers):
    payload = {
        "env_id": CARTPOLE,    
    }
    response = await client.post("/gym/environments", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["env_id"] == CARTPOLE
    assert "observation_space" in data
    assert "action_space" in data
    
async def test_create_invalid_environment(client, auth_headers):
    response = await client.post("/gym/environments", json = {
        "env_id":"invalid_id"
    }, headers=auth_headers)
    assert response.status_code == 400, "Invalid_environment response code missmatched"

async def test_create_environment_no_auth(client):
    response = await client.post("/gym/environments", json={
        "env_id": CARTPOLE
    })
    assert response.status_code == 401, "invalid response code for create environment no auth"
    

# Reset environmetn --------
async def test_reset_environment(client, auth_headers):
    create = await client.post("/gym/environments", json={"env_id": CARTPOLE}, headers=auth_headers)
    session_id = create.json()["session_id"]
    
    response = await client.post(f"/gym/environments/{session_id}/reset", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "observation" in data
    assert isinstance(data["observation"], list)
    
# step -----------
async def test_step_environment(client, auth_headers):
    create = await client.post("/gym/environments", json={"env_id":CARTPOLE}, headers=auth_headers)
    session_id = create.json()["session_id"]
    
    response = await client.post(f"gym/environments/{session_id}/step", json={"action":0}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "observation" in data
    assert "terminated" in data
    assert "truncated" in data
    assert "reward" in data
    assert "step_count" in data
    assert data["step_count"] == 1
    
    
async def test_step_invalid_action(client, auth_headers):
    create = await client.post("/gym/environments", json={"env_id":CARTPOLE}, headers=auth_headers)
    session_id = create.json()["session_id"]
    
    response = await client.post(f"/gym/environments/{session_id}/step", json={"action":999}, headers=auth_headers)
    assert response.status_code == 400
    
async def test_step_nonexistent_session(client, auth_headers):
    response = await client.post("/gym/environments/fake_session/step", json={"action":0}, headers=auth_headers)
    assert response.status_code == 404
    
    
# session ---------

async def test_get_session_info(client, auth_headers):
    create = await client.post("/gym/environments", json={"env_id":CARTPOLE}, headers=auth_headers)
    session_id = create.json()["session_id"]
    # take some steps
    for _ in range(5):
        await client.post(f"/gym/environments/{session_id}/step", json={"action":1}, headers=auth_headers)
    
    response = await client.get(f"/gym/environments/{session_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["step_count"] == 5
    assert data["is_active"] == True
    
    
# list sessions
async def test_lsit_environments(client, auth_headers):
    # create multiple session
    create1 = await client.post("/gym/environments", json={"env_id":CARTPOLE}, headers=auth_headers)
    create2 = await client.post("/gym/environments", json={"env_id":CARTPOLE}, headers=auth_headers)
    
    response = await client.get("/gym/environments", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    

# Close environment
async def test_close_environment(client, auth_headers):
    create = await client.post("/gym/environments", json={"env_id":CARTPOLE}, headers=auth_headers)
    session_id = create.json()["session_id"]
    
    response = await client.delete(f"/gym/environments/{session_id}", headers=auth_headers)
    assert response.status_code == 200
    
    
# benchmark ---------
async def test_benchmark(client, auth_headers):
    response = await client.post("/gym/benchmark", json={
        "env_id": CARTPOLE,
        "episodes":3,
        "max_steps":100
    }, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["episodes"] == 3
    assert "mean_reward" in data
    assert "min_reward" in data
    assert "max_reward" in data
    assert data["min_reward"] <= data["mean_reward"] <= data["max_reward"]
    