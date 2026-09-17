from app.core.security import hash_password
from app.database.postgres import SessionLocal
from app.models.user import User


db = SessionLocal()

try:
    existing = db.query(User).filter(
        User.email == "employee@technova.com"
    ).first()

    if existing:
        print("Employee already exists.")
    else:
        employee = User(
            organization_id=1,
            name="Test Employee",
            email="employee@technova.com",
            password_hash=hash_password("Employee@123"),
            role="employee",
            is_active=True,
        )

        db.add(employee)
        db.commit()

        print("Employee created successfully.")

finally:
    db.close()