# Importações principais
from fastapi import FastAPI, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from datetime import date
import requests

# Conexão com o banco e modelos
from database import SessionLocal, engine
from models import Participante, Base

# Cria a aplicação
app = FastAPI()

# Cria as tabelas no banco (caso ainda não existam)
Base.metadata.create_all(bind=engine)

# Modelo de entrada para atualização de data de nascimento
class AtualizaNascimento(BaseModel):
    nova_data: str  # Formato esperado: YYYY-MM-DD

# Dependência para obter sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint: Upload de arquivo Excel e inserção no banco
@app.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.xlsx'):
        return {"erro": "Por favor, envie um arquivo .xlsx"}

    conteudo = await file.read()
    df = pd.read_excel(conteudo)

    for _, row in df.iterrows():
        participante = Participante(
            nome_completo=row["Nome completo"],
            data_nascimento=pd.to_datetime(row["Data de Nascimento"]).date(),
            sexo=row["Sexo"],
            email=row["E-mail"],
            celular=str(row["Celular"]) if not pd.isna(row.get("Celular", "")) else ""
        )
        db.add(participante)

    db.commit()
    return {"mensagem": "Dados inseridos com sucesso no banco de dados"}

# Endpoint: Listar participantes (com filtro opcional por sexo)
@app.get("/participantes/")
def listar_participantes(sexo: Optional[str] = Query(None), db: Session = Depends(get_db)):
    if sexo:
        participantes = db.query(Participante).filter(Participante.sexo == sexo).all()
    else:
        participantes = db.query(Participante).all()

    return participantes

# Endpoint: Atualizar data de nascimento de um participante
@app.put("/participantes/{id}")
def atualizar_nascimento(id: int, dados: AtualizaNascimento, db: Session = Depends(get_db)):
    participante = db.query(Participante).filter(Participante.id == id).first()

    if not participante:
        return {"erro": "Participante não encontrado"}

    try:
        participante.data_nascimento = pd.to_datetime(dados.nova_data).date()
    except:
        return {"erro": "Formato de data inválido. Use YYYY-MM-DD"}

    db.commit()
    db.refresh(participante)

    return {"mensagem": f"Data de nascimento de {participante.nome_completo} atualizada com sucesso!"}

# Endpoint: Deletar todos os participantes da base
@app.delete("/participantes/")
def deletar_todos(db: Session = Depends(get_db)):
    total = db.query(Participante).delete()
    db.commit()
    return {"mensagem": f"{total} participante(s) foram deletados da base de dados."}

# Endpoint: Webhook que calcula a idade, envia à Wayv e retorna
@app.post("/webhook/")
def receber_webhook(payload: dict):
    data_nascimento = payload.get("data_nascimento")
    form_id = payload.get("form_id")

    # Adicionando template_id e execution_company_id
    template_id = "679a0ab6c8825d82fe8273ff"  # Exemplo do template_id
    execution_company_id = "664274977fc8ba05332d2f0c"  # Exemplo do execution_company_id

    if not data_nascimento or not form_id:
        return {"erro": "Campos obrigatórios: data_nascimento e form_id"}

    try:
        nascimento = pd.to_datetime(data_nascimento).date()
        hoje = date.today()
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
    except:
        return {"erro": "Data de nascimento inválida"}

    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb21wYW55X2lkIjoiNjY0Mjc0OTc3ZmM4YmEwNTMzMmQyZjBjIiwiY3VycmVudF90aW1lIjoxNzMzNDMwMzg3NDcxLCJleHAiOjIwNDg5NjMxODd9.9kdeolnmsr2zRUeZQoOqL_FOppMAqFoC1zJqbo4769M"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload_envio = {
        "form_id": form_id,
        "template_id": template_id,  # Adicionando template_id
        "execution_company_id": execution_company_id,  # Adicionando execution_company_id
        "fields": {
            "idade": idade 
        }
    }

    try:
        response = requests.post("https://app.way-v.com/api/integration/checklists", json=payload_envio, headers=headers)
        if response.status_code == 200:
            return {"form_id": form_id, "idade": idade, "status": "Enviado com sucesso"}
        else:
            return {
                "form_id": form_id,
                "idade": idade,
                "status": "Erro ao enviar",
                "detalhes": response.text
            }
    except Exception as e:
        return {"erro": f"Falha ao tentar enviar dados: {str(e)}"}