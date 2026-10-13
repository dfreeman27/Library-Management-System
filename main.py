"""
Module 3 Project: Library Management System
main.py — Command-line interface

Your job: Implement each menu handler function below.
The main menu loop is already provided — just fill in the handlers.
"""

from models import init_db
from datetime import date
from crud import (
    add_book, add_author, add_member, checkout_book, return_book,
    list_books, search_books_by_title, find_books_by_author,
    list_member_borrowings, list_overdue_books,
)


def handle_add_book():
    """Prompt for book details and add to the database."""
    
    title = input("Title: ").strip()
    isbn = input("ISBN: ").strip()

    if not title or not isbn:
        print("Title and ISBN are required.")
        return

    year_input = input("Year published: ").strip()
    copies_input = input("Available copies: ").strip()
    
    try:
        year_published = int(year_input) if year_input else None
        available_copies = int(copies_input) if copies_input else 1
    except ValueError:
        print("Year and copies must be whole numbers.")
        return

    if available_copies < 0:
        print("Copies cannot be negative.")
        return

    
    book = add_book(title, isbn, year_published, available_copies)
    print(f"Added: {book.title} (ID: {book.id})")
   
    
    


def handle_add_member():
    """Prompt for member details and register in the database."""

    name = input("Name:").strip()
    email = input("Email:").strip()

    if not name or not email:
        print("Name and email are required.")
        return

    if "@" not in email:
        print("Please enter a valid email address.")
        return

    
    member = add_member(name, email)
    print(f"Registered: {member.name} (ID: {member.id})")
   

    


def handle_search_books():
    """Prompt for a search term and display matching books."""
    keyword = input("Search by title: ").strip()

    if not keyword:
        print("Please enter a search term.")
        return

    books = search_books_by_title(keyword)

    if not books:
        print(f"No books found matching '{keyword}'.")
        return

    print(f"\nFound {len(books)} book(s):")
    for book in books:
        print(f"  [{book.id}] {book.title} | ISBN: {book.isbn} | "
              f"Copies available: {book.available_copies}")

    


def handle_checkout():
    """Prompt for book ID and member ID, then check out the book."""
    books = list_books()

    if not books:
        print("There are no books in the library.")
        return

    print("\nBooks:")
    for book in books:
        print(f"  [{book.id}] {book.title} | Copies available: {book.available_copies}")

    try:
        book_id = int(input("\nEnter book ID: ").strip())
        member_id = int(input("Enter member ID: ").strip())
    except ValueError:
        print("IDs must be whole numbers.")
        return

    try:
        borrowing = checkout_book(book_id, member_id)
        print(f"Checked out successfully. Borrowing ID: {borrowing.id}")
    except ValueError as e:
        print(f"Could not check out book: {e}")


def handle_return():
    """Prompt for a borrowing ID and return the book."""
    try:
        borrowing_id = int(input("Enter borrowing ID: ").strip())
    except ValueError:
        print("Borrowing ID must be a whole number.")
        return

    try:
        return_book(borrowing_id)
        print(f"Borrowing {borrowing_id} returned successfully.")
    except ValueError as e:
        print(f"Could not return book: {e}")



def handle_member_borrowings():
    """Display all active borrowings for a member."""
    try:
        member_id = int(input("Enter member ID: ").strip())
    except ValueError:
        print("Member ID must be a whole number.")
        return

    borrowings = list_member_borrowings(member_id)

    if not borrowings:
        print(f"Member {member_id} has no active borrowings.")
        return

    print(f"\nActive borrowings for member {member_id}:")
    for b in borrowings:
        print(f"  Borrowing [{b.id}] | Book ID: {b.book_id} | "
              f"Checked out: {b.checkout_date}")


def handle_overdue():
    """Display all overdue borrowings."""
    overdue = list_overdue_books()

    if not overdue:
        print("No overdue books.")
        return

    print(f"\n{len(overdue)} overdue borrowing(s):")
    for b in overdue:
        days_out = (date.today() - b.checkout_date).days
        print(f"  Borrowing [{b.id}] | Book ID: {b.book_id} | "
              f"Member ID: {b.member_id} | Checked out: {b.checkout_date} "
              f"({days_out} days ago)")


def main():
    init_db()

    while True:
        print("\n📚 Library Management System")
        print("1. Add a book")
        print("2. Add a member")
        print("3. Search books")
        print("4. Check out a book")
        print("5. Return a book")
        print("6. View member's borrowings")
        print("7. View overdue books")
        print("8. Exit")

        choice = input("\nChoose an option (1-8): ").strip()

        if choice == "1":
            handle_add_book()
        elif choice == "2":
            handle_add_member()
        elif choice == "3":
            handle_search_books()
        elif choice == "4":
            handle_checkout()
        elif choice == "5":
            handle_return()
        elif choice == "6":
            handle_member_borrowings()
        elif choice == "7":
            handle_overdue()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-8.")


if __name__ == "__main__":
    main()
