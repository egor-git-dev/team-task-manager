from fastapi import FastAPI

app = FastAPI(
    title="Team Task Manager",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
