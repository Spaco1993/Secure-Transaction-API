import logging
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
from app import database, models, schemas, auth

# Create tables
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Secure Transactions API", version="1.0.0")

# CORS (lock this down per environment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],  # set allowed origins explicitly in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    # Bootstrap: first ever user becomes admin
    user_count = db.query(models.User).count()
    role = "admin" if user_count == 0 else "user"
    db_user = models.User(
        email=user.email,
        hashed_password=auth.get_password_hash(user.password),
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    token = auth.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# ---------------- Transactions CRUD ----------------
@app.post("/transactions", response_model=schemas.TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(database.get_db), user: models.User = Depends(auth.get_current_user)):
    db_tx = models.Transaction(
        amount=tx.amount,
        currency=tx.currency,
        description=tx.description,
        owner_id=user.id,
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

@app.get("/transactions", response_model=List[schemas.TransactionOut])
def list_transactions(db: Session = Depends(database.get_db), user: models.User = Depends(auth.get_current_user)):
    q = db.query(models.Transaction)
    if user.role != "admin":
        q = q.filter(models.Transaction.owner_id == user.id)
    return q.order_by(models.Transaction.created_at.desc()).all()

@app.get("/transactions/{tx_id}", response_model=schemas.TransactionOut)
def get_transaction(tx_id: int, db: Session = Depends(database.get_db), user: models.User = Depends(auth.get_current_user)):
    tx = db.query(models.Transaction).filter(models.Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if user.role != "admin" and tx.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted")
    return tx

@app.put("/transactions/{tx_id}", response_model=schemas.TransactionOut)
def update_transaction(tx_id: int, payload: schemas.TransactionUpdate, db: Session = Depends(database.get_db), user: models.User = Depends(auth.get_current_user)):
    tx = db.query(models.Transaction).filter(models.Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if user.role != "admin" and tx.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted")
    if payload.amount is not None:
        tx.amount = payload.amount
    if payload.currency is not None:
        tx.currency = payload.currency
    if payload.description is not None:
        tx.description = payload.description
    db.commit()
    db.refresh(tx)
    return tx

@app.delete("/transactions/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(tx_id: int, db: Session = Depends(database.get_db), user: models.User = Depends(auth.get_current_user)):
    tx = db.query(models.Transaction).filter(models.Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if user.role != "admin" and tx.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted")
    db.delete(tx)
    db.commit()
    return None

# --------------- Error handling & logging ---------------
logger = logging.getLogger("uvicorn.error")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})
