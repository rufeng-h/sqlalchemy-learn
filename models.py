import datetime
from typing import Optional, List

from sqlalchemy import String, ForeignKey, Text, BIGINT
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    addresses: Mapped[List["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[int] = mapped_column(nullable=False, default=0)
    create_time: Mapped[datetime.datetime] = mapped_column(nullable=True, index=True)
    update_time: Mapped[datetime.datetime] = mapped_column(nullable=True)
    disallow_comment: Mapped[bool] = mapped_column(nullable=True, default=False)
    edit_time: Mapped[datetime.datetime] = mapped_column(nullable=True)
    editor_type: Mapped[int] = mapped_column(default=0)
    format_content: Mapped[str] = mapped_column(Text)
    likes: Mapped[int] = mapped_column(BIGINT, default=0)
    meta_description: Mapped[str] = mapped_column(String(1023))
    meta_keywords: Mapped[str] = mapped_column(String(511))
    original_content: Mapped[int] = mapped_column(Text)
    password: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    status: Mapped[int] = mapped_column(default=1, index=True)
    summary: Mapped[str] = mapped_column(Text)
    template: Mapped[str] = mapped_column(String(255))
    thumbnail: Mapped[str] = mapped_column(String(1023))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    top_priority: Mapped[int] = mapped_column(default=0)
    url: Mapped[str] = mapped_column(String(255))
    visits: Mapped[int] = mapped_column(default=0)
    word_count: Mapped[int] = mapped_column(default=0)
    version: Mapped[int] = mapped_column(default=1)

    def __str__(self):
        return f"{self.id}: {self.title} {self.create_time}"

    __repr__ = __str__


class Option(Base):
    __tablename__ = "options"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    create_time: Mapped[Optional[datetime.datetime]]
    update_time: Mapped[Optional[datetime.datetime]]
    type: Mapped[int] = mapped_column(default=0)
    option_key: Mapped[str] = mapped_column(String(100), nullable=False)
    option_value: Mapped[str] = mapped_column(Text, nullable=False)
