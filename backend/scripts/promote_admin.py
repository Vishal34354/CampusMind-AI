import argparse
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.repositories.user import UserRepository


def main():
    parser = argparse.ArgumentParser(
        description="Safely promote a registered CampusMind AI user account to Administrator."
    )
    parser.add_argument(
        "email",
        help="Email address of the user account to promote",
    )
    args = parser.parse_args()

    email = args.email.strip().lower()

    db = SessionLocal()
    try:
        repo = UserRepository(db)
        user = repo.get_by_email(email)

        if not user:
            print(f"[-] Error: User with email '{email}' was not found in the database.")
            sys.exit(1)

        if user.is_admin and user.role == "admin":
            print(f"[!] User '{user.full_name}' ({email}) is already an administrator.")
            sys.exit(0)

        updated_user = repo.promote_to_admin(user)
        print(
            f"[+] Successfully promoted '{updated_user.full_name}' ({updated_user.email}) "
            "to Administrator (role='admin', is_admin=True)."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
