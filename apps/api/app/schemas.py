from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: str
    tenant_id: int


class CustomerCreate(BaseModel):
    name: str
    document: str
    email: EmailStr | None = None
    phone: str | None = None
    segment: str
    state: str
    city: str
    notes: str | None = None


class CustomerOut(CustomerCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: int
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class SiteCreate(BaseModel):
    customer_id: str
    nickname: str
    address: str
    distributor: str
    uc_code: str
    tariff_group: str
    tariff_modality: str
    market_type: str = "UNKNOWN"
    contracted_demand_kw: Decimal | None = None
    meter_voltage_kv: Decimal | None = None


class SiteOut(SiteCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: int
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class InvoiceCreate(BaseModel):
    site_id: str
    reference_month: date
    issue_date: date | None = None
    due_date: date | None = None
    reading_start: date | None = None
    reading_end: date | None = None
    days: int | None = None
    total_amount: Decimal
    status: str = "UPLOADED"
    distributor: str
    market_type: str
    tariff_group: str
    raw_hash: str | None = None


class InvoiceOut(InvoiceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: int
    created_at: datetime
    updated_at: datetime | None = None


class InvoiceLineItemCreate(BaseModel):
    invoice_id: str
    category: str
    name_raw: str
    quantity: Decimal | None = None
    unit: str | None = None
    unit_price: Decimal | None = None
    amount: Decimal
    period: str = "NA"


class InvoiceLineItemOut(InvoiceLineItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: int
    created_at: datetime


class InvoiceTaxCreate(BaseModel):
    invoice_id: str
    tax_type: str
    base_amount: Decimal
    rate: Decimal
    amount: Decimal
    notes: str | None = None


class InvoiceTaxOut(InvoiceTaxCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: int
    created_at: datetime


class InvoiceFileCreate(BaseModel):
    invoice_id: str
    storage_provider: str = "minio"
    bucket: str
    object_key: str
    original_filename: str
    content_type: str | None = None
    size_bytes: int


class InvoiceFileOut(InvoiceFileCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: int
    uploaded_at: datetime


class InvoiceExtractionCreate(BaseModel):
    invoice_id: str
    extractor_version: str
    method: str
    confidence_score: Decimal
    extracted_json: dict
    evidence_json: dict


class InvoiceExtractionOut(InvoiceExtractionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: int
    created_at: datetime


class AuditFindingCreate(BaseModel):
    invoice_id: str
    rule_code: str
    ruleset_version: str
    level: str
    title: str
    message: str
    evidence: dict


class AuditFindingOut(AuditFindingCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: int
    created_at: datetime


class IcmsStatementCreate(BaseModel):
    site_id: str
    start_month: date
    end_month: date
    storage_bucket: str
    storage_key: str
    format: str
    summary_json: dict


class IcmsStatementOut(IcmsStatementCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: int
    generated_at: datetime
    created_at: datetime


class RulesetCreate(BaseModel):
    name: str
    version: str
    description: str | None = None
    is_active: bool = True


class RulesetOut(RulesetCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: int
    created_at: datetime


class RuleCreate(BaseModel):
    ruleset_id: str
    code: str
    title: str
    severity_default: str
    condition_json: dict
    actions_json: dict


class RuleOut(RuleCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: int
    created_at: datetime
