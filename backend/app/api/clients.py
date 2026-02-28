from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Client
from ..schemas import Client as ClientSchema, ClientCreate
from typing import List

router = APIRouter()

@router.get("/")
def list_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    return {"code": 0, "data": clients}

@router.post("/")
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return {"code": 0, "data": db_client}

@router.get("/{client_id}")
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="客户不存在")
    return {"code": 0, "data": client}

@router.put("/{client_id}")
def update_client(client_id: int, client: ClientCreate, db: Session = Depends(get_db)):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="客户不存在")
    for key, value in client.model_dump().items():
        setattr(db_client, key, value)
    db.commit()
    db.refresh(db_client)
    return {"code": 0, "data": db_client}

@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if client:
        db.delete(client)
        db.commit()
    return {"code": 0, "message": "删除成功"}
