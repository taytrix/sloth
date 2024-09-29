from fastapi import FastAPI, Request, Response
from handlers import hud  # Changed to relative import

app = FastAPI()

@app.get("/")
async def root(request: Request, response: Response):
    return await hud.handle_auth(request, response)

@app.head("/")
async def head():
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)