# fastapi ve javascript kullanarak html sayfasına girilen yeni verinin databasede olup olmadığını kontrol etmek istiyorum
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Annotated
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = 'postgresql://postgres:20022007@localhost:5432/fastapitest2'
engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependency = Annotated[Session, Depends(get_db)]

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String, index=True)
    
Base.metadata.create_all(bind=engine)

class ItemResponse(BaseModel):
    id : int
    name : str



@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html") as f:
        return f.read()

@app.post("/items/")
def create_items(item: ItemResponse):
    db = SessionLocal()
    try:
        db_item = Item(name=item.name,id = item.id)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Veritabani okuma hatasi : "+str(e))
    finally:
        db.close()


@app.get("/items/",response_model=List[ItemResponse])
def read_items(db : db_dependency):
    result = db.query(Item).all()
    if not result:
        raise HTTPException(status_code=404,detail='Question is not found')
    return result

        



