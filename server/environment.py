from models import SQLAction, SQLObservation, SQLState
from server.database import create_database, setup_task_1, setup_task_2, setup_task_3
from server.tasks import TASKS, compute_reward

import sqlite3
import uuid

from pydantic import BaseModel
from typing import Any, Dict


class StepResult(BaseModel):
    observation: SQLObservation
    reward: float
    done: bool
    info: Dict[str, Any]

class SQLQueryEnvironment:
    def __init__(self):
        self.db_path = None
        self.current_task = None
        self.task_id = None
        self.step_count = 0
        self.max_steps = 10
        self.best_score = 0.0
        self.episode_id = None

    def reset(self, task_id: str) -> StepResult:
        # Thread-safe: create fresh connection for this operation
        conn, cursor = create_database(task_id)
        self.db_path = task_id + ".db"
        
        # Set task
        self.task_id = task_id
        self.current_task = TASKS[task_id]

        # Reset state
        self.step_count = 0
        self.best_score = 0.0
        self.episode_id = str(uuid.uuid4())

        # Setup database based on task
        if task_id == "task_1_syntax":
            setup_task_1(conn, cursor)
        elif task_id == "task_2_logic":
            setup_task_2(conn, cursor)
        elif task_id == "task_3_optimization":
            setup_task_3(conn, cursor)
        
        # Close connection immediately (fresh connection per operation)
        conn.close()

        # Build initial observation
        obs = SQLObservation(
            task_id=task_id,
            task_description=self.current_task["description"],
            broken_query=self.current_task["broken_query"],
            current_query="",
            schema=self._get_schema(),
            error_message="",
            result_preview="",
            attempt_number=0,
            best_score_so_far=0.0,
            reward=0.0,
            done=False
        )

        return StepResult(
            observation=obs,
            reward=0.0,
            done=False,
            info={}
        )
    def _get_schema(self) -> str:
        # Thread-safe: create fresh connection for this operation
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        schema_info = []

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            column_defs = [f"{col[1]} ({col[2]})" for col in columns]
            schema_info.append(f"{table_name}: " + ", ".join(column_defs))

        conn.close()
        return "\n".join(schema_info)
    
    def step(self, action: SQLAction) -> StepResult:
        # Thread-safe: create fresh connection for this operation
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        self.step_count += 1

        query = action.query
        error_message = ""
        result_rows = []
        result_columns = []
        has_error = False

        # Execute query
        try:
            cursor.execute(query)
            result_rows = cursor.fetchall()
            result_columns = [desc[0] for desc in cursor.description] if cursor.description else []
        except Exception as e:
            error_message = str(e)
            has_error = True

        # Get expected result
        expected_query = self.current_task["expected_query"]

        cursor.execute(expected_query)
        expected_rows = cursor.fetchall()
        expected_columns = [desc[0] for desc in cursor.description]

        # Compute reward
        reward = compute_reward(
            has_error,
            result_columns,
            expected_columns,
            result_rows,
            expected_rows
        )

        # Track best score
        if reward > self.best_score:
            self.best_score = reward

        # Done condition
        done = (reward == 1.0) or (self.step_count >= self.max_steps)

        # Build observation
        obs = SQLObservation(
            task_id=self.task_id,
            task_description=self.current_task["description"],
            broken_query=self.current_task["broken_query"],
            current_query=query,
            schema=self._get_schema(),
            error_message=error_message,
            result_preview=str(result_rows[:5]),
            attempt_number=self.step_count,
            best_score_so_far=self.best_score,
            reward=reward,
            done=done
        )
        
        # Close connection immediately after operation (fresh connection per operation)
        conn.close()

        return StepResult(
            observation=obs,
            reward=reward,
            done=done,
            info={}
        )

    def state(self) -> SQLState:
        return SQLState(
            episode_id=self.episode_id,
            step_count=self.step_count,
            task_id=self.task_id,
            max_steps=self.max_steps,
            current_score=self.best_score
        )