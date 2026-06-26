import os
import re
import json
from dotenv import load_dotenv
import requests
import numpy as np
from openai import OpenAI

load_dotenv()
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# PART 1: Fetch jobs with Adzuna

def fetch_jobs(pages):
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 20,
        "what": "software engineer",
        "where": "Saint Louis, Missouri",
    }

    os.makedirs("jobs", exist_ok=True) # Create job folder if it doesn't exist
    all_jobs = []
    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/us/search/{page}"
        response = requests.get(url, params=params)
        all_jobs += response.json()["results"]
        print(f"Fetched page {page}")

    for i in range(len(all_jobs)): # Loop over every job we fetched
        job = all_jobs[i]
        filename = f"job_{i + 1:02d}.json" 
        path = f"jobs/{filename}"
        with open(path, 'w') as f:
            json.dump(job, f, indent=2)
        print(f"Saved {filename}: {job['title']} @ {job['company']['display_name']}")

    print(f"\nFetched {len(all_jobs)} jobs")
    return all_jobs


# PART 2: Preprocessing jobs and resume

def clean_text(text):
    text = re.sub(r'<[^>]+>', ' ', text) # Strip HTML tags
    text = re.sub(r'\s+', ' ', text).strip() # Shorten all whitespace into single spaces
    return text.lower()

def preprocess_job(job):
    title = job['title']
    description = job['description']
    return clean_text(f"{title} {description}")

def preprocess_resume(path):
    with open(path, 'r') as f:
        raw = f.read()
    keep_sections = ['EDUCATION', 'RELEVANT COURSEWORK', 'TECHNICAL SKILLS', 'PROJECTS', 'EXPERIENCE']
    sections = re.split(r'\n(?=[A-Z][A-Z\s]+:)', raw) # Split on section headers
    kept = []
    for section in sections:
        header = section.split(':')[0].strip().upper() # Grab just the header text and uppercase it
        if any(keep in header for keep in keep_sections):
            kept.append(section)
    return clean_text(' '.join(kept))


# PART 3: Embedding

def get_embeddings(texts):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts, # Send all texts at once in a single API call
    )
    embeddings = []
    for item in response.data: # Loop through each result
        embeddings.append(item.embedding) # Pull out the vector and add it to our list
    return embeddings # return all vectors

# PART 4: Cosine Similarity

def cosine_similarity(a, b):
    a = np.array(a) # Convert list a into a NumPy array so we can do math on it
    b = np.array(b) # Convert list b into a NumPy array so we can do math on it
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def main():
    # PART 1: fetch and save jobs (skip if already done)
    if not os.path.exists("jobs"):
        pages = int(input("How many pages of jobs do you want to fetch? (20 jobs/page): "))
        fetch_jobs(pages)
    else:
        print("jobs already fetched")

    # PART 2: preprocess jobs and resume
    jobs = []
    for filename in sorted(os.listdir("jobs")): # Go through the jobs folder in alphabetical order
        if filename.endswith(".json"):
            with open("jobs/" + filename, 'r') as f:
                jobs.append(json.load(f)) # Read it and add the job data to our list

    job_texts = []
    for job in jobs: # Loop through each job
        job_texts.append(preprocess_job(job))  # Clean up the job text and add it to the list
    resume_text = preprocess_resume("resume.txt") # Clean up and extract the relevant parts of the resume
    print(f"Preprocessed {len(job_texts)} jobs and resume")

    # PART 3: embed everything in one batched API call
    all_texts = [resume_text] + job_texts
    all_embeddings = get_embeddings(all_texts)  # Convert all of them to vectors in one API call
    resume_embedding = all_embeddings[0]
    job_embeddings = []

    for i in range(1, len(all_embeddings)): # Loop through everything after the resume vector
        job_embeddings.append(all_embeddings[i]) 
    print(f"generated {len(all_embeddings)} embeddings")

    # Part 4: Score each job with cosine similarity
    scored = []
    for i in range(len(jobs)):  #Loop through each job
        score = cosine_similarity(resume_embedding, job_embeddings[i])
        scored.append((score, i))
    scored.sort(reverse=True)

    # Print top 10 matches
    print("\n \n----- Top 10 Matching Jobs ----- \n \n")
    print(f"{'#':<4} {'Score':<8} {'Title':<45} Company")
    print("-------------------------------------------------------------------------------------------")
    for i in range(10):
        score, job_index = scored[i]
        job = jobs[job_index]
        title = job['title'][:44]
        company = job['company']['display_name']
        print(f"{i + 1:<4} {score:.4f}   {title:<45} {company}")

main()
