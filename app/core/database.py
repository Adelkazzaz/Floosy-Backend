from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from fastapi import FastAPI
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient = None

async def connect_to_mongo(app: FastAPI) -> AsyncGenerator:
    global client
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        app.state.database = client[settings.DATABASE_NAME]
        await client.admin.command('ping')
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
    yield
    await close_mongo_connection(app)

async def close_mongo_connection(app: FastAPI):
    global client
    if client:
        client.close()

async def get_database() -> AsyncIOMotorDatabase:
    return client[settings.DATABASE_NAME]
