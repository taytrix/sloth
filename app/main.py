from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import hashlib

app = FastAPI()

HUD_SECRET = "bozo"  # This should be stored securely in a real application

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Extract query parameters
    params = dict(request.query_params)
    avatar_key = params.get('avatar_key', 'N/A')
    username = params.get('username', 'N/A')
    displayname = params.get('displayname', 'N/A')
    received_hmac = params.get('hmac_signature', 'N/A')

    # Verify HMAC (without timestamp)
    message = avatar_key + username + displayname
    expected_hmac = hashlib.sha256((message + HUD_SECRET).encode()).hexdigest()
    
    hmac_verified = received_hmac == expected_hmac

    # Debug logging
    print(f"Message: '{message}'")
    print(f"Expected HMAC: {expected_hmac}")
    print(f"Received HMAC: {received_hmac}")

    html_content = f"""
    <html>
        <head>
            <title>HUD Auth Test</title>
        </head>
        <body>
            <h1>HUD Auth Test</h1>
            <p>Avatar Key: {avatar_key}</p>
            <p>Username: {username}</p>
            <p>Display Name: {displayname}</p>
            <p>HMAC Signature: {received_hmac}</p>
            <p>HMAC Verified: {'Yes' if hmac_verified else 'No'}</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.head("/")
async def head():
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)