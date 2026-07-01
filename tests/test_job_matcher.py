from job_matcher import JobMatcher

matcher = JobMatcher()


def test_rank_returns_sorted_results():
    # rank() should return jobs sorted from highest to lowest score
    jobs = [{"title": "Job A"}, {"title": "Job B"}, {"title": "Job C"}]
    resume_embedding = [1.0, 0.0, 0.0]
    job_embeddings = [
        [0.5, 0.5, 0.0],  # medium match
        [1.0, 0.0, 0.0],  # perfect match
        [0.0, 1.0, 0.0],  # low match
    ]
    ranked = matcher.rank(jobs, resume_embedding, job_embeddings)

    scores = [score for score, _ in ranked] # extract just the scores and leave the job index
    assert scores == sorted(scores, reverse=True)  # scores should go from high to low
