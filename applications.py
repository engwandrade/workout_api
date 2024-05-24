from fastapi import FastAPI, Query, HTTPException, Path
from pydantic import BaseModel
from typing import List, Optional
from fastapi_pagination import Page, add_pagination, paginate
from uuid import UUID, uuid4

app = FastAPI()

class Atleta(BaseModel):
    id: Optional[UUID] = uuid4()
    nome: str
    cpf: str
    centro_treinamento: str
    categoria: str

class AtletaUpdate(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    centro_treinamento: Optional[str] = None
    categoria: Optional[str] = None

atletas_db = [
    {"id": uuid4(), "nome": "João", "cpf": "123.456.789-00", "centro_treinamento": "Centro A", "categoria": "Profissional"},
    {"id": uuid4(), "nome": "Maria", "cpf": "987.654.321-00", "centro_treinamento": "Centro B", "categoria": "Amador"}
]

@app.get("/atletas", response_model=List[Atleta])
def get_all_atletas():
    return atletas_db

@app.get("/atletas/{atleta_id}", response_model=Atleta)
def get_atleta(atleta_id: UUID = Path(...)):
    atleta = next((atleta for atleta in atletas_db if atleta["id"] == atleta_id), None)
    if atleta is None:
        raise HTTPException(status_code=404, detail="Atleta not found")
    return atleta

@app.get("/atletas/query")
def read_atletas(nome: str = Query(None), cpf: str = Query(None)):
    results = [atleta for atleta in atletas_db if (nome in atleta["nome"] if nome else True) and (cpf in atleta["cpf"] if cpf else True)]
    return results

@app.post("/atletas")
def create_atleta(atleta: Atleta):
    for existing_atleta in atletas_db:
        if existing_atleta["cpf"] == atleta.cpf:
            raise HTTPException(status_code=400, detail=f"Já existe um atleta cadastrado com o cpf: {atleta.cpf}")
    atleta.id = uuid4()
    atletas_db.append(atleta.dict())
    return atleta

@app.patch("/atletas/{atleta_id}", response_model=Atleta)
def update_atleta(atleta_id: UUID, atleta_update: AtletaUpdate):
    atleta = next((atleta for atleta in atletas_db if atleta["id"] == atleta_id), None)
    if atleta is None:
        raise HTTPException(status_code=404, detail="Atleta not found")
    update_data = atleta_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        atleta[key] = value
    return atleta

@app.get("/atletas_pag", response_model=Page[Atleta])
def read_atletas_pag():
    return paginate(atletas_db)

add_pagination(app)
