from sqlalchemy import select

from app.database.postgres import SessionLocal
from app.models.user import User
from app.models.organization import Organization
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.core.security import hash_password


EMPLOYEES = [
    {
        "name": "Aarav Mehta",
        "role": "employee",
        "projects": ["PayFlow", "SecureGate"],
    },
    {
        "name": "Ishita Kulkarni",
        "role": "employee",
        "projects": ["PayFlow", "HelpDesk Pro"],
    },
    {
        "name": "Rahul Patil",
        "role": "employee",
        "projects": ["PayFlow", "ShopSphere"],
    },
    {
        "name": "Sneha Joshi",
        "role": "employee",
        "projects": ["PayFlow", "ShopSphere", "HelpDesk Pro"],
    },
    {
        "name": "Vikram Deshmukh",
        "role": "employee",
        "projects": ["PayFlow", "SecureGate", "InsightHub"],
    },
    {
        "name": "Ananya Shah",
        "role": "employee",
        "projects": ["InsightHub", "ShopSphere"],
    },
    {
        "name": "Kunal Verma",
        "role": "employee",
        "projects": ["PayFlow", "ShopSphere", "InsightHub"],
    },
    {
        "name": "Neha Kapoor",
        "role": "employee",
        "projects": ["HRConnect"],
    },
    {
        "name": "Aditya Nair",
        "role": "employee",
        "projects": ["PayFlow", "HRConnect"],
    },
    {
        "name": "Pooja More",
        "role": "employee",
        "projects": ["HelpDesk Pro", "ShopSphere"],
    },
    {
        "name": "Manav Rao",
        "role": "employee",
        "projects": ["HRConnect", "SecureGate"],
    },
    {
        "name": "Tanvi Joshi",
        "role": "employee",
        "projects": ["InsightHub", "HelpDesk Pro"],
    },
]

PASSWORD = "Demo@2026!"


def make_email(name: str) -> str:
    return name.lower().replace(" ", ".") + "@technova.com"


db = SessionLocal()

try:
    org = db.scalar(
        select(Organization)
        .where(Organization.name == "TechNova Solutions Pvt. Ltd.")
    )

    if not org:
        raise RuntimeError(
            "TechNova Solutions Pvt. Ltd. organization was not found."
        )

    print(f"Organization: {org.name} (id={org.id})")
    print()

    for employee in EMPLOYEES:
        name = employee["name"]
        email = make_email(name)

        user = db.scalar(
            select(User).where(User.email == email)
        )

        if not user:
            user = User(
                organization_id=org.id,
                name=name,
                email=email,
                password_hash=hash_password(PASSWORD),
                role="employee",
                approval_status="APPROVED",
                is_active=True,
            )

            db.add(user)
            db.flush()

            print(f"CREATED USER: {name} -> {email}")
        else:
            print(f"EXISTS USER:  {name} -> {email}")

        for project_name in employee["projects"]:
            project = db.scalar(
                select(Project).where(
                    Project.organization_id == org.id,
                    Project.name == project_name,
                )
            )

            if not project:
                print(
                    f"  WARNING: Project '{project_name}' not found. "
                    f"Skipping membership."
                )
                continue

            membership = db.scalar(
                select(ProjectMember).where(
                    ProjectMember.project_id == project.id,
                    ProjectMember.user_id == user.id,
                )
            )

            if not membership:
                membership = ProjectMember(
                    project_id=project.id,
                    user_id=user.id,
                    permission="PROJECT_MEMBER",
                )

                db.add(membership)

                print(f"  + {project_name}")
            else:
                print(f"  = {project_name} already assigned")

        print()

    db.commit()

    print("=" * 60)
    print("EMPLOYEE SETUP COMPLETE")
    print("=" * 60)
    print(f"Employees processed: {len(EMPLOYEES)}")
    print(f"Password: {PASSWORD}")

except Exception:
    db.rollback()
    raise

finally:
    db.close()