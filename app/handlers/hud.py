from fastapi import HTTPException, Request, Response
from fastapi.responses import HTMLResponse
import base64
import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

HUD_SECRET = "bozo"  # This should be stored securely in a real application

# MAIN HANDLER

async def handle_auth(request: Request, response: Response) -> Response:
    logger.info("Handling HUD auth request")
    logger.debug(f"Request headers: {request.headers}")
    logger.debug(f"Request cookies: {request.cookies}")

    encrypted_data = request.query_params.get("encrypted_data", "")
    sl_viewer_browser = request.cookies.get("sl_viewer_browser")
    logger.debug(f"sl_viewer_browser value from request: {sl_viewer_browser}")

    logger.debug(f"Received encrypted_data: {encrypted_data[:20]}...")  # Log first 20 chars for brevity

    if not encrypted_data:
        raise HTTPException(status_code=400, detail="Missing encrypted_data parameter")

    if sl_viewer_browser is None or sl_viewer_browser == "":
        logger.debug("sl_viewer_browser is None or empty, decrypting data")
        decrypted_data = decrypt_data(encrypted_data)
        parsed_data = parse_json_data(decrypted_data)
        
        cookie_value = json.dumps(parsed_data)
        set_cookie(response, "sl_viewer_browser", cookie_value)
        logger.debug(f"Cookie set in response: {cookie_value}")
    else:
        try:
            parsed_data = json.loads(sl_viewer_browser)
            logger.debug(f"Using existing cookie data: {parsed_data}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid cookie data: {e}")
            raise HTTPException(status_code=400, detail="Invalid cookie data")

    html_content = generate_html_response(parsed_data, request)

    # Set the content and headers on the existing response object
    response.body = html_content.encode()
    response.status_code = 200
    response.media_type = "text/html"

    logger.debug(f"Response headers before returning: {response.headers}")
    set_cookie_header = response.headers.get('Set-Cookie')
    logger.debug(f"Set-Cookie header before returning: {set_cookie_header}")
    
    logger.info("Returning HTML response")
    return response

# HELPERS

def set_cookie(response: Response, cookie_name: str, cookie_value: str) -> None:
    response.set_cookie(
        key=cookie_name,
        value=cookie_value,
        max_age=300,  # 5 minutes
        httponly=True,
        secure=True,
        samesite="None",
        #domain=".dix.lol",  # To allow subdomains to share the cookie
        path="/"  # Ensure it's available on all paths
    )
    logger.debug(f"Setting cookie: {cookie_name} = {cookie_value}")
    logger.debug(f"Cookie attributes - Domain: .dix.lol, Path: /, Secure: True, SameSite: None, HttpOnly: True, Max-Age: 300")
    logger.debug(f"Response headers after setting cookie: {response.headers}")




# SL is sending us XORed data so we need to decrypt it
def decrypt_data(encrypted_data: str) -> str:
    logger.debug("Starting decryption process")
    secret_base64 = base64.b64encode(HUD_SECRET.encode()).decode()
    logger.debug(f"Secret in base64: {secret_base64}")
    
    decrypted_base64 = xor_base64(encrypted_data, secret_base64)
    logger.debug(f"Decrypted base64 data: {decrypted_base64[:20]}...")  # Log first 20 chars for brevity

    decrypted_data = base64.b64decode(decrypted_base64).decode()
    logger.debug(f"Decrypted data: {decrypted_data}")
    return decrypted_data

# Inside the decrypted data is a JSON that we need to parse
def parse_json_data(decrypted_data: str) -> dict:
    try:
        logger.debug("Attempting to parse JSON data")
        data = json.loads(decrypted_data)
        logger.debug(f"Parsed JSON data: {data}")
        
        parsed_data = {
            'avatar_key': data.get('avatar_key', 'N/A'),
            'username': data.get('username', 'N/A'),
            'displayname': data.get('displayname', 'N/A')
        }
        
        logger.info(
            f"Extracted data - "
            f"Avatar Key: {parsed_data['avatar_key']}, "
            f"Username: {parsed_data['username']}, "
            f"Display Name: {parsed_data['displayname']}"
        )
        return parsed_data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")

# We need to return HTML to SL for the HUD test
def generate_html_response(parsed_data: dict, request: Request) -> str:
    html_content = f"""
    <html>
        <head>
            <title>HUD Auth Test</title>
        </head>
        <body>
            <h1>HUD Auth Test</h1>
            <h2>SL Viewer Browser Cookie:</h2>
            <pre>{json.dumps(parsed_data, indent=2)}</pre>
            <h2>All Request Headers:</h2>
            <pre>{json.dumps(dict(request.headers), indent=2)}</pre>
            <h2>All Request Cookies:</h2>
            <pre>{json.dumps(dict(request.cookies), indent=2)}</pre>
        </body>
    </html>
    """
    return html_content

# This function takes two base64 encoded strings and XORs them
def xor_base64(s1: str, s2: str) -> str:
    logger.debug(f"Entering xor_base64 function with s1 length: {len(s1)}, s2 length: {len(s2)}")
    
    b1 = base64.b64decode(s1)
    b2 = base64.b64decode(s2)
    logger.debug(f"Decoded b1 length: {len(b1)}, b2 length: {len(b2)}")
    
    b2 = (b2 * (len(b1) // len(b2) + 1))[:len(b1)]
    logger.debug(f"Adjusted b2 length: {len(b2)}")
    
    xored = bytes(a ^ b for a, b in zip(b1, b2))
    logger.debug(f"XORed result length: {len(xored)}")
    
    result = base64.b64encode(xored).decode()
    logger.debug(f"Returning base64 result with length: {len(result)}")
    return result
