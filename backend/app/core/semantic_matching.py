"""
Core module for ML/NLP semantic skill matching using sentence-transformers.
"""

import os
import ssl
from typing import List, Dict, Any, Optional
import numpy as np

from app.core.normalization import normalize_skill_set, normalize_skill

# Global singleton for lazy model loading
_model = None
DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_SIMILARITY_THRESHOLD = 0.55


def _setup_ssl_context():
    """
    Sets up SSL bypass for downloading HuggingFace model files if SSL CA bundle issues exist.
    """
    os.environ["PYTHONHTTPSVERIFY"] = "0"
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    try:
        import certifi
        os.environ["SSL_CERT_FILE"] = certifi.where()
        os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
        os.environ["CURL_CA_BUNDLE"] = certifi.where()
    except ImportError:
        pass
    try:
        import httpx
        _orig_init = httpx.Client.__init__

        def _patched_init(self, *args, **kwargs):
            kwargs["verify"] = False
            _orig_init(self, *args, **kwargs)

        httpx.Client.__init__ = _patched_init
    except Exception:
        pass
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except AttributeError:
        pass


def get_embedding_model(model_name: str = DEFAULT_MODEL_NAME):
    """
    Lazy-loads and returns the SentenceTransformer model singleton.
    """
    global _model
    if _model is None:
        _setup_ssl_context()
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(model_name)
    return _model


def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Computes cosine similarity between two 1D numpy vectors.
    """
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))


def compute_semantic_matching(
    student_skills: List[str],
    required_skills: List[str],
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    model_name: str = DEFAULT_MODEL_NAME
) -> Dict[str, Any]:
    """
    Computes semantic and exact matching between student skills and job required skills.

    Returns:
    {
        "exact_matches": List[str],
        "semantic_matches": List[Dict[str, Any]],  # {"job_skill": str, "student_skill": str, "similarity_score": float}
        "unmatched_required_skills": List[str],
        "exact_match_score": float,  # 0.0 to 1.0
        "combined_match_score": float  # 0.0 to 1.0
    }
    """
    # Step 1: Normalize input skill sets
    norm_student_skills_set = normalize_skill_set(student_skills)
    norm_required_skills_set = normalize_skill_set(required_skills)

    norm_student_skills = sorted(list(norm_student_skills_set))
    norm_required_skills = sorted(list(norm_required_skills_set))

    total_required_count = len(norm_required_skills)

    if total_required_count == 0:
        return {
            "exact_matches": [],
            "semantic_matches": [],
            "unmatched_required_skills": [],
            "exact_match_score": 0.0,
            "combined_match_score": 0.0
        }

    # Step 2: Exact Matching
    exact_matches = sorted(list(norm_student_skills_set.intersection(norm_required_skills_set)))

    unmatched_required = sorted(list(norm_required_skills_set - set(exact_matches)))
    unmatched_student = sorted(list(norm_student_skills_set - set(exact_matches)))

    semantic_matches: List[Dict[str, Any]] = []
    final_unmatched_required: List[str] = []

    # Step 3: Semantic Matching for remaining unmatched skills
    if unmatched_required and unmatched_student:
        model = get_embedding_model(model_name)

        # Encode unmatched skills
        student_embeddings = model.encode(unmatched_student, convert_to_numpy=True)
        required_embeddings = model.encode(unmatched_required, convert_to_numpy=True)

        available_student_indices = set(range(len(unmatched_student)))

        for req_idx, req_skill in enumerate(unmatched_required):
            req_vec = required_embeddings[req_idx]
            best_score = -1.0
            best_stud_idx = -1

            for stud_idx in available_student_indices:
                stud_vec = student_embeddings[stud_idx]
                sim = compute_cosine_similarity(req_vec, stud_vec)
                if sim > best_score:
                    best_score = sim
                    best_stud_idx = stud_idx

            if best_score >= similarity_threshold and best_stud_idx != -1:
                best_stud_skill = unmatched_student[best_stud_idx]
                semantic_matches.append({
                    "job_skill": req_skill,
                    "student_skill": best_stud_skill,
                    "similarity_score": round(float(best_score), 4)
                })
            else:
                final_unmatched_required.append(req_skill)
    else:
        final_unmatched_required = unmatched_required

    # Step 4: Scoring
    exact_match_score = round(len(exact_matches) / total_required_count, 4)

    # Combined score calculation: exact matches count full (1.0), semantic matches weighted by their similarity score
    semantic_weighted_sum = sum(m["similarity_score"] for m in semantic_matches)
    combined_match_score = round(min(1.0, (len(exact_matches) + semantic_weighted_sum) / total_required_count), 4)

    return {
        "exact_matches": exact_matches,
        "semantic_matches": semantic_matches,
        "unmatched_required_skills": sorted(final_unmatched_required),
        "exact_match_score": exact_match_score,
        "combined_match_score": combined_match_score
    }
