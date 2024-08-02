from datetime import date
from typing import Optional

from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

from .base import Base


class CDE(Base):
    __tablename__ = "cde"

    code: Mapped[str] = mapped_column(unique=True)
    name: Mapped[Optional[str]]
    drug_type: Mapped[Optional[str]]
    apply_type: Mapped[Optional[str]]
    reg_type: Mapped[Optional[str]]
    pharm_name: Mapped[Optional[str]]
    accept_date: Mapped[Optional[date]]

    @declared_attr.directive
    def __table_args__(cls):
        return (
            Index(f"{cls.__tablename__}_code_idx", "code", unique=True),
        )
