from fastapi import FastAPI  # type: ignore[reportMissingImports]

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, world"}