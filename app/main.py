from fastapi import FastAPI
from handlers import hud  # Changed to relative import

app = FastAPI()

@app.get("/")
async def root(encrypted_data: str = ""):
    return await hud.handle_auth(encrypted_data)

@app.head("/")
async def head():
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)