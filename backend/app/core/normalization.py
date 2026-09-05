import re
from typing import Iterable, Set, List

# Extensible dictionary mapping skill aliases and variations to canonical skill names
SKILL_ALIASES = {
    # Python variations
    "python": "python",
    "python 3": "python",
    "python3": "python",
    "python programming": "python",
    "py": "python",

    # Machine Learning / AI variations
    "ml": "machine learning",
    "machine learning": "machine learning",
    "ml/ai": "machine learning",
    "ai/ml": "machine learning",
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",

    # JavaScript variations
    "js": "javascript",
    "javascript": "javascript",

    # TypeScript variations
    "ts": "typescript",
    "typescript": "typescript",

    # React variations
    "react": "react",
    "reactjs": "react",
    "react.js": "react",
    "react native": "react native",

    # Node.js variations
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",

    # PostgreSQL variations
    "postgres": "postgresql",
    "postgresql": "postgresql",

    # Scikit-learn variations
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "scikit-learn": "scikit-learn",

    # C / C++ / C# / .NET variations
    "c++": "c++",
    "cpp": "c++",
    "c#": "c#",
    "csharp": "c#",
    ".net": ".net",
    "dotnet": ".net",
    ".net core": ".net",

    # Database variations
    "mongo": "mongodb",
    "mongodb": "mongodb",
    "sql": "sql",
    "mysql": "mysql",
    "nosql": "nosql",

    # REST API variations
    "rest": "rest api",
    "rest api": "rest api",
    "rest apis": "rest api",
    "restful api": "rest api",
    "restful apis": "rest api",

    # Other common tech aliases
    "golang": "go",
    "go": "go",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "docker": "docker",
    "aws": "aws",
    "amazon web services": "aws",
    "gcp": "google cloud platform",
    "vue": "vue.js",
    "vuejs": "vue.js",
    "vue.js": "vue.js",
    "tf": "tensorflow",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch"
}


def normalize_skill(raw_skill: str) -> str:
    """
    Normalizes a single skill string:
    1. Trims whitespace and converts to lower case.
    2. Removes unwanted surrounding punctuation while preserving meaningful
       tech symbols like '+', '#', '.', '-'.
    3. Maps known aliases/synonyms to canonical skill names.
    """
    if not raw_skill:
        return ""

    # 1. Lowercase & strip leading/trailing whitespace
    cleaned = raw_skill.strip().lower()

    # 2. Collapse internal multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # 3. Strip surrounding trailing/leading noise punctuation (e.g. "python,", "react.")
    #    without stripping meaningful prefix/suffix chars like in '.net', 'c++', 'c#'
    cleaned = re.sub(r'^[^\w.+#-]+|[^\w.+#-]+$', '', cleaned)

    if not cleaned:
        return ""

    # 4. Lookup in alias dictionary
    return SKILL_ALIASES.get(cleaned, cleaned)


def normalize_skill_set(skills: Iterable[str]) -> Set[str]:
    """
    Normalizes an iterable of raw skill strings and returns a deduplicated set
    of canonical skill names.
    """
    normalized_set = set()
    for s in skills:
        norm = normalize_skill(s)
        if norm:
            normalized_set.add(norm)
    return normalized_set


def normalize_skill_list(skills: Iterable[str]) -> List[str]:
    """
    Normalizes an iterable of raw skill strings and returns a sorted list
    of unique canonical skill names.
    """
    return sorted(normalize_skill_set(skills))
