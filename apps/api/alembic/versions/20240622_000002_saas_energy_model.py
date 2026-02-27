"""add saas energy management model

Revision ID: 20240622_000002
Revises: 20240621_000001
Create Date: 2024-06-22 00:00:02
"""

from alembic import op
import sqlalchemy as sa


revision = "20240622_000002"
down_revision = "20240621_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
    op.drop_index("ix_users_email", table_name="users")
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_unique_constraint("uq_users_tenant_email", "users", ["tenant_id", "email"])

    op.create_table(
        "customers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("document", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("segment", sa.String(length=30), nullable=False),
        sa.Column("state", sa.String(length=2), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "document", name="uq_customers_tenant_document"),
        sa.CheckConstraint(
            "segment IN ('industrial','hospital','hotel','comercio','servico_publico','residencial','outro')",
            name="ck_customers_segment",
        ),
    )
    op.create_index("ix_customers_tenant_id", "customers", ["tenant_id"])
    op.create_index("ix_customers_tenant_name", "customers", ["tenant_id", "name"])

    op.create_table(
        "sites",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("nickname", sa.String(length=120), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("distributor", sa.String(length=100), nullable=False),
        sa.Column("uc_code", sa.String(length=100), nullable=False),
        sa.Column("tariff_group", sa.String(length=20), nullable=False),
        sa.Column("tariff_modality", sa.String(length=50), nullable=False),
        sa.Column("market_type", sa.String(length=20), nullable=False),
        sa.Column("contracted_demand_kw", sa.Numeric(14, 4), nullable=True),
        sa.Column("meter_voltage_kv", sa.Numeric(14, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "distributor", "uc_code", name="uq_sites_tenant_distributor_uc"),
        sa.CheckConstraint("market_type IN ('FREE','CAPTIVE','UNKNOWN')", name="ck_sites_market_type"),
    )
    op.create_index("ix_sites_tenant_id", "sites", ["tenant_id"])
    op.create_index("ix_sites_tenant_customer", "sites", ["tenant_id", "customer_id"])

    op.create_table(
        "invoices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.String(length=36), nullable=False),
        sa.Column("reference_month", sa.Date(), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("reading_start", sa.Date(), nullable=True),
        sa.Column("reading_end", sa.Date(), nullable=True),
        sa.Column("days", sa.Integer(), nullable=True),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("distributor", sa.String(length=100), nullable=False),
        sa.Column("market_type", sa.String(length=20), nullable=False),
        sa.Column("tariff_group", sa.String(length=20), nullable=False),
        sa.Column("raw_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "site_id", "reference_month", name="uq_invoice_site_refmonth"),
        sa.CheckConstraint(
            "status IN ('UPLOADED','PROCESSING','PROCESSED','FAILED')",
            name="ck_invoices_status",
        ),
    )
    op.create_index("ix_invoices_tenant_id", "invoices", ["tenant_id"])
    op.create_index("ix_invoices_tenant_reference", "invoices", ["tenant_id", "reference_month"])
    op.create_index("ix_invoices_raw_hash", "invoices", ["raw_hash"])

    op.create_table(
        "invoice_files",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("storage_provider", sa.String(length=20), nullable=False),
        sa.Column("bucket", sa.String(length=120), nullable=False),
        sa.Column("object_key", sa.String(length=512), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invoice_files_tenant_invoice", "invoice_files", ["tenant_id", "invoice_id"])

    op.create_table(
        "invoice_extractions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("extractor_version", sa.String(length=50), nullable=False),
        sa.Column("method", sa.String(length=20), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("extracted_json", sa.JSON(), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("confidence_score >= 0 AND confidence_score <= 100", name="ck_confidence_range"),
    )
    op.create_index("ix_invoice_extractions_tenant_invoice", "invoice_extractions", ["tenant_id", "invoice_id"])

    op.create_table(
        "invoice_line_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("name_raw", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 4), nullable=True),
        sa.Column("unit", sa.String(length=20), nullable=True),
        sa.Column("unit_price", sa.Numeric(14, 6), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("period", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "category IN ('TE','TUSD','DEMANDA','REATIVOS','ILUMINACAO_PUBLICA','ENCARGOS','OUTROS')",
            name="ck_lineitem_category",
        ),
        sa.CheckConstraint("period IN ('PONTA','FORA_PONTA','NA')", name="ck_lineitem_period"),
    )
    op.create_index("ix_invoice_line_items_tenant_invoice_category", "invoice_line_items", ["tenant_id", "invoice_id", "category"])

    op.create_table(
        "invoice_taxes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("tax_type", sa.String(length=20), nullable=False),
        sa.Column("base_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("rate", sa.Numeric(8, 4), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "invoice_id",
            "tax_type",
            "rate",
            "base_amount",
            name="uq_invoice_taxes_unique_tax",
        ),
        sa.CheckConstraint("tax_type IN ('ICMS','PIS','COFINS','OUTRO')", name="ck_tax_type"),
    )

    op.create_table(
        "audit_findings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("rule_code", sa.String(length=100), nullable=False),
        sa.Column("ruleset_version", sa.String(length=50), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("level IN ('PASS','WARN','FAIL','REVIEW')", name="ck_finding_level"),
    )
    op.create_index("ix_audit_findings_tenant_invoice_level", "audit_findings", ["tenant_id", "invoice_id", "level"])

    op.create_table(
        "icms_statements",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.String(length=36), nullable=False),
        sa.Column("start_month", sa.Date(), nullable=False),
        sa.Column("end_month", sa.Date(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("storage_bucket", sa.String(length=120), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("format", sa.String(length=10), nullable=False),
        sa.Column("summary_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("format IN ('PDF','XLSX','BOTH')", name="ck_icms_format"),
    )
    op.create_index("ix_icms_statements_tenant_site", "icms_statements", ["tenant_id", "site_id"])

    op.create_table(
        "rulesets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "name", "version", name="uq_rulesets_tenant_name_version"),
    )

    op.create_table(
        "rules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("ruleset_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("severity_default", sa.String(length=20), nullable=False),
        sa.Column("condition_json", sa.JSON(), nullable=False),
        sa.Column("actions_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ruleset_id"], ["rulesets.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "ruleset_id", "code", name="uq_rules_tenant_ruleset_code"),
    )


def downgrade() -> None:
    op.drop_table("rules")
    op.drop_table("rulesets")
    op.drop_index("ix_icms_statements_tenant_site", table_name="icms_statements")
    op.drop_table("icms_statements")
    op.drop_index("ix_audit_findings_tenant_invoice_level", table_name="audit_findings")
    op.drop_table("audit_findings")
    op.drop_table("invoice_taxes")
    op.drop_index("ix_invoice_line_items_tenant_invoice_category", table_name="invoice_line_items")
    op.drop_table("invoice_line_items")
    op.drop_index("ix_invoice_extractions_tenant_invoice", table_name="invoice_extractions")
    op.drop_table("invoice_extractions")
    op.drop_index("ix_invoice_files_tenant_invoice", table_name="invoice_files")
    op.drop_table("invoice_files")
    op.drop_index("ix_invoices_raw_hash", table_name="invoices")
    op.drop_index("ix_invoices_tenant_reference", table_name="invoices")
    op.drop_index("ix_invoices_tenant_id", table_name="invoices")
    op.drop_table("invoices")
    op.drop_index("ix_sites_tenant_customer", table_name="sites")
    op.drop_index("ix_sites_tenant_id", table_name="sites")
    op.drop_table("sites")
    op.drop_index("ix_customers_tenant_name", table_name="customers")
    op.drop_index("ix_customers_tenant_id", table_name="customers")
    op.drop_table("customers")
    op.drop_constraint("uq_users_tenant_email", "users", type_="unique")
    op.drop_index("ix_users_email", table_name="users")
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.drop_column("users", "updated_at")
    op.drop_column("tenants", "updated_at")
