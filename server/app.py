from fastapi import FastAPI
from server.environment import SQLQueryEnvironment

app = FastAPI()

# Global environment instance
env = SQLQueryEnvironment()

@app.post("/reset")
def reset(task_id: str):
    result = env.reset(task_id)
    return result

from models import SQLAction

@app.post("/step")
def step(action: SQLAction):
    result = env.step(action)
    return result

@app.get("/state")
def state():
    return env.state()