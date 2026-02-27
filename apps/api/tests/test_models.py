from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models import Customer, Invoice, Site, Tenant


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    LocalSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with LocalSession() as session:
        yield session


def test_create_tenant_customer_site_invoice_relationships(db_session: Session) -> None:
    tenant = Tenant(name="Tenant Test")
    db_session.add(tenant)
    db_session.flush()

    customer = Customer(
        tenant_id=tenant.id,
        name="Cliente Teste",
        document="11122233344",
        segment="industrial",
        state="SP",
        city="São Paulo",
    )
    db_session.add(customer)
    db_session.flush()

    site = Site(
        tenant_id=tenant.id,
        customer_id=customer.id,
        nickname="Unidade 1",
        address="Rua X, 123",
        distributor="ENEL-SP",
        uc_code="UC-0001",
        tariff_group="A4",
        tariff_modality="verde",
        market_type="FREE",
        contracted_demand_kw=Decimal("100.00"),
    )
    db_session.add(site)
    db_session.flush()

    invoice = Invoice(
        tenant_id=tenant.id,
        site_id=site.id,
        reference_month=date(2024, 1, 1),
        total_amount=Decimal("1000.00"),
        status="UPLOADED",
        distributor=site.distributor,
        market_type=site.market_type,
        tariff_group=site.tariff_group,
    )
    db_session.add(invoice)
    db_session.commit()

    stored_invoice = db_session.query(Invoice).first()
    assert stored_invoice is not None
    assert stored_invoice.site_id == site.id
    assert stored_invoice.tenant_id == tenant.id


def test_unique_constraint_sites_tenant_distributor_uc(db_session: Session) -> None:
    tenant = Tenant(name="Tenant Constraint")
    db_session.add(tenant)
    db_session.flush()

    customer = Customer(
        tenant_id=tenant.id,
        name="Cliente Constraint",
        document="99988877766",
        segment="comercio",
        state="RJ",
        city="Rio de Janeiro",
    )
    db_session.add(customer)
    db_session.flush()

    first_site = Site(
        tenant_id=tenant.id,
        customer_id=customer.id,
        nickname="Unidade A",
        address="Av. Y, 456",
        distributor="COELBA",
        uc_code="UC-9999",
        tariff_group="A4",
        tariff_modality="azul",
        market_type="CAPTIVE",
    )
    db_session.add(first_site)
    db_session.commit()

    duplicate_site = Site(
        tenant_id=tenant.id,
        customer_id=customer.id,
        nickname="Unidade B",
        address="Av. Z, 789",
        distributor="COELBA",
        uc_code="UC-9999",
        tariff_group="A4",
        tariff_modality="azul",
        market_type="CAPTIVE",
    )
    db_session.add(duplicate_site)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_users_email_can_repeat_in_different_tenants(db_session: Session) -> None:
    from app.models import User

    tenant_a = Tenant(name="Tenant A")
    tenant_b = Tenant(name="Tenant B")
    db_session.add_all([tenant_a, tenant_b])
    db_session.flush()

    user_a = User(
        tenant_id=tenant_a.id,
        email="same@example.com",
        full_name="User A",
        hashed_password="hash",
        role="admin",
    )
    user_b = User(
        tenant_id=tenant_b.id,
        email="same@example.com",
        full_name="User B",
        hashed_password="hash",
        role="admin",
    )

    db_session.add_all([user_a, user_b])
    db_session.commit()

    users = db_session.query(User).filter(User.email == "same@example.com").all()
    assert len(users) == 2
