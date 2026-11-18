from fastapi import FastAPI
from app.routes.student import router as student_router
from app.routes.interest import router as interest_router
from app.routes.assessment import router as assessment_router
from app.routes.attempt import router as attempt_router
from app.routes.result import router as result_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Course and School Recommendation System",
    description="Backend API for recommending academic programs and matching schools in Muntinlupa City.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_router)
app.include_router(interest_router)
app.include_router(assessment_router)
app.include_router(attempt_router)
app.include_router(result_router)


@app.get("/")
def root():
    return {
        "message": "AI Course Recommendation API is running",
        "status": "success",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Course Recommendation API",
    }