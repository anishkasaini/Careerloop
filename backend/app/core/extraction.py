import re
from typing import List, Set
from app.core.normalization import normalize_skill

# Comprehensive skills taxonomy including canonical names, aliases, and common variations
EXTRACTION_TAXONOMY = [
    # Programming Languages
    "python", "python 3", "python3", "python programming", "py",
    "javascript", "js", "typescript", "ts",
    "c++", "cpp", "c#", "csharp", "c", "java", "ruby", "php", "swift", "kotlin", "go", "golang", "rust", "scala",

    # Frameworks & Libraries
    "fastapi", "flask", "django", "react", "reactjs", "react.js", "react native",
    "vue", "vuejs", "vue.js", "angular", "angularjs", "node", "nodejs", "node.js", "express", "expressjs",
    "next.js", "nextjs", "nuxt", "spring", "spring boot", ".net", "dotnet", ".net core",
    "html", "css", "bootstrap", "tailwind", "tailwind css",

    # AI / ML / Data Science
    "machine learning", "ml", "ml/ai", "ai/ml", "artificial intelligence", "ai",
    "deep learning", "data science", "natural language processing", "nlp",
    "computer vision", "cv", "neural networks", "reinforcement learning",
    "scikit-learn", "sklearn", "scikit learn", "tensorflow", "tf", "pytorch", "keras",
    "numpy", "pandas", "matplotlib", "seaborn", "scipy", "opencv", "spacy", "nltk",

    # Databases & Storage
    "sql", "mysql", "postgresql", "postgres", "sqlite", "mongodb", "mongo",
    "redis", "elasticsearch", "cassandra", "dynamodb", "oracle", "mariadb", "nosql",

    # DevOps, Cloud & Tools
    "docker", "kubernetes", "k8s", "aws", "amazon web services", "gcp", "google cloud platform", "azure",
    "git", "github", "gitlab", "bitbucket", "ci/cd", "jenkins", "terraform", "ansible",
    "linux", "bash", "shell", "unix", "nginx", "apache",

    # Architecture & Concepts
    "rest api", "rest apis", "restful api", "restful apis", "rest", "graphql", "microservices",
    "agile", "scrum", "jira", "oop", "object oriented programming", "unit testing", "system design"
]


def extract_skills_from_text(raw_text: str) -> List[str]:
    """
    Extracts tech skills from raw text (job description or resume):
    1. Scans text for terms using strict boundary regex patterns to prevent
       false positive substring matches (e.g. 'sql' inside 'mysql' or 'postgresql').
    2. Preserves special tech characters like '+', '#', '.', '-'.
    3. Normalizes each extracted skill using app.core.normalization.
    4. Returns a sorted list of unique canonical skill names.
    """
    if not raw_text:
        return []

    found_skills: Set[str] = set()

    # Sort taxonomy by length descending so multi-word terms are evaluated first
    sorted_taxonomy = sorted(set(EXTRACTION_TAXONOMY), key=len, reverse=True)

    for term in sorted_taxonomy:
        # Construct strict boundary pattern according to term structure
        if term.startswith('.'):
            prefix = r'(?<![a-zA-Z0-9])'
        else:
            prefix = r'(?<![a-zA-Z0-9#+.])'

        suffix = r'(?![a-zA-Z0-9#+])'
        pattern = prefix + re.escape(term) + suffix

        if re.search(pattern, raw_text, re.IGNORECASE):
            norm = normalize_skill(term)
            if norm:
                found_skills.add(norm)

    return sorted(found_skills)
