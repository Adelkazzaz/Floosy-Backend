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
        logger.error(f"Failed to connect to cloud MongoDB: {e}")
        try:
            # Fallback to local MongoDB
            local_uri = "mongodb://localhost:27017"
            logger.info("Attempting to connect to local MongoDB...")
            client = AsyncIOMotorClient(local_uri)
            app.state.database = client[settings.DATABASE_NAME]
            await client.admin.command('ping')
            logger.info("Connected to local MongoDB successfully")
        except Exception as local_error:
            logger.error(f"Failed to connect to local MongoDB as well: {local_error}")
            raise Exception("Could not connect to any MongoDB instance")
        
    yield
    await close_mongo_connection(app)

async def close_mongo_connection(app: FastAPI):
    global client
    if client:
        client.close()

async def get_database() -> AsyncIOMotorDatabase:
    return client[settings.DATABASE_NAME]
