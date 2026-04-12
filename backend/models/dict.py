from sqlalchemy import String, Date, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.base import DictBase


class DictPerson(DictBase, Base):
    __tablename__ = "dict_person"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    id_card: Mapped[str] = mapped_column(String(18), unique=True, nullable=False)
    birth_date: Mapped[str | None] = mapped_column(Date)
    join_date: Mapped[str | None] = mapped_column(Date)
    position: Mapped[str | None] = mapped_column(String(50))
    department: Mapped[str | None] = mapped_column(String(50))
    employment_type: Mapped[str | None] = mapped_column(String(30))
    school: Mapped[str | None] = mapped_column(String(100))
    degree: Mapped[str | None] = mapped_column(String(30))
