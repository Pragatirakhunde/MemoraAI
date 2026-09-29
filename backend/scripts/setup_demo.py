from app.core.security import hash_password
from app.database.postgres import SessionLocal
from app.models.department import Department
from app.models.organization import Organization
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User


def get_or_create(db, model, defaults=None, **filters):
    row = db.query(model).filter_by(**filters).first()
    if row:
        return row, False
    payload = dict(filters)
    payload.update(defaults or {})
    row = model(**payload)
    db.add(row)
    db.flush()
    return row, True


def main():
    db = SessionLocal()
    try:
        org, _ = get_or_create(
            db,
            Organization,
            id=1,
            defaults={"name": "TechNova", "slug": "technova", "description": "Demo enterprise organization for Memora AI."},
        )
        db.flush()

        department, _ = get_or_create(
            db,
            Department,
            organization_id=org.id,
            name="Engineering",
            defaults={"description": "Software engineering and platform team."},
        )

        admin, _ = get_or_create(
            db,
            User,
            email="admin@technova.com",
            defaults={
                "organization_id": org.id,
                "name": "System Admin",
                "password_hash": hash_password("Admin@123"),
                "role": "admin",
                "approval_status": "APPROVED",
                "is_active": True,
            },
        )
        admin.organization_id = org.id
        admin.role = "admin"
        admin.approval_status = "APPROVED"
        admin.is_active = True

        employee, _ = get_or_create(
            db,
            User,
            email="employee@technova.com",
            defaults={
                "organization_id": org.id,
                "name": "Test Employee",
                "password_hash": hash_password("Employee@123"),
                "role": "employee",
                "approval_status": "APPROVED",
                "is_active": True,
                "department_id": department.id,
            },
        )
        employee.organization_id = org.id
        employee.department_id = department.id
        employee.approval_status = "APPROVED"
        employee.is_active = True

        projects = [
            ("PayFlow", "payflow", "Payment and billing platform."),
            ("ShopSphere", "shopsphere", "E-commerce platform."),
            ("HelpDesk Pro", "helpdesk-pro", "IT service and ticketing platform."),
            ("InsightHub", "insighthub", "Analytics and business intelligence platform."),
            ("HRConnect", "hrconnect", "HR and employee management platform."),
        ]
        created_projects = []
        for name, slug, description in projects:
            project, _ = get_or_create(
                db,
                Project,
                organization_id=org.id,
                slug=slug,
                defaults={"name": name, "description": description, "status": "active"},
            )
            project.name = name
            project.description = description
            project.status = "active"
            created_projects.append(project)

        payflow = next(p for p in created_projects if p.slug == "payflow")
        member = db.query(ProjectMember).filter_by(project_id=payflow.id, user_id=employee.id).first()
        if member is None:
            db.add(ProjectMember(project_id=payflow.id, user_id=employee.id, permission="PROJECT_MEMBER"))

        db.commit()
        print("Demo setup complete.")
        print(f"Organization: {org.id} | {org.name}")
        print(f"Admin: {admin.email} / Admin@123")
        print(f"Employee: {employee.email} / Employee@123")
        print(f"Employee department: {department.name}")
        print(f"Employee assigned project: {payflow.name}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
