import os
import json
from client import EnvClient

from groq import Groq

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def log_start(task: str, env: str, model: str):
    print(json.dumps({
        "event": "start",
        "task": task,
        "env": env,
        "model": model
    }))


def log_step(step: int, action: str, reward: float, done: bool, error: str):
    print(json.dumps({
        "event": "step",
        "step": step,
        "action": action,
        "reward": reward,
        "done": done,
        "error": error
    }))


def log_end(score: float, success: bool):
    print(json.dumps({
        "event": "end",
        "score": score,
        "success": success
    }))

def generate_sql_query(task_description: str, broken_query: str, schema: str):
    prompt = f"""
You are an expert SQL assistant.

Fix the SQL query based on the task.

Return ONLY JSON:
{{"query": "<fixed_sql_query>"}}

Task:
{task_description}

Schema:
{schema}

Broken Query:
{broken_query}
"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except Exception:
        return {"query": broken_query}  # fallback
    
# print("API KEY:", os.getenv("GROQ_API_KEY"))

def run_task(task_id: str):
    client = EnvClient()

    # Reset environment
    result = client.reset(task_id)
    obs = result["observation"]

    log_start(task=task_id, env="sql_query_env", model="llama-3.1-8b-instant")

    max_steps = 4  # IMPORTANT (keeps API usage low)

    for step in range(1, max_steps + 1):
        # Generate SQL using LLM
        llm_output = generate_sql_query(
            task_description=obs["task_description"],
            broken_query=obs["broken_query"],
            schema=obs["schema"]
        )

        query = llm_output.get("query", obs["broken_query"])

        # Send to environment
        result = client.step(query=query, task_id=task_id)

        reward = result["reward"]
        done = result["done"]
        error = result["observation"]["error_message"]

        # Log step
        log_step(
            step=step,
            action=query,
            reward=reward,
            done=done,
            error=error
        )

        # Update observation
        obs = result["observation"]

        # Stop early if solved
        if done:
            break

    final_score = obs["best_score_so_far"]
    success = final_score == 1.0

    log_end(score=final_score, success=success)