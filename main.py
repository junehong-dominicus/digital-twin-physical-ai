from fastapi import FastAPI

app = FastAPI(title="LLM Digital Twin API")

@app.get("/")
def root():
    return {"status": "Digital Twin Online"}