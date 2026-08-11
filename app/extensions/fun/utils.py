import requests

API = "https://uselessfacts.jsph.pl/api/v2"


def fetch_random_fact() -> str:
    response = requests.get(f"{API}/facts/random", headers={"Accept": "application/json"})

    if not response.ok:
        raise RuntimeError(f"Error: status code {response.status_code}")

    data = response.json()
    return data.get("text")
