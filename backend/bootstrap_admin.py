"""Create the first QuanLy account explicitly, never during app import.

Run only after the reviewed MySQL schema exists. The password is read from the
terminal without echoing and is never written to a file or log.
"""

from getpass import getpass

from passlib.context import CryptContext

from database import SessionLocal
from models import User


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def main():
    username = input("Username for first QuanLy account: ").strip()
    full_name = input("Full name: ").strip()
    password = getpass("Password: ")
    password_confirm = getpass("Confirm password: ")

    if not username or not full_name or not password:
        raise SystemExit("Username, full name, and password are required.")
    if password != password_confirm:
        raise SystemExit("Passwords do not match.")

    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == username).first():
            raise SystemExit("Username already exists; no account was changed.")
        db.add(
            User(
                username=username,
                password=pwd_context.hash(password),
                full_name=full_name,
                role="QuanLy",
            )
        )
        db.commit()
        print("QuanLy account created.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
