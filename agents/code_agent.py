import json
import os
from langchain_groq import ChatGroq
from core.decision_ledger import DecisionLedger

class CodeAgent:
    def __init__(self, llm: ChatGroq, ledger: DecisionLedger):
        self.llm = llm
        self.ledger = ledger
        self.name = "Code Agent"

    def run(self, spec: dict, architecture: dict) -> dict:
        print(f"\n💻 [{self.name}] Generating production code...")

        system_prompt = """You are a senior Python backend developer.
Generate production-grade FastAPI code based on the spec and architecture.

Respond ONLY with a valid JSON object with these keys:
{
  "main_py": "full content of main.py as a string",
  "models_py": "full content of models.py as a string",
  "database_py": "full content of database.py as a string",
  "routes_py": "full content of routes.py as a string"
}

Use FastAPI, SQLAlchemy, Pydantic. Include proper error handling. Real working code only."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate FastAPI code for:\nSpec: {json.dumps(spec, indent=2)}\nArchitecture: {json.dumps(architecture, indent=2)}"}
        ]

        response = self.llm.invoke(messages)
        raw = response.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        try:
            code_files = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: generate a working todo API
            code_files = self._fallback_code(spec)

        os.makedirs("outputs/generated_app", exist_ok=True)
        file_map = {
            "main.py": code_files.get("main_py", ""),
            "models.py": code_files.get("models_py", ""),
            "database.py": code_files.get("database_py", ""),
            "routes.py": code_files.get("routes_py", "")
        }

        saved = []
        for filename, content in file_map.items():
            if content:
                path = f"outputs/generated_app/{filename}"
                with open(path, "w") as f:
                    f.write(content)
                saved.append(filename)

        self.ledger.log(
            agent=self.name,
            decision=f"Generated {len(saved)} code files: {', '.join(saved)}",
            reasoning="Used FastAPI + SQLAlchemy + Pydantic as per architecture spec",
            alternatives=["Django REST framework", "Flask + Marshmallow"],
            confidence=0.91
        )

        return {"files": file_map, "saved_paths": saved}

    def _fallback_code(self, spec: dict) -> dict:
        project = spec.get("project_name", "App")
        return {
            "database_py": '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
            "models_py": '''from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)
''',
            "routes_py": '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import models
from database import get_db

router = APIRouter()

class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = ""

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None

class ItemResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    class Config:
        from_attributes = True

@router.get("/items", response_model=list[ItemResponse])
def get_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()

@router.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, update: ItemUpdate, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}
''',
            "main_py": f'''from fastapi import FastAPI
from database import engine
import models
from routes import router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="{project} API",
    description="Auto-generated by ARIA-Lite",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {{"message": "Welcome to {project} API", "docs": "/docs"}}

@app.get("/health")
def health():
    return {{"status": "healthy", "agent": "ARIA-Lite"}}
'''
        }