import os
import json
from dotenv import load_dotenv

from job_fetcher import JobFetcher
from text_preprocessor import TextPreprocessor
from embedding_service import OpenAIEmbeddingService
from job_matcher import JobMatcher

load_dotenv()


def main():
    fetcher = JobFetcher(
        app_id=os.getenv("ADZUNA_APP_ID"),
        app_key=os.getenv("ADZUNA_APP_KEY"),
    )
    preprocessor = TextPreprocessor()
    embedder = OpenAIEmbeddingService(api_key=os.getenv("OPENAI_API_KEY"))
    matcher = JobMatcher()

    # PART 1: fetch and save jobs (skip if already done)
    if not os.path.exists("jobs"):
        pages = int(input("How many pages of jobs do you want to fetch? (20 jobs/page): "))
        fetcher.fetch(pages)
    else:
        print("Jobs already fetched")

    # Load jobs from disk
    jobs = []
    for filename in sorted(os.listdir("jobs")):  # Go through the jobs folder in alphabetical order
        if filename.endswith(".json"):
            with open(f"jobs/{filename}", 'r') as f:
                jobs.append(json.load(f))  # Read it and add the job data to our list

    # PART 2: preprocess jobs and resume
    job_texts = [preprocessor.process_job(job) for job in jobs]  # Clean up each job's text
    resume_text = preprocessor.process_resume("resume.txt")  # Clean up and extract the relevant parts of the resume
    print(f"Preprocessed {len(job_texts)} jobs and resume")

    # PART 3: embed everything in one batched API call
    all_embeddings = embedder.get_embeddings([resume_text] + job_texts)  # Convert all of them to vectors in one API call
    resume_embedding = all_embeddings[0]
    job_embeddings = all_embeddings[1:]  # Everything after the resume vector
    print(f"Generated {len(all_embeddings)} embeddings")

    # PART 4: Score each job with cosine similarity
    ranked = matcher.rank(jobs, resume_embedding, job_embeddings)

    # Print top 10 matches
    print("\n\n----- Top 10 Matching Jobs -----\n\n")
    print(f"{'#':<4} {'Score':<8} {'Title':<45} Company")
    print("-" * 91)
    for i in range(10):
        score, job_index = ranked[i]
        job = jobs[job_index]
        print(f"{i + 1:<4} {score:.4f}   {job['title'][:44]:<45} {job['company']['display_name']}")


main()
