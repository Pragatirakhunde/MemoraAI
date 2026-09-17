from app.core.security import hash_password
from app.database.postgres import SessionLocal
from app.models.user import User


def create_admin():

    db = SessionLocal()

    try:
        existing = db.query(User).filter(
            User.email == "admin@technova.com"
        ).first()

        if existing:
            print("Admin already exists.")
            return

        admin = User(
            organization_id=1,
            name="System Admin",
            email="admin@technova.com",
            password_hash=hash_password("Admin@123"),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()