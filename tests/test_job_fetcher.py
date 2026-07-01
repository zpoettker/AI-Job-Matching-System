import shutil
from unittest.mock import patch, MagicMock
from job_fetcher import JobFetcher

fetcher = JobFetcher(app_id="fake_id", app_key="fake_key")


def fake_response(): # fake API response that looks like what Adzuna actually returns
    mock = MagicMock()
    mock.json.return_value = {
        "results": [
            {"title": "Software Engineer", "company": {"display_name": "Test Corp"}, "description": "Python job"}
        ]
    }
    return mock


@patch("job_fetcher.requests.get") # Temporarily replace requests.get with a mock object for this test
def test_fetch_returns_jobs(mock_get):
    mock_get.return_value = fake_response()
    jobs = fetcher.fetch(pages=1)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Software Engineer"
    shutil.rmtree("jobs", ignore_errors=True)  # Remove jobs folder after test