from sqlalchemy import Column, Integer, String, Date
from database import Base

class Participante(Base):
    __tablename__ = "participantes"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String)
    data_nascimento = Column(Date)
    sexo = Column(String)
    email = Column(String)
    celular = Column(String)
