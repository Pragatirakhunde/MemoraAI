from fastapi import FastAPI

app = FastAPI(
    title="Enterprise Memory Engine",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Enterprise Memory Engine API"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }