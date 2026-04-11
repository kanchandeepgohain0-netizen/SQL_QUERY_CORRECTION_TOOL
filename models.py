from pydantic import BaseModel
from typing import Dict, Any


# Base classes (replacement for openenv.core)
class Action(BaseModel):
    pass


class Observation(BaseModel):
    done: bool
    reward: float
    metadata: Dict[str, Any] = {}


class State(BaseModel):
    pass

# =========================
# ACTION (Agent → Env)
# =========================
class SQLAction(Action):
    query: str          # SQL query from agent
    task_id: str        # Task identifier

# =========================
# OBSERVATION (Env → Agent)
# =========================
class SQLObservation(Observation):
    # Inherited: reward: Optional[float], done: bool

    task_id: str
    task_description: str
    broken_query: str
    current_query: str
    schema: str
    error_message: str
    result_preview: str
    attempt_number: int
    best_score_so_far: float

# =========================
# STATE (Internal)
# =========================
class SQLState(State):
    # Inherited: episode_id, step_count
    episode_id: str
    step_count: int
    task_id: str
    max_steps: int
    current_score: float