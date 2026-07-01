import numpy as np


class JobMatcher:
    def cosine_similarity(self, a, b):
        a = np.array(a)  # Convert list a into a NumPy array so we can do math on it
        b = np.array(b)  # Convert list b into a NumPy array so we can do math on it
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def rank(self, jobs, resume_embedding, job_embeddings):
        scored = []
        for i, job in enumerate(jobs):  # Loop through each job
            score = self.cosine_similarity(resume_embedding, job_embeddings[i])
            scored.append((score, i))
        scored.sort(reverse=True)
        return scored
