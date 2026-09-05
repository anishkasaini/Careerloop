"""
Core module for Skill Gap Analysis and Learning Recommendation Engine.
"""

from typing import List, Dict, Any, Optional
import numpy as np

from app.core.normalization import normalize_skill_set, normalize_skill
from app.core.semantic_matching import (
    compute_semantic_matching,
    get_embedding_model,
    compute_cosine_similarity,
    DEFAULT_SIMILARITY_THRESHOLD
)

# Curated recommendation catalog for high-demand technical skills
RECOMMENDATION_CATALOG = {
    "docker": "Learn Docker fundamentals, including images, containers, Dockerfiles, volumes, and basic Docker Compose.",
    "postgresql": "Learn PostgreSQL fundamentals, relational database concepts, SQL queries, joins, indexes, and database design.",
    "python": "Learn Python programming core concepts, data structures, object-oriented design, and standard libraries.",
    "fastapi": "Learn FastAPI fundamentals, Pydantic validation, async endpoints, dependency injection, and RESTful API architecture.",
    "sql": "Learn SQL query writing, relational schemas, aggregation, joins, subqueries, and database indexing.",
    "git": "Learn Git version control, branching workflows, merging, rebasing, pull requests, and collaborative repository management.",
    "aws": "Learn AWS cloud essentials, including EC2 compute, S3 storage, IAM security policies, and cloud deployment practices.",
    "machine learning": "Learn Machine Learning fundamentals, supervised and unsupervised algorithms, evaluation metrics, and model pipelines.",
    "scikit-learn": "Learn scikit-learn for model building, preprocessing pipelines, cross-validation, and hyperparameter tuning.",
    "react": "Learn React fundamentals, component lifecycle, hooks (useState, useEffect), state management, and modern UI development.",
    "node.js": "Learn Node.js runtime fundamentals, asynchronous programming, Express/Fastify frameworks, and backend API creation.",
    "javascript": "Learn modern JavaScript (ES6+), DOM manipulation, promises, async/await, and modular programming.",
    "typescript": "Learn TypeScript static typing, interfaces, generics, type guards, and integration with modern frameworks.",
    "rest api": "Learn RESTful API principles, HTTP methods, status codes, payload design, and API authentication patterns.",
    "kubernetes": "Learn Kubernetes architecture, Pods, Deployments, Services, ConfigMaps, and cluster container orchestration.",
    "mongodb": "Learn MongoDB NoSQL concepts, document data modeling, aggregation pipelines, and CRUD operations.",
    "redis": "Learn Redis in-memory data structures, caching strategies, pub/sub messaging, and session storage.",
    "linux": "Learn Linux command line navigation, shell scripting, file permissions, and system administration essentials.",
    "pandas": "Learn pandas for tabular data manipulation, data cleaning, filtering, grouping, merging, and exploratory data analysis.",
    "numpy": "Learn NumPy multidimensional arrays, vectorized operations, linear algebra functions, and numerical computing.",
    "tensorflow": "Learn TensorFlow framework, building neural network architectures, loss functions, training loops, and Keras APIs.",
    "pytorch": "Learn PyTorch tensors, autograd, custom neural network modules, DataLoader pipelines, and GPU acceleration.",
    "django": "Learn Django web framework, ORM, models, views, templates, forms, and administrative tools.",
    "flask": "Learn Flask microframework, routing, request handling, blueprints, and lightweight REST API construction.",
    "ci/cd": "Learn CI/CD automation principles, pipeline configuration (such as GitHub Actions), automated testing, and deployment workflows.",
    "graphql": "Learn GraphQL schema definition, queries, mutations, resolvers, and API client integration.",
    "c++": "Learn modern C++ (C++11/14/17), object-oriented design, memory management, pointers, and the Standard Template Library (STL).",
    "java": "Learn Java object-oriented principles, JVM architecture, collections framework, multithreading, and design patterns."
}


def get_recommendation_for_skill(skill: str) -> str:
    """
    Returns specific learning guidance for a skill from the catalog,
    or a structured generic recommendation if not cataloged.
    """
    normalized = normalize_skill(skill)
    if normalized in RECOMMENDATION_CATALOG:
        return RECOMMENDATION_CATALOG[normalized]
    return f"Develop practical experience with {normalized} through documentation, guided projects, and hands-on practice."


def prioritize_missing_skills(
    missing_skills: List[str],
    student_skills: List[str]
) -> List[Dict[str, Any]]:
    """
    Prioritizes missing skills based on whether the student has any adjacent/foundational
    skills (semantic relationship) or no related background whatsoever.

    Returns a list of dicts:
    [
        {
            "skill": str,
            "priority": "high" | "medium",
            "reason": str,
            "max_similarity": float
        }
    ]
    """
    if not missing_skills:
        return []

    if not student_skills:
        # If student has no skills at all, all missing skills are high priority
        return [
            {
                "skill": s,
                "priority": "high",
                "reason": "Directly required with no related student background",
                "max_similarity": 0.0
            }
            for s in sorted(missing_skills)
        ]

    try:
        model = get_embedding_model()
        missing_embeddings = model.encode(missing_skills, convert_to_numpy=True)
        student_embeddings = model.encode(student_skills, convert_to_numpy=True)

        prioritized = []
        for idx, missing_skill in enumerate(missing_skills):
            m_vec = missing_embeddings[idx]
            max_sim = 0.0
            best_stud = ""

            for s_idx, s_skill in enumerate(student_skills):
                s_vec = student_embeddings[s_idx]
                sim = compute_cosine_similarity(m_vec, s_vec)
                if sim > max_sim:
                    max_sim = sim
                    best_stud = s_skill

            # If student has adjacent knowledge (e.g. 0.30 <= sim < threshold), medium priority
            # If zero/low knowledge (sim < 0.30), high priority pure gap
            if max_sim >= 0.30:
                priority = "medium"
                reason = f"Adjacent foundational knowledge exists in student profile ({best_stud})"
            else:
                priority = "high"
                reason = "Directly required with no related student background"

            prioritized.append({
                "skill": missing_skill,
                "priority": priority,
                "reason": reason,
                "max_similarity": round(float(max_sim), 4)
            })

        # Sort: 'high' priority first, then 'medium', then alphabetically
        priority_order = {"high": 0, "medium": 1}
        prioritized.sort(key=lambda x: (priority_order.get(x["priority"], 2), x["skill"]))
        return prioritized

    except Exception:
        # Fallback if embedding model cannot be loaded
        return [
            {
                "skill": s,
                "priority": "high",
                "reason": "Directly required skill",
                "max_similarity": 0.0
            }
            for s in sorted(missing_skills)
        ]


def analyze_skill_gap(
    student_skills: List[str],
    required_skills: List[str],
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
) -> Dict[str, Any]:
    """
    Performs end-to-end skill gap analysis and generates learning recommendations.

    Returns:
    {
        "exact_matches": List[str],
        "semantic_matches": List[Dict[str, Any]],
        "missing_skills": List[str],
        "skill_gap_percentage": float,
        "recommendations": List[Dict[str, Any]]
    }
    """
    norm_student_set = normalize_skill_set(student_skills)
    norm_required_set = normalize_skill_set(required_skills)

    norm_student_skills = sorted(list(norm_student_set))
    norm_required_skills = sorted(list(norm_required_set))

    if not norm_required_skills:
        return {
            "exact_matches": [],
            "semantic_matches": [],
            "missing_skills": [],
            "skill_gap_percentage": 0.0,
            "recommendations": []
        }

    # Step 1: Compute matching using Phase 3 semantic engine
    matching_result = compute_semantic_matching(
        student_skills=norm_student_skills,
        required_skills=norm_required_skills,
        similarity_threshold=similarity_threshold
    )

    exact_matches = matching_result["exact_matches"]
    semantic_matches = matching_result["semantic_matches"]
    unmatched_required = matching_result["unmatched_required_skills"]
    combined_score = matching_result["combined_match_score"]

    # Step 2: Skill gap percentage
    # exact matches cover 100%, semantic matches partially bridge gap by similarity score
    skill_gap_percentage = round(max(0.0, (1.0 - combined_score) * 100), 2)

    # Step 3: Prioritize missing skills
    prioritized_info = prioritize_missing_skills(
        missing_skills=unmatched_required,
        student_skills=norm_student_skills
    )

    prioritized_missing_skills = [item["skill"] for item in prioritized_info]

    # Step 4: Generate recommendations for missing skills
    recommendations = []
    for item in prioritized_info:
        skill_name = item["skill"]
        rec_text = get_recommendation_for_skill(skill_name)
        recommendations.append({
            "skill": skill_name,
            "priority": item["priority"],
            "reason": item["reason"],
            "recommendation": rec_text
        })

    return {
        "exact_matches": exact_matches,
        "semantic_matches": semantic_matches,
        "missing_skills": prioritized_missing_skills,
        "skill_gap_percentage": skill_gap_percentage,
        "recommendations": recommendations
    }
