import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import contacts, auth, users
from src.conf.config import settings
from fastapi_limiter import FastAPILimiter
from contextlib import asynccontextmanager
import asyncio

import sys
import os
sys.path.append(os.getcwd())

async def startup():
    """
    Initialize the connection to Redis. Allows to use Redis to store rate limit information.
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)

        
@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Background task starts at statrup """
    asyncio.create_task(startup())
    yield

app = FastAPI(lifespan=lifespan)

origins = [ 
    "http://localhost:3000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')

@app.get("/")
def read_root():
    """
    Just a root route for funsies.

    Returns:
        dict: Simple Hello World sentence.
    """
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)
    