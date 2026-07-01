import os
import json
import requests


class JobFetcher:
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def fetch(self, pages):
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": 20,
            "what": "software engineer",
            "where": "Saint Louis, Missouri",
        }

        os.makedirs("jobs", exist_ok=True)  # Create job folder if it doesn't exist
        all_jobs = []
        for page in range(1, pages + 1):
            url = f"https://api.adzuna.com/v1/api/jobs/us/search/{page}"
            response = requests.get(url, params=params)
            all_jobs += response.json()["results"]
            print(f"Fetched page {page}")

        for i, job in enumerate(all_jobs):  # Loop over every job we fetched
            filename = f"job_{i + 1:02d}.json"
            path = f"jobs/{filename}"
            with open(path, 'w') as f:
                json.dump(job, f, indent=2)
            print(f"Saved {filename}: {job['title']} @ {job['company']['display_name']}")

        print(f"\nFetched {len(all_jobs)} jobs")
        return all_jobs
