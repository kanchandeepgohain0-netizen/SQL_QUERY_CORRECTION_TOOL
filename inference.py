import os
import json
from client import EnvClient

from openai import OpenAI

import os

os.environ["MODEL_NAME"] = "openai/gpt-5.2"
os.environ["API_BASE_URL"] = "https://openrouter.ai/api/v1/chat/completions"
os.environ["HF_TOKEN"] = "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"

openai_client = OpenAI(
    base_url=os.getenv("API_BASE_URL"),
    api_key=os.getenv("HF_TOKEN")
)

def log_start(task: str, env: str, model: str):
    print("[START] " + json.dumps({
        "task": task,
        "env": env,
        "model": model
    }))


def log_step(step: int, action: str, reward: float, done: bool, error: str):
    print("[STEP] " + json.dumps({
        "step": step,
        "action": action,
        "reward": reward,
        "done": done,
        "error": error
    }))

def log_end(score: float, success: bool):
    print("[END] " + json.dumps({
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

    response = openai_client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
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

    log_start(task=task_id, env="sql_query_env", model=os.getenv("MODEL_NAME"))

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

print(os.getenv("MODEL_NAME"))
print(os.getenv("API_BASE_URL"))
print(os.getenv("HF_TOKEN"))