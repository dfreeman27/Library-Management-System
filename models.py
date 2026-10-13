"""
Module 3 Project: Library Management System
models.py — SQLAlchemy models and database setup

Your job: Implement the models marked with # TODO.
All models must use SQLAlchemy 2.0 syntax: Mapped and mapped_column.
"""

from sqlalchemy import create_engine, String, Integer, ForeignKey, Table, Column, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from typing import Optional 
from datetime import date

engine = create_engine("sqlite:///library.db", echo=False)


class Base(DeclarativeBase):
    pass



book_authors = Table(
     "book_authors",
     Base.metadata,
     Column("book_id",   Integer, ForeignKey("books.id"),   primary_key=True),
     Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
)


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150),nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(String(300),nullable=True)

    books: Mapped[list["Book"]] = relationship(secondary=book_authors, back_populates="authors")


class Member(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150),nullable=False)
    email: Mapped[str] = mapped_column(String(200),unique=True,nullable=False)
    membership_date: Mapped[date] = mapped_column(Date)
    
    borrowings: Mapped[list["Borrowing"]] = relationship(back_populates="member")
    

class Book(Base):
    __tablename__ = "books"
    id:Mapped[int] = mapped_column(primary_key=True)
    title:Mapped[str] = mapped_column(String(250),nullable=False)
    isbn: Mapped[str] = mapped_column(String(50),unique=True,nullable=False)
    year_published: Mapped[Optional[int]] = mapped_column(Integer)
    available_copies: Mapped[int] = mapped_column(Integer,default=1,nullable=False)

    authors: Mapped[list["Author"]] = relationship(
            secondary=book_authors,
            back_populates="books",
        )
    
    borrowings: Mapped[list["Borrowing"]] = relationship(
            back_populates="book",
        )


class Borrowing(Base):
    __tablename__ = "borrowings"
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(
           ForeignKey("books.id"), nullable=False
       )
    member_id: Mapped[int] = mapped_column(
           ForeignKey("members.id"), nullable=False
       )
    checkout_date: Mapped[date] = mapped_column(
            Date, default=date.today, nullable=False
        )
    return_date: Mapped[Optional[date]] = mapped_column(
            Date, nullable=True
        )
    
    book: Mapped["Book"] = relationship(back_populates="borrowings")
    member: Mapped["Member"] = relationship(back_populates="borrowings")

    def __repr__(self):
        return (
            f"Borrowing(book_id={self.book_id}, "
            f"member_id={self.member_id}, "
            f"checkout_date={self.checkout_date})"
        )


def init_db():
    """Create all tables in the database. Call once before using any other functions."""
   
    Base.metadata.create_all(engine)
    