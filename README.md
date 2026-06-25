# AI-Powered Job Matching System
Zach Poettker | CS325 | Project 1

## Overview
This project is an AI-powered job matching pipeline that fetches software engineering job postings from the Adzuna Jobs API, embeds them alongside a resume using OpenAI's text-embedding-3-small model, and ranks the jobs by cosine similarity to identify the best matches.

---

## Approach

### 1. Data Acquisition
For acquiring job postings, I decided to go with the [Adzuna Jobs API](https://developer.adzuna.com), which is a publicly available RESTful API that provides structured job listing data for major cities in the US, including St. Louis, MO. For this decision I considered using web scraping or a public job API, but ultimately decided on using an API for the following reasons: 1. Web scraping is more challenging to implement correctly, 2. It requires more maintenance and is more fragile — if a website changes its HTML format it can break everything, and 3. A lot of major job boards explicitly prohibit automated scraping in their Terms of Service, so using an official API seemed more appropriate for this project. Each job posting is saved as an individual JSON file in a `jobs/` folder.

### 2. Data Preprocessing
Raw data from an API is usually not ready to feed directly into a machine learning model. Before embedding, both the job postings and the resume go through cleaning and preparation to ensure the embedding model receives the highest quality input possible.

For job postings, the primary concern is that API responses may have residual HTML left over from the descriptions that we do not want fed to the model. I strip these using Python's string tools, normalize the whitespace by collapsing multiple spaces, tabs, and newlines into clean single spaces, and concatenate the job title and description into a single string.

For the resume, the approach is a little different. The resume is stored as a plain text file and preprocessing focuses on extracting the sections most relevant to job matching: Experience, Skills, Education, Projects, and Relevant Coursework. Sections like contact information are stripped, as they add no meaningful content for the purposes of comparing to job postings. The extracted sections are then joined into a single continuous text block that serves as the input to the embedding model.

### 3. Embedding Pipeline
The embedding pipeline is the step that converts text into something a computer can mathematically compare. When a piece of text is passed through the embedding model, it is transformed into a long list of numbers — in this case 1536 numbers — that represent the meaning of the text. I researched and considered several options before settling on OpenAI's `text-embedding-3-small` model. Google's Gemini embedding model is a strong alternative, but requires setting up a separate API account and learning a different library. Free open source options like HuggingFace also exist, but require substantial local processing time. I selected OpenAI because it hits the right balance for this project: it is easy to set up, well documented, and very cheap at this scale.

To use the API efficiently, all job posting texts are sent in a single batched request rather than one call per job, which reduces both processing time and API usage.

### 4. Similarity Engine
With embeddings generated for both the resume and job postings, the final step is to compare them and determine which jobs are most similar. I considered two methods: Euclidean distance and cosine similarity. Euclidean distance measures the straight-line distance between two points in space, but it is poorly suited for text embeddings because it is sensitive to vector magnitude — longer texts tend to produce larger vectors, which would introduce a bias based on text length rather than actual content relevance.

I chose cosine similarity instead because rather than measuring distance between two vectors, it measures the angle between them. Two vectors pointing in the same direction will have a cosine similarity of 1 regardless of their magnitudes, making it completely insensitive to text length. The formula is:

```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```

The result is a value between 0 and 1, where values closer to 1 indicate stronger similarity. All scores are collected, sorted in descending order, and the top 10 results are printed with their job title, company name, and similarity score.

---

## Results
The pipeline outputs a ranked table of the 10 most relevant job postings for the given resume:

```
----- Top 10 Matching Jobs -----

#    Score    Title                                         Company
-------------------------------------------------------------------------------------------
1    0.4497   Software Engineer II                          Indeed
2    0.4396   Staff ML Software Engineer                    Indeed
3    0.4280   C++ Software Engineer                         London Stock Exchange Group
...
```

---

## Installation

**Requirements:** Python 3.9+

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd Project-1A
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your API keys:
   ```
   ADZUNA_APP_ID=your_app_id_here
   ADZUNA_APP_KEY=your_app_key_here
   OPENAI_API_KEY=your_openai_key_here
   ```
   - Adzuna API keys: [developer.adzuna.com](https://developer.adzuna.com)
   - OpenAI API key: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

5. Add your resume as plain text in `resume.txt` in the project root.

---

## Usage

Run the pipeline:
```bash
python main.py
```

On first run, you will be prompted to choose how many pages of jobs to fetch (20 jobs per page). The jobs are saved to the `jobs/` folder and reused on future runs.

Delete the folder to re-fetch fresh listings.
