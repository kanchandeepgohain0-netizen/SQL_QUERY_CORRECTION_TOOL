from openenv.core.env_server import Action, Observation, State
from typing import Optional

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

    task_id: str
    max_steps: int
    current_score: float