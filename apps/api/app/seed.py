from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import (
    AuditFinding,
    Customer,
    IcmsStatement,
    Invoice,
    InvoiceExtraction,
    InvoiceFile,
    InvoiceLineItem,
    InvoiceTax,
    Rule,
    Ruleset,
    Site,
    Tenant,
    User,
)
from app.security import get_password_hash


def run_seed(db: Session) -> None:
    tenant = db.query(Tenant).filter(Tenant.name == "Tenant Demo").first()
    if not tenant:
        tenant = Tenant(name="Tenant Demo")
        db.add(tenant)
        db.flush()

    admin = db.query(User).filter(User.email == "admin@demo.com").first()
    if not admin:
        admin = User(
            email="admin@demo.com",
            full_name="Admin Demo",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            tenant_id=tenant.id,
        )
        db.add(admin)

    customer_user = db.query(User).filter(User.email == "cliente@demo.com").first()
    if not customer_user:
        db.add(
            User(
                email="cliente@demo.com",
                full_name="Cliente Demo",
                hashed_password=get_password_hash("cliente123"),
                role="cliente",
                tenant_id=tenant.id,
            )
        )

    customer = db.query(Customer).filter(Customer.tenant_id == tenant.id, Customer.document == "12345678000199").first()
    if not customer:
        customer = Customer(
            tenant_id=tenant.id,
            name="Hotel Demo Ltda",
            document="12345678000199",
            email="financeiro@hoteldemo.com",
            phone="+55 71 99999-0000",
            segment="hotel",
            state="BA",
            city="Salvador",
            notes="Cliente criado por seed",
        )
        db.add(customer)
        db.flush()

    site = db.query(Site).filter(Site.tenant_id == tenant.id, Site.distributor == "COELBA", Site.uc_code == "1234567890").first()
    if not site:
        site = Site(
            tenant_id=tenant.id,
            customer_id=customer.id,
            nickname="Matriz",
            address="Av. Principal, 1000 - Salvador/BA",
            distributor="COELBA",
            uc_code="1234567890",
            tariff_group="A4",
            tariff_modality="verde",
            market_type="CAPTIVE",
            contracted_demand_kw=Decimal("350.00"),
            meter_voltage_kv=Decimal("13.80"),
        )
        db.add(site)
        db.flush()

    invoice = db.query(Invoice).filter(Invoice.tenant_id == tenant.id, Invoice.site_id == site.id, Invoice.reference_month == date(2024, 5, 1)).first()
    if not invoice:
        invoice = Invoice(
            tenant_id=tenant.id,
            site_id=site.id,
            reference_month=date(2024, 5, 1),
            issue_date=date(2024, 5, 10),
            due_date=date(2024, 5, 20),
            reading_start=date(2024, 4, 1),
            reading_end=date(2024, 4, 30),
            days=30,
            total_amount=Decimal("15234.78"),
            status="PROCESSED",
            distributor="COELBA",
            market_type="CAPTIVE",
            tariff_group="A4",
            raw_hash="f" * 64,
        )
        db.add(invoice)
        db.flush()

    if not db.query(InvoiceLineItem).filter(InvoiceLineItem.invoice_id == invoice.id).first():
        db.add_all(
            [
                InvoiceLineItem(
                    tenant_id=tenant.id,
                    invoice_id=invoice.id,
                    category="TE",
                    name_raw="Tarifa de Energia",
                    quantity=Decimal("12000"),
                    unit="kWh",
                    unit_price=Decimal("0.6532"),
                    amount=Decimal("7838.40"),
                    period="FORA_PONTA",
                ),
                InvoiceLineItem(
                    tenant_id=tenant.id,
                    invoice_id=invoice.id,
                    category="TUSD",
                    name_raw="Uso do Sistema de Distribuição",
                    quantity=Decimal("12000"),
                    unit="kWh",
                    unit_price=Decimal("0.4110"),
                    amount=Decimal("4932.00"),
                    period="FORA_PONTA",
                ),
            ]
        )

    if not db.query(InvoiceTax).filter(InvoiceTax.invoice_id == invoice.id).first():
        db.add(
            InvoiceTax(
                tenant_id=tenant.id,
                invoice_id=invoice.id,
                tax_type="ICMS",
                base_amount=Decimal("12770.40"),
                rate=Decimal("0.1800"),
                amount=Decimal("2298.67"),
                notes="ICMS padrão",
            )
        )

    if not db.query(InvoiceFile).filter(InvoiceFile.invoice_id == invoice.id).first():
        db.add(
            InvoiceFile(
                tenant_id=tenant.id,
                invoice_id=invoice.id,
                storage_provider="minio",
                bucket="invoices",
                object_key=f"{tenant.id}/{invoice.id}.pdf",
                original_filename="fatura-maio-2024.pdf",
                content_type="application/pdf",
                size_bytes=412345,
            )
        )

    if not db.query(InvoiceExtraction).filter(InvoiceExtraction.invoice_id == invoice.id).first():
        db.add(
            InvoiceExtraction(
                tenant_id=tenant.id,
                invoice_id=invoice.id,
                extractor_version="v1.0.0",
                method="PDF_TEXT",
                confidence_score=Decimal("97.50"),
                extracted_json={"distributor": "COELBA", "reference_month": "2024-05"},
                evidence_json={"page": 1, "bbox": [100, 100, 200, 120]},
            )
        )

    if not db.query(AuditFinding).filter(AuditFinding.invoice_id == invoice.id).first():
        db.add(
            AuditFinding(
                tenant_id=tenant.id,
                invoice_id=invoice.id,
                rule_code="ICMS-001",
                ruleset_version="1.0.0",
                level="WARN",
                title="Alíquota acima da média",
                message="A alíquota de ICMS ficou acima da média histórica dos últimos 12 meses.",
                evidence={"rate": 0.18, "historical_avg": 0.16},
            )
        )

    ruleset = db.query(Ruleset).filter(Ruleset.tenant_id == tenant.id, Ruleset.name == "Regras Fiscais").first()
    if not ruleset:
        ruleset = Ruleset(
            tenant_id=tenant.id,
            name="Regras Fiscais",
            version="1.0.0",
            description="Regras padrão de validação tributária",
            is_active=True,
        )
        db.add(ruleset)
        db.flush()

    if not db.query(Rule).filter(Rule.ruleset_id == ruleset.id, Rule.code == "ICMS-001").first():
        db.add(
            Rule(
                tenant_id=tenant.id,
                ruleset_id=ruleset.id,
                code="ICMS-001",
                title="Valida ICMS acima do teto",
                severity_default="WARN",
                condition_json={"op": ">", "left": {"var": "icms_rate"}, "right": 0.17},
                actions_json={"message": "ICMS acima do teto esperado"},
            )
        )

    if not db.query(IcmsStatement).filter(IcmsStatement.tenant_id == tenant.id, IcmsStatement.site_id == site.id).first():
        db.add(
            IcmsStatement(
                tenant_id=tenant.id,
                site_id=site.id,
                start_month=date(2024, 1, 1),
                end_month=date(2024, 5, 1),
                storage_bucket="icms",
                storage_key=f"{tenant.id}/{site.id}/icms-2024-01_2024-05.xlsx",
                format="XLSX",
                summary_json={"total_base": 60000, "total_icms": 10800},
            )
        )

    db.commit()


def main() -> None:
    with SessionLocal() as db:
        run_seed(db)


if __name__ == "__main__":
    main()
