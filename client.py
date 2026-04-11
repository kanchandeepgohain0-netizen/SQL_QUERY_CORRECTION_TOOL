import requests


class EnvClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url

    def reset(self, task_id: str):
        response = requests.post(
            f"{self.base_url}/reset",
            params={"task_id": task_id}
        )
        return response.json()
    
    def step(self, query: str, task_id: str):
        response = requests.post(
            f"{self.base_url}/step",
            json={
                "query": query,
                "task_id": task_id
            }
        )
        return response.json()
    
    def state(self):
        response = requests.get(
            f"{self.base_url}/state"
        )
        return response.json()