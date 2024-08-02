from typing import Union

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


async def upsert_table(
        db: AsyncSession,
        table, datum: dict, index_elements: list, do_update=False
):
    stmt = insert(table).values(datum)
    if do_update:
        stmt = stmt.on_conflict_do_update(
            index_elements=index_elements,
            set_={**datum, "modified_at": func.now()}
        )
    else:
        stmt = stmt.on_conflict_do_nothing(
            index_elements=index_elements
        )
    return await db.execute(stmt)


