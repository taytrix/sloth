from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import base64
import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

HUD_SECRET = "bozo"  # This should be stored securely in a real application

def xor_base64(s1, s2):
    logger.debug(f"Entering xor_base64 function with s1 length: {len(s1)}, s2 length: {len(s2)}")
    
    # Decode base64 strings to bytes
    b1 = base64.b64decode(s1)
    b2 = base64.b64decode(s2)
    logger.debug(f"Decoded b1 length: {len(b1)}, b2 length: {len(b2)}")
    
    # Ensure b2 is at least as long as b1 by repeating it
    b2 = (b2 * (len(b1) // len(b2) + 1))[:len(b1)]
    logger.debug(f"Adjusted b2 length: {len(b2)}")
    
    # XOR the bytes
    xored = bytes(a ^ b for a, b in zip(b1, b2))
    logger.debug(f"XORed result length: {len(xored)}")
    
    # Return the result as base64
    result = base64.b64encode(xored).decode()
    logger.debug(f"Returning base64 result with length: {len(result)}")
    return result

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    logger.info("Received request at root endpoint")
    
    # Extract query parameters
    params = dict(request.query_params)
    encrypted_data = params.get('encrypted_data', '')
    logger.debug(f"Received encrypted_data: {encrypted_data[:20]}...")  # Log first 20 chars for brevity

    # Decrypt the data
    logger.debug("Starting decryption process")
    secret_base64 = base64.b64encode(HUD_SECRET.encode()).decode()
    logger.debug(f"Secret in base64: {secret_base64}")
    
    decrypted_base64 = xor_base64(encrypted_data, secret_base64)
    logger.debug(f"Decrypted base64 data: {decrypted_base64[:20]}...")  # Log first 20 chars for brevity

    decrypted_data = base64.b64decode(decrypted_base64).decode()
    logger.debug(f"Decrypted data: {decrypted_data}")

    # Parse the JSON data
    try:
        logger.debug("Attempting to parse JSON data")
        data = json.loads(decrypted_data)
        logger.debug(f"Parsed JSON data: {data}")
        
        avatar_key = data.get('avatar_key', 'N/A')
        username = data.get('username', 'N/A')
        displayname = data.get('displayname', 'N/A')
        
        logger.info(f"Extracted data - Avatar Key: {avatar_key}, Username: {username}, Display Name: {displayname}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return HTMLResponse(content=f"Error: Invalid data format - {str(e)}", status_code=400)

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
            <p>Data successfully decrypted and parsed</p>
        </body>
    </html>
    """
    logger.info("Returning HTML response")
    return HTMLResponse(content=html_content, status_code=200)

@app.head("/")
async def head():
    logger.info("Received HEAD request")
    return {"message": "OK"}

if __name__ == "__main__":
    logger.info("Starting the FastAPI application")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)