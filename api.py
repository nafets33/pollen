import os
import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import argparse
from dotenv import load_dotenv

from chess_piece import fastapi_router
from chess_piece.fastapi_queen import load_bishop_data

load_dotenv()
prod = True
pg_migration = os.getenv('pg_migration', 'True').lower() == 'true'

# ✅ Simple global cache - just a dict
CACHE = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load cache on startup, clear on shutdown."""
    
    # ✅ STARTUP - Load BISHOP
    print("🚀 Loading BISHOP cache...")
    try:
        # ticker_info = load_bishop_data(prod)
        ticker_info = {}
        print(f"BISHOP ticker_info loaded: {len(ticker_info)} records")
        CACHE['BISHOP'] = {'ticker_info': ticker_info}
        print(f"BISHOP loaded: {list(CACHE['BISHOP'].keys())}")
    except Exception as e:
        print(f"❌ Failed to load BISHOP: {e}")
        CACHE['BISHOP'] = {}
    
    yield  # App runs
    
    # SHUTDOWN - Clear cache
    print("👋 Clearing cache...")
    CACHE.clear()

# Create app
app = FastAPI(title="Pollen API", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(fastapi_router.router)

# Root
@app.get("/")
def root():
    return {
        "message": "Pollen API",
        "bishop_loaded": 'BISHOP' in CACHE and CACHE['BISHOP'] is not None
    }

# Get BISHOP summary
@app.get("/cache/bishop")
def get_bishop():
    """Get BISHOP cache summary."""
    if 'BISHOP' not in CACHE or not CACHE['BISHOP']:
        return {"error": "BISHOP not loaded"}
    
    BISHOP = CACHE['BISHOP']
    return {
        "keys": list(BISHOP.keys()),
        "ticker_info": BISHOP.get('ticker_info', [])
    }

# Get specific BISHOP key ## NOT USED CURRENTLY
@app.get("/cache/bishop/{key}")
def get_bishop_key(key: str):
    """Get specific BISHOP data (e.g., ticker_info, 2025_Screen)."""
    if 'BISHOP' not in CACHE or not CACHE['BISHOP']:
        return {"error": "BISHOP not loaded"}
    
    BISHOP = CACHE['BISHOP']
    
    if key not in BISHOP:
        return {
            "error": f"Key '{key}' not found",
            "available": list(BISHOP.keys())
        }
    
    data = BISHOP[key]
    
    # Convert DataFrame to dict
    if hasattr(data, 'to_dict'):
        return {"data": data.to_dict('records')}
    
    return {"data": data}

if __name__ == '__main__':
    API_URL = os.getenv('fastAPI_url', 'http://localhost:8000')
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', default=API_URL.split("://")[1].split(":")[0])
    parser.add_argument('-port', default=API_URL.split(":")[2])

    args = parser.parse_args()
    
    print(f"🌐 Starting at http://{args.ip}:{args.port}")
    uvicorn.run(app, host=args.ip, port=int(args.port))
