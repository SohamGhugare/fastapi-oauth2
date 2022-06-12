from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def index():
    return "Hello World"

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)
