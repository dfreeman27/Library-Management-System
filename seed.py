"""
Module 3 Project: Library Management System
seed.py — Populate the database with sample data for testing.

Run after implementing your models and CRUD functions:
    python seed.py

Sample data is loaded from sample_data.json.
"""

from sqlalchemy import select
import json
from models import init_db, engine, Session, Author, Borrowing, Book, Member
from crud import add_author, add_book, add_member
from datetime import date 


def seed():
    """Load sample data from sample_data.json and insert it into the database."""
    init_db()

    with open("sample_data.json") as f:
        data = json.load(f)
    # 1. Add authors, skipping records already loaded by an earlier run.
    for author_data in data["authors"]:
        with Session(engine) as session:
            author_exists = session.scalar(
                select(Author.id).where(Author.name == author_data["name"])
            )
        if author_exists is None:
            add_author(author_data["name"], author_data.get("bio"))

    # 2. Add books only when their ISBN is not already in the database,
    # then ensure each book-author association exists.
    for book_data in data["books"]:
        with Session(engine) as session:
            book_exists = session.scalar(
                select(Book.id).where(Book.isbn == book_data["isbn"])
            )
        if book_exists is None:
            add_book(
                book_data["title"],
                book_data["isbn"],
                book_data.get("year_published"),
                book_data.get("available_copies", 1),
            )

        with Session(engine) as session:
            book = session.scalar(
                select(Book).where(Book.isbn == book_data["isbn"])
            )

            if book is None:
                raise ValueError(
                    f"Book not found: {book_data['isbn']}"
                )

            for author_name in book_data["authors"]:
                author = session.scalar(
                    select(Author).where(Author.name == author_name)
                )

                if author is None:
                    raise ValueError(
                        f"Author not found: {author_name}"
                    )

                if author not in book.authors:
                    book.authors.append(author)

            session.commit()

    # 3. Add members, skipping email addresses already registered.
    for member_data in data["members"]:
        with Session(engine) as session:
            member_exists = session.scalar(
                select(Member.id).where(Member.email == member_data["email"])
            )
        if member_exists is None:
            add_member(member_data["name"], member_data["email"])

    # 4. Add each borrowing once, preserving dates and only decrementing
    # availability for a newly added, active borrowing.
    for borrowing_data in data["borrowings"]:
        checkout_date = date.fromisoformat(borrowing_data["checkout_date"])
        return_date = (
            date.fromisoformat(borrowing_data["return_date"])
            if borrowing_data.get("return_date")
            else None
        )

        with Session(engine) as session:
            book = session.scalar(
                select(Book).where(
                    Book.isbn == borrowing_data["book_isbn"]
                )
            )
            member = session.scalar(
                select(Member).where(
                    Member.email == borrowing_data["member_email"]
                )
            )

            if book is None:
                raise ValueError(
                    f"Book not found: {borrowing_data['book_isbn']}"
                )

            if member is None:
                raise ValueError(
                    f"Member not found: {borrowing_data['member_email']}"
                )

            borrowing_exists = session.scalar(
                select(Borrowing.id).where(
                    Borrowing.book_id == book.id,
                    Borrowing.member_id == member.id,
                    Borrowing.checkout_date == checkout_date,
                )
            )
            if borrowing_exists is None:
                if return_date is None:
                    if book.available_copies <= 0:
                        raise ValueError(
                            f"No copies available for book: {book.isbn}"
                        )
                    book.available_copies -= 1

                session.add(
                    Borrowing(
                        book_id=book.id,
                        member_id=member.id,
                        checkout_date=checkout_date,
                        return_date=return_date,
                    )
                )
                session.commit()
            else:
                borrowing = session.get(Borrowing, borrowing_exists)
                if (
                    borrowing is not None
                    and return_date is not None
                    and borrowing.return_date is None
                ):
                    # Repair returned sample loans created by older versions
                    # of this seeder, which left return_date unset.
                    borrowing.return_date = return_date
                    book.available_copies += 1
                    session.commit()

    print("Seed complete!")


if __name__ == "__main__":
    seed()
