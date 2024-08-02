import json
from datetime import datetime
from functools import partial

from sqlalchemy import func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


engine = create_async_engine(
    "postgresql+asyncpg://postgres:Pandaaaa906~@192.168.5.247/chemhost",
    pool_pre_ping=True,
    json_serializer=partial(json.dumps, ensure_ascii=False),
)


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    modified_at: Mapped[datetime] = mapped_column(default=func.now())
