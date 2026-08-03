from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, Date, DateTime, func, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

# Tabella ponte per la relazione Many-to-Many tra Entries e Tags
entry_tags = Table(
    "entry_tags",
    Base.metadata,
    Column("entry_id", ForeignKey("entries.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

entry_habits = Table(
    "entry_habits",
    Base.metadata,
    Column("entry_id", ForeignKey("entries.id", ondelete="CASCADE"), primary_key=True),
    Column("habit_id", ForeignKey("habits.id", ondelete="CASCADE"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relazioni
    entries: Mapped[List["Entry"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    habits: Mapped[List["Habit"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    entry_date: Mapped[date] = mapped_column(Date, index=True) # Ottimo per filtrare il calendario
    title: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    mood_score: Mapped[Optional[int]] = mapped_column() # Da 1 a 5, opzionale
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relazioni
    user: Mapped["User"] = relationship(back_populates="entries")
    tags: Mapped[List["Tag"]] = relationship(secondary=entry_tags, back_populates="entries")
    habits: Mapped[List["Habit"]] = relationship(secondary=entry_habits, back_populates="entries")

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(50))
    color: Mapped[Optional[str]] = mapped_column(String(7)) # Es: #FF0000 per rosso

    # Relazioni
    user: Mapped["User"] = relationship(back_populates="tags")
    entries: Mapped[List["Entry"]] = relationship(secondary=entry_tags, back_populates="tags")

class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(50))
    icon: Mapped[Optional[str]] = mapped_column(String(10)) # Es: "🏃‍♂️"

    user: Mapped["User"] = relationship(back_populates="habits")
    entries: Mapped[List["Entry"]] = relationship(secondary=entry_habits, back_populates="habits")