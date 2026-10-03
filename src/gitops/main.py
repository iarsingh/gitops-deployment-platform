from fastapi import FastAPI
from gitops.compare import compare

app = FastAPI()

@app.post("/compare")
def post_compare(body: dict):
    return compare(body["desired"], body["observed"])
