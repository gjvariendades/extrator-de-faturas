from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_role, tenant_guard
from app.models import User
from app.schemas import LoginRequest, Token, UserOut
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
    _: User = Depends(require_role("admin", "analista")),
    db: Session = Depends(get_db),
) -> list[User]:
    return db.query(User).all()
