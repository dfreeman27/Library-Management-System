"""
Module 3 Project: Library Management System
crud.py — Create, Read, Update, Delete operations

Your job: Implement every function below.
Import your models and engine from models.py.
"""

from models import engine, Book, Author, Member, Borrowing
from sqlalchemy.orm import Session
from datetime import date, timedelta


# ──────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────

def add_book(title: str, isbn: str, year_published: int = None,
             available_copies: int = 1):
    """Add a new book to the database. Returns the created Book object."""
    new_book = Book(
        title=title,
        isbn=isbn,
        year_published=year_published,
        available_copies=available_copies
    )
    with Session(engine, expire_on_commit=False) as session:
        session.add(new_book)
        session.commit()
        return new_book

    

def add_author(name: str, bio: str = None):
    """Add a new author. Returns the created Author object."""
    new_author = Author(
        name=name,
        bio=bio 
    )
    with Session(engine, expire_on_commit=False) as session:
        session.add(new_author)
        session.commit()
        return new_author
    

def add_member(name: str, email: str):
    """
    Register a new member with today's date as membership_date.
    Returns the created Member object.
    """
    new_member = Member(
        name=name,
        email=email,
        membership_date=date.today()
    )
    with Session(engine, expire_on_commit=False) as session:
        session.add(new_member)
        session.commit()
        return new_member


def checkout_book(book_id: int, member_id: int):
    """
    Check out a book to a member.
    Decrements available_copies by 1 and sets checkout_date to today.
    Raises ValueError if available_copies == 0.
    Returns the created Borrowing object.
    """
   
    with Session(engine, expire_on_commit=False) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise ValueError("Book not found.")

        member = session.get(Member, member_id)
        if member is None:
            raise ValueError("Member not found.")

        if book.available_copies == 0:
            raise ValueError("No copies of this book are available.")

        borrowing = Borrowing(
            book_id=book_id,
            member_id=member_id,
            checkout_date=date.today(),
            return_date=None
        )
        book.available_copies -= 1

        session.add(borrowing)
        session.commit()
        return borrowing


# ──────────────────────────────────────────
# READ
# ──────────────────────────────────────────

def list_books():
    """Return a list of all Book objects."""
    with Session(engine, expire_on_commit=False) as session:
        return session.query(Book).order_by(Book.title).all()

def search_books_by_title(title: str):
    """Return books whose title contains the given string (case-insensitive)."""
    with Session(engine) as session:
        return session.query(Book).filter(Book.title.ilike(f"%{title}%")).order_by(Book.title).all()


def find_books_by_author(author_name: str):
    """Return all books associated with an author whose name contains author_name."""
    with Session(engine, expire_on_commit=False) as session:
         return (
            session.query(Book)
            .join(Book.authors)
            .filter(Author.name.ilike(f"%{author_name}%"))
            .order_by(Book.title)
            .all()
        )


def list_member_borrowings(member_id: int):
    """Return all active (unreturned) Borrowing objects for the given member."""
    with Session(engine, expire_on_commit=False) as session:
        return (
        session.query(Borrowing)
        .filter(
        Borrowing.member_id == member_id,
        Borrowing.return_date.is_(None)
        )
        .order_by(Borrowing.checkout_date.desc())
        .all()
        )


def list_overdue_books(days: int = 14):
    """
    Return Borrowing objects where return_date is NULL and
    checkout_date is more than `days` days ago.
    """
    cutoff_date = date.today() - timedelta(days=days)
    with Session(engine, expire_on_commit=False) as session:
        return(session.query(Borrowing).filter(Borrowing.return_date.is_(None),Borrowing.checkout_date < cutoff_date).all()
               )



# ──────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────

def return_book(borrowing_id: int):
    """
    Mark a borrowing as returned.
    Sets return_date to today and increments book.available_copies by 1.
    Raises ValueError if the borrowing is not found or already returned.
    """
    with Session(engine, expire_on_commit=False) as session:
        borrowing = session.get(Borrowing, borrowing_id)
        if borrowing is None:
            raise ValueError("Borrowing not found.")

        if borrowing.return_date is not None:
            raise ValueError("This book has already been returned.")

        book = session.get(Book, borrowing.book_id)
        if book is None:
            raise ValueError("Book not found.")

        borrowing.return_date = date.today()
        book.available_copies += 1

        session.commit()
        return borrowing


def update_member_email(member_id: int, new_email: str):
    """Update the email address for a member. Returns the updated Member object."""
    with Session(engine, expire_on_commit=False) as session:
        member = session.get(Member, member_id)
        if member is None:
            raise ValueError("Member not found.")

        member.email = new_email
        session.commit()
        return member

# ──────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────

def delete_book(book_id: int):
    """
    Delete a book from the database.
    Raises ValueError if the book has any active (unreturned) borrowings.
    """
    with Session(engine, expire_on_commit=False) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise ValueError("Book not found.")

        loans = session.query(Borrowing).filter(Borrowing.book_id == book.id)

        if loans.filter(Borrowing.return_date.is_(None)).first() is not None:
            raise ValueError("Cannot delete a book with active borrowings.")

        if loans.first() is not None:
            raise ValueError(
                "Cannot delete a book that has loan history."
            )

        session.delete(book)
        session.commit()

def delete_member(member_id: int):
    """
    Delete a member from the database.
    Raises ValueError if the member has any active (unreturned) borrowings.
    """
    with Session(engine, expire_on_commit=False) as session:
        member = session.get(Member, member_id)
        if member is None:
            raise ValueError("Member not found.")

        loans = session.query(Borrowing).filter(Borrowing.member_id == member.id)

        if loans.filter(Borrowing.return_date.is_(None)).first() is not None:
            raise ValueError("Cannot delete a member with active borrowings.")

        if loans.first() is not None:
            raise ValueError("Cannot delete a member that has loan history.")

        session.delete(member)
        session.commit()
