from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime, timedelta
import asyncio

Base = declarative_base()
engine = create_async_engine("sqlite+aiosqlite:///chat.db")
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def cleanup_old_chats():
    async with AsyncSessionLocal() as session:
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        await session.execute(
            f"DELETE FROM chat_sessions WHERE created_at < '{cutoff.isoformat()}'"
        )
        await session.commit()