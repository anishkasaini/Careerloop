from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, matching, students, skills, resume, opportunities

app = FastAPI(
    title="CareerLoop AI API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(matching.router)
app.include_router(students.router)
app.include_router(skills.router)
app.include_router(resume.router)
app.include_router(opportunities.router)


@app.get("/")
def root():
    return {
        "message": "CareerLoop AI Backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }