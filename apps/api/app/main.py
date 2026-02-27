from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, require_role, tenant_guard
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
    User,
)
from app.schemas import (
    AuditFindingCreate,
    AuditFindingOut,
    CustomerCreate,
    CustomerOut,
    IcmsStatementCreate,
    IcmsStatementOut,
    InvoiceCreate,
    InvoiceExtractionCreate,
    InvoiceExtractionOut,
    InvoiceFileCreate,
    InvoiceFileOut,
    InvoiceLineItemCreate,
    InvoiceLineItemOut,
    InvoiceOut,
    InvoiceTaxCreate,
    InvoiceTaxOut,
    LoginRequest,
    RuleCreate,
    RuleOut,
    RulesetCreate,
    RulesetOut,
    SiteCreate,
    SiteOut,
    Token,
    UserOut,
)
from app.security import create_access_token, verify_password

app = FastAPI(title="Extrator API")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return Token(access_token=create_access_token(user.email))


@app.get("/me", response_model=UserOut)
def me(current_user: User = Depends(tenant_guard)) -> User:
    return current_user


@app.get("/admin/users", response_model=list[UserOut])
def list_users(
    current_user: User = Depends(require_role("admin", "analista")),
    db: Session = Depends(get_db),
) -> list[User]:
    return db.query(User).filter(User.tenant_id == current_user.tenant_id).all()


def create_for_tenant(model_cls, payload, tenant_id: int, db: Session):
    item = model_cls(tenant_id=tenant_id, **payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Violação de constraint/relacionamento") from exc
    db.refresh(item)
    return item


@app.post("/customers", response_model=CustomerOut)
def create_customer(payload: CustomerCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_for_tenant(Customer, payload, current_user.tenant_id, db)


@app.get("/customers", response_model=list[CustomerOut])
def list_customers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Customer).filter(Customer.tenant_id == current_user.tenant_id).all()


@app.post("/sites", response_model=SiteOut)
def create_site(payload: SiteCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_for_tenant(Site, payload, current_user.tenant_id, db)


@app.get("/sites", response_model=list[SiteOut])
def list_sites(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Site).filter(Site.tenant_id == current_user.tenant_id).all()


@app.post("/invoices", response_model=InvoiceOut)
def create_invoice(payload: InvoiceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_for_tenant(Invoice, payload, current_user.tenant_id, db)


@app.get("/invoices", response_model=list[InvoiceOut])
def list_invoices(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Invoice).filter(Invoice.tenant_id == current_user.tenant_id).all()


@app.post("/invoice-files", response_model=InvoiceFileOut)
def create_invoice_file(
    payload: InvoiceFileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return create_for_tenant(InvoiceFile, payload, current_user.tenant_id, db)


@app.get("/invoice-files", response_model=list[InvoiceFileOut])
def list_invoice_files(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(InvoiceFile).filter(InvoiceFile.tenant_id == current_user.tenant_id).all()


@app.post("/invoice-extractions", response_model=InvoiceExtractionOut)
def create_invoice_extraction(
    payload: InvoiceExtractionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_for_tenant(InvoiceExtraction, payload, current_user.tenant_id, db)


@app.get("/invoice-extractions", response_model=list[InvoiceExtractionOut])
def list_invoice_extractions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(InvoiceExtraction).filter(InvoiceExtraction.tenant_id == current_user.tenant_id).all()


@app.post("/invoice-line-items", response_model=InvoiceLineItemOut)
def create_invoice_line_item(
    payload: InvoiceLineItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_for_tenant(InvoiceLineItem, payload, current_user.tenant_id, db)


@app.get("/invoice-line-items", response_model=list[InvoiceLineItemOut])
def list_invoice_line_items(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(InvoiceLineItem).filter(InvoiceLineItem.tenant_id == current_user.tenant_id).all()


@app.post("/invoice-taxes", response_model=InvoiceTaxOut)
def create_invoice_tax(
    payload: InvoiceTaxCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return create_for_tenant(InvoiceTax, payload, current_user.tenant_id, db)


@app.get("/invoice-taxes", response_model=list[InvoiceTaxOut])
def list_invoice_taxes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(InvoiceTax).filter(InvoiceTax.tenant_id == current_user.tenant_id).all()


@app.post("/audit-findings", response_model=AuditFindingOut)
def create_audit_finding(
    payload: AuditFindingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return create_for_tenant(AuditFinding, payload, current_user.tenant_id, db)


@app.get("/audit-findings", response_model=list[AuditFindingOut])
def list_audit_findings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(AuditFinding).filter(AuditFinding.tenant_id == current_user.tenant_id).all()


@app.post("/icms-statements", response_model=IcmsStatementOut)
def create_icms_statement(
    payload: IcmsStatementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_for_tenant(IcmsStatement, payload, current_user.tenant_id, db)


@app.get("/icms-statements", response_model=list[IcmsStatementOut])
def list_icms_statements(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(IcmsStatement).filter(IcmsStatement.tenant_id == current_user.tenant_id).all()


@app.post("/rulesets", response_model=RulesetOut)
def create_ruleset(payload: RulesetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_for_tenant(Ruleset, payload, current_user.tenant_id, db)


@app.get("/rulesets", response_model=list[RulesetOut])
def list_rulesets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Ruleset).filter(Ruleset.tenant_id == current_user.tenant_id).all()


@app.post("/rules", response_model=RuleOut)
def create_rule(payload: RuleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_for_tenant(Rule, payload, current_user.tenant_id, db)


@app.get("/rules", response_model=list[RuleOut])
def list_rules(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Rule).filter(Rule.tenant_id == current_user.tenant_id).all()
