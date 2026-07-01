import re


class TextPreprocessor:
    KEEP_SECTIONS = ['EDUCATION', 'RELEVANT COURSEWORK', 'TECHNICAL SKILLS', 'PROJECTS', 'EXPERIENCE']

    def clean(self, text):
        text = re.sub(r'<[^>]+>', ' ', text)  # Strip HTML tags
        text = re.sub(r'\s+', ' ', text).strip()  # Shorten all whitespace into single spaces
        return text.lower()

    def process_job(self, job):
        return self.clean(f"{job['title']} {job['description']}")

    def process_resume(self, path):
        with open(path, 'r') as f:
            raw = f.read()
        sections = re.split(r'\n(?=[A-Z][A-Z\s]+:)', raw)  # Split on section headers
        kept = []
        for section in sections:
            header = section.split(':')[0].strip().upper()  # Grab just the header text and uppercase it
            if any(keep in header for keep in self.KEEP_SECTIONS):
                kept.append(section)
        return self.clean(' '.join(kept))
