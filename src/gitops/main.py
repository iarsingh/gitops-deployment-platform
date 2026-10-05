from gitops.ops import router as ops_router
from fastapi import FastAPI
from gitops.compare import compare

app = FastAPI()
app.include_router(ops_router, prefix="/v1")

@app.post("/compare")
def post_compare(body: dict):
    return compare(body["desired"], body["observed"])
