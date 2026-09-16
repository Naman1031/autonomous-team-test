import string
import urllib.parse
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="URL Shortener API")

db_urls = {}
db_id_counter = 1000

BASE62_ALPHABET = string.ascii_letters + string.digits

def base62_encode(num: int) -> str:
    if num == 0:
        return BASE62_ALPHABET[0]
    arr = []
    base = len(BASE62_ALPHABET)
    while num > 0:
        rem = num % base
        arr.append(BASE62_ALPHABET[rem])
        num = num // base
    return "".join(reversed(arr))

def is_valid_url(url: str) -> bool:
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme in ["http", "https"], result.netloc])
    except Exception:
        return False

class ShortenRequest(BaseModel):
    url: str

class ShortenResponse(BaseModel):
    short_code: str
    long_url: str

@app.post("/api/v1/shorten", status_code=status.HTTP_201_CREATED, response_model=ShortenResponse)
def shorten_url(payload: ShortenRequest):
    if not is_valid_url(payload.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format"
        )
    
    global db_id_counter
    for code, stored_url in db_urls.items():
        if stored_url == payload.url:
            return ShortenResponse(short_code=code, long_url=payload.url)
            
    short_code = base62_encode(db_id_counter)
    db_id_counter += 1
    db_urls[short_code] = payload.url
    
    return ShortenResponse(short_code=short_code, long_url=payload.url)
