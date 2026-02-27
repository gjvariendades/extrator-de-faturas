from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Tenant, User
from app.security import get_password_hash


def run_seed(db: Session) -> None:
    tenant = db.query(Tenant).filter(Tenant.name == "Tenant Demo").first()
    if not tenant:
        tenant = Tenant(name="Tenant Demo")
        db.add(tenant)
        db.flush()

    user = db.query(User).filter(User.email == "admin@demo.com").first()
    if not user:
        db.add(
            User(
                email="admin@demo.com",
                full_name="Admin Demo",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                tenant_id=tenant.id,
            )
        )

    db.commit()


def main() -> None:
    with SessionLocal() as db:
        run_seed(db)


if __name__ == "__main__":
    main()
